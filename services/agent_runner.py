import asyncio
import logging
from collections import defaultdict

from fastapi import HTTPException, BackgroundTasks

from agents.document_extractor import DocumentExtractorAgent
from agents.policy_checker import PolicyCheckerAgent

from uuid import UUID, uuid4

from models.enums import AgentStatus, AgentType, LockKey
from services.status_store import create_run_status, update_status

logger = logging.getLogger(__name__)

AGENT_FACTORY = {
    AgentType.DOCUMENT_EXTRACTOR: DocumentExtractorAgent,
    AgentType.POLICY_CHECKER: PolicyCheckerAgent,
}

running_locks = defaultdict(asyncio.Lock)


def _get_lock(lock_key) -> asyncio.Lock | None:
    """
    Only blocks the same user from running the same agent type concurrently.
    Different users/types don't block each other.

    :param lock_key: Tuple[UUID, AgentType] - Unique key for the lock based on user ID and agent type.
    :return: asyncio.Lock - The lock for the given user and agent type.
    """
    running_lock = running_locks[lock_key]
    locked = running_lock.locked()
    if locked:
        # Already running
        raise HTTPException(status_code=409, detail='An agent is already running')

    return running_lock


def _get_agent(agent_type: AgentType, user_id: UUID) -> DocumentExtractorAgent | PolicyCheckerAgent:
    try:
        return AGENT_FACTORY[agent_type](user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def run_agent(agent_type: AgentType, user_id: UUID, background_tasks: BackgroundTasks,
                    lock_timeout: float = 10.0) -> UUID:
    """
    Factory function to create an agent instance based on the agent type.

    :param agent_type: Type of the agent to create.
    :param user_id: User ID associated with the agent.
    :param background_tasks: Background tasks to run the agent in the background.
    :param lock_timeout: Timeout for acquiring the running lock.
    :return: The UUID of the task.
    """
    if agent_type not in AGENT_FACTORY:
        raise HTTPException(status_code=400, detail=f'Unknown agent type: {agent_type}')

    logger.info(f'Running agent of type {agent_type} for user {user_id}, timeout {lock_timeout} seconds.')

    run_id = uuid4()
    lock_key = LockKey(user_id=user_id, agent_type=agent_type)

    agent = _get_agent(lock_key.agent_type, lock_key.user_id)

    running_lock = _get_lock(lock_key)

    # Create initial status record
    create_run_status(run_id, lock_key.agent_type, lock_key.user_id)

    # Define the background task
    async def agent_runner():
        try:
            await asyncio.wait_for(running_lock.acquire(), timeout=lock_timeout)
            logger.debug(f'Acquired lock for {lock_key} with timeout {lock_timeout} seconds')
        except asyncio.TimeoutError:
            logger.error(f'Failed to acquire lock for {lock_key} within {lock_timeout} seconds')
            update_status(run_id, AgentStatus.FAILED, error='Failed to acquire lock')
            return

        try:
            result = await asyncio.wait_for(agent.run(), timeout=lock_timeout)
            update_status(run_id, AgentStatus.COMPLETED, result=result)
            logger.debug(f'Agent run completed successfully for {lock_key} with result: {result}')
        except asyncio.TimeoutError:
            update_status(run_id, AgentStatus.FAILED, error='Agent run timed out')
            logger.error(f'Agent run timed out for {lock_key} after {lock_timeout} seconds')
        except Exception as e:
            update_status(run_id, AgentStatus.FAILED, error=str(e))
            logger.error(f'Agent run failed for {lock_key} with error: {str(e)}')
        finally:
            running_lock.release()
            if not running_lock.locked():
                running_locks.pop(lock_key, None)

    # Schedule the agent runner task in background
    background_tasks.add_task(agent_runner)

    return run_id
