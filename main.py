import asyncio

from fastapi import FastAPI, HTTPException, BackgroundTasks
from uuid import uuid4, UUID

from models.models import AgentRequest, AgentStatus
from models.enums import AgentStatus as EnumAgentStatus
from services.agent_runner import get_agent
from services.status_store import create_run_status, update_status, status_store

app = FastAPI()


running_lock = asyncio.Lock()


running = False


@app.post('/agents/run')
async def run_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    # Try to acquire the lock without waiting
    locked = running_lock.locked()
    if locked:
        # Already running
        raise HTTPException(status_code=409, detail='An agent is already running')

    run_id = uuid4()
    try:
        agent = get_agent(request.agent_type.value, request.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create initial status record
    create_run_status(run_id, request.agent_type, request.user_id)

    # Define the background task
    async def agent_runner():
        async with running_lock:
            try:
                result = await agent.run()
                update_status(run_id, EnumAgentStatus.COMPLETED, result=result)
            except Exception as e:
                update_status(run_id, EnumAgentStatus.FAILED, error=str(e))

    # Schedule the agent runner task in background
    background_tasks.add_task(agent_runner)

    return {'run_id': run_id, 'status': EnumAgentStatus.RUNNING}


@app.get('/agents/status/{run_id}', response_model=AgentStatus)
def get_status(run_id: UUID):
    status = status_store.get(run_id)
    if not status:
        raise HTTPException(status_code=404, detail='Run ID not found')
    return status
