import pytest
import asyncio
from httpx import AsyncClient
from uuid import UUID
from main import app, running_lock
from services.status_store import status_store


@pytest.fixture(autouse=True)
async def reset_globals():
    # Before each test, ensure the lock is free and status_store is cleared
    # Note: asyncio.Lock has no reset method; if locked, release it safely
    if running_lock.locked():
        running_lock.release()
    status_store.clear()
    yield
    if running_lock.locked():
        running_lock.release()
    status_store.clear()


@pytest.mark.asyncio
async def test_run_agent_returns_running():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await ac.post('/agents/run', json={
            'agent_type': 'document-extractor',
            'user_id': '123e4567-e89b-12d3-a456-426614174000'
        })
        assert response.status_code == 200
        data = response.json()
        assert 'run_id' in data
        assert data['status'] == 'running'

        # Check that the run_id status is 'running' initially
        run_id = data['run_id']
        status = status_store.get(UUID(run_id))
        assert status is not None
        assert status.status in ("running", "completed")


@pytest.mark.asyncio
async def test_run_agent_busy():
    # Acquire the lock manually to simulate busy agent
    await running_lock.acquire()
    try:
        async with AsyncClient(app=app, base_url='http://test') as ac:
            response = await ac.post('/agents/run', json={
                'agent_type': 'policy-checker',
                'user_id': '123e4567-e89b-12d3-a456-426614174000'
            })
        assert response.status_code == 409
        assert response.json()['detail'] == 'An agent is already running'
    finally:
        running_lock.release()


@pytest.mark.asyncio
async def test_run_agent_invalid_type():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/agents/run", json={
            "agent_type": "invalid-agent",
            "user_id": "123e4567-e89b-12d3-a456-426614174000"
        })
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    # Check that error_detail contains the enum validation error
    assert any(
        e.get("loc") == ["body", "agent_type"] and "enum" in e.get("type", "")
        for e in error_detail
    )


@pytest.mark.asyncio
async def test_status_endpoint_progression():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        # Trigger an agent run
        response = await ac.post('/agents/run', json={
            'agent_type': 'document-extractor',
            'user_id': '123e4567-e89b-12d3-a456-426614174000'
        })
        data = response.json()
        run_id = data['run_id']

        # Immediately check status: should be 'running'
        response_status = await ac.get(f'/agents/status/{run_id}')
        assert response_status.status_code == 200
        status_data = response_status.json()
        assert status_data["status"] in ("running", "completed")

        # Wait long enough for background task (5 seconds sleep) + buffer
        await asyncio.sleep(6)

        # Check status again: should be 'completed'
        response_status = await ac.get(f'/agents/status/{run_id}')
        assert response_status.status_code == 200
        status_data = response_status.json()
        assert status_data['status'] == 'completed'
        assert status_data['result'] == 'extracted'


@pytest.mark.asyncio
async def test_get_status_not_found():
    import uuid
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await ac.get(f'/agents/status/{uuid.uuid4()}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Run ID not found'
