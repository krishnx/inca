from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

from .enums import AgentType, AgentStatus as EnumAgentStatus


class AgentRequest(BaseModel):
    agent_type: AgentType
    user_id: UUID


class AgentStatus(BaseModel):
    run_id: UUID
    agent_type: AgentType
    user_id: UUID
    status: EnumAgentStatus
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
