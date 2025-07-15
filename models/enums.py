from collections import namedtuple
from enum import Enum


class AgentStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    DOCUMENT_EXTRACTOR = 'document-extractor'
    POLICY_CHECKER = 'policy-checker'


LockKey = namedtuple('LockKey', ['user_id', 'agent_type'])
