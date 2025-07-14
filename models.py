from pydantic import BaseModel
from enum import Enum
from uuid import UUID
from typing import Optional
from datetime import datetime


class AgentType(str, Enum):
    DOCUMENT_EXTRACTOR = 'document-extractor'
    POLICY_CHECKER = 'policy-checker'


class AgentRequest(BaseModel):
    agent_type: AgentType
    user_id: UUID


class AgentStatus(BaseModel):
    run_id: UUID
    agent_type: AgentType
    user_id: UUID
    status: str  # e.g. pending, running, completed, failed
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
