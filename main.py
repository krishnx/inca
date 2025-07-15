
from fastapi import FastAPI, HTTPException, BackgroundTasks
from uuid import UUID

from models.models import AgentRequest, AgentStatus
from models.enums import AgentStatus as EnumAgentStatus
from services.agent_runner import run_agent
from services.status_store import status_store

app = FastAPI()


@app.post('/agents/run')
async def run(request: AgentRequest, background_tasks: BackgroundTasks):
    run_id = await run_agent(request.agent_type.value, request.user_id, background_tasks)

    return {'run_id': run_id, 'status': EnumAgentStatus.RUNNING}


@app.get('/agents/status/{run_id}', response_model=AgentStatus)
def get_status(run_id: UUID):
    status = status_store.get(run_id)
    if not status:
        raise HTTPException(status_code=404, detail=f'Run ID: {run_id} not found')

    return status
