from uuid import UUID
from typing import Dict
from models import AgentStatus, EnumAgentStatus
from datetime import datetime, timezone

status_store: Dict[UUID, AgentStatus] = {}


def create_run_status(run_id, agent_type, user_id):
    status = AgentStatus(
        run_id=run_id,
        agent_type=agent_type,
        user_id=user_id,
        status=EnumAgentStatus.RUNNING,
        started_at=datetime.now(timezone.utc)
    )
    status_store[run_id] = status

    return status


def update_status(run_id, status: str, result=None, error=None):
    record = status_store.get(run_id)
    if record:
        record.status = status
        record.result = result
        record.error = error
        record.completed_at = datetime.now(timezone.utc)
