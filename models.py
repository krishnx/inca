from pydantic import BaseModel
from enum import Enum
from uuid import UUID
from typing import Optional
from datetime import datetime

from enum import Enum


# region Enum
class EnumAgentStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EnumAgentType(str, Enum):
    DOCUMENT_EXTRACTOR = 'document-extractor'
    POLICY_CHECKER = 'policy-checker'


# endregion Enum


# region Models
class AgentRequest(BaseModel):
    agent_type: EnumAgentType
    user_id: UUID


class AgentStatus(BaseModel):
    run_id: UUID
    agent_type: EnumAgentType
    user_id: UUID
    status: EnumAgentStatus
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# endregion Models
