from agents.base import IAgent
from agents.document import DocumentExtractorAgent
from agents.policy import PolicyCheckerAgent

from uuid import UUID


def get_agent(agent_type: str, user_id: UUID) -> IAgent:
    if agent_type == 'document-extractor':
        return DocumentExtractorAgent(user_id)
    elif agent_type == 'policy-checker':
        return PolicyCheckerAgent(user_id)
    else:
        raise ValueError(f'Unknown agent type: {agent_type}')
