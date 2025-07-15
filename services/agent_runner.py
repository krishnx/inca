import asyncio

from fastapi import HTTPException, BackgroundTasks

from agents.document_extractor import DocumentExtractorAgent
from agents.policy_checker import PolicyCheckerAgent

from uuid import UUID, uuid4

from models.enums import AgentStatus, AgentType
from services.status_store import create_run_status, update_status

AGENT_FACTORY = {
    AgentType.DOCUMENT_EXTRACTOR: DocumentExtractorAgent,
    AgentType.POLICY_CHECKER: PolicyCheckerAgent,
}

running_lock = asyncio.Lock()


async def run_agent(agent_type: AgentType, user_id: UUID, background_tasks: BackgroundTasks) -> UUID:
    """
    Factory function to create an agent instance based on the agent type.

    :param background_tasks:
    :param agent_type: Type of the agent to create.
    :param user_id: User ID associated with the agent.
    :return: An instance of IAgent.
    """
    if agent_type not in AGENT_FACTORY:
        raise HTTPException(status_code=400, detail=f'Unknown agent type: {agent_type}')

    # Try to acquire the lock without waiting
    locked = running_lock.locked()
    if locked:
        # Already running
        raise HTTPException(status_code=409, detail='An agent is already running')

    run_id = uuid4()
    try:
        agent = AGENT_FACTORY[agent_type](user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create initial status record
    create_run_status(run_id, agent_type, user_id)

    # Define the background task
    async def agent_runner():
        async with running_lock:
            try:
                result = await agent.run()
                update_status(run_id, AgentStatus.COMPLETED, result=result)
            except Exception as e:
                update_status(run_id, AgentStatus.FAILED, error=str(e))

    # Schedule the agent runner task in background
    background_tasks.add_task(agent_runner)

    return run_id
