import asyncio

import pytest
from uuid import UUID, uuid4
from fastapi import BackgroundTasks, HTTPException

from services import agent_runner
from models.enums import AgentType, AgentStatus, LockKey
from services.agent_runner import running_locks


class MockAgent:
    def __init__(self, user_id):
        self.user_id = user_id

    async def run(self):
        return 'mock result'


@pytest.mark.asyncio
async def test_run_agent_success(monkeypatch):
    run_id_holder = {}

    monkeypatch.setattr(agent_runner, 'create_run_status', lambda rid, a, u: run_id_holder.update({'run_id': rid}))
    monkeypatch.setattr(agent_runner, 'update_status', lambda rid, status, result=None, error=None: None)
    monkeypatch.setitem(agent_runner.AGENT_FACTORY, AgentType.DOCUMENT_EXTRACTOR, MockAgent)

    background_tasks = BackgroundTasks()
    user_id = uuid4()

    run_id = await agent_runner.run_agent(AgentType.DOCUMENT_EXTRACTOR, user_id, background_tasks)

    assert isinstance(run_id, UUID)
    assert run_id_holder['run_id'] == run_id
    assert len(background_tasks.tasks) == 1


@pytest.mark.asyncio
async def test_run_agent_invalid_type():
    background_tasks = BackgroundTasks()
    user_id = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        await agent_runner.run_agent('INVALID_TYPE', user_id, background_tasks)  # type: ignore

    assert exc_info.value.status_code == 400
    assert 'Unknown agent type' in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_run_agent_already_running(monkeypatch):
    background_tasks = BackgroundTasks()
    user_id = uuid4()
    agent_type = AgentType.DOCUMENT_EXTRACTOR
    lock_key = LockKey(user_id=user_id, agent_type=agent_type)

    # Create and acquire the lock manually
    lock = asyncio.Lock()
    await lock.acquire()
    running_locks[lock_key] = lock

    try:
        with pytest.raises(HTTPException) as exc_info:
            await agent_runner.run_agent(agent_type, user_id, background_tasks)

        assert exc_info.value.status_code == 409
        assert 'already running' in str(exc_info.value.detail)
    finally:
        # Ensure the lock is released and cleaned up
        if lock.locked():
            lock.release()
        running_locks.pop(lock_key, None)


@pytest.mark.asyncio
async def test_run_agent_instantiation_error(monkeypatch):
    class FailingAgent:
        def __init__(self, user_id):
            raise ValueError('Invalid user_id')

    monkeypatch.setitem(agent_runner.AGENT_FACTORY, AgentType.DOCUMENT_EXTRACTOR, FailingAgent)
    background_tasks = BackgroundTasks()

    with pytest.raises(HTTPException) as exc_info:
        await agent_runner.run_agent(AgentType.DOCUMENT_EXTRACTOR, uuid4(), background_tasks)

    assert exc_info.value.status_code == 400
    assert 'Invalid user_id' in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_agent_runner_failure(monkeypatch):
    class FailingAgent:
        def __init__(self, user_id):
            self.user_id = user_id

        async def run(self):
            raise RuntimeError('Something went wrong')

    monkeypatch.setitem(agent_runner.AGENT_FACTORY, AgentType.DOCUMENT_EXTRACTOR, FailingAgent)

    called = {'status': None, 'error': None}

    def mock_create_run_status(run_id, agent_type, user_id):  # noqa: F841
        pass

    def mock_update_status(run_id, status, result=None, error=None):  # noqa: F841
        called['status'] = status
        called['error'] = error

    monkeypatch.setattr(agent_runner, 'create_run_status', mock_create_run_status)
    monkeypatch.setattr(agent_runner, 'update_status', mock_update_status)

    background_tasks = BackgroundTasks()
    run_id = await agent_runner.run_agent(AgentType.DOCUMENT_EXTRACTOR, uuid4(), background_tasks)

    # Manually run the background task
    await background_tasks.tasks[0]()

    assert called['status'] == AgentStatus.FAILED
    assert 'Something went wrong' in called['error']
