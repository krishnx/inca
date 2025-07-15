import abc
from uuid import UUID


class IAgent(abc.ABC):
    RUN_TIME = 5  # seconds

    def __init__(self, user_id: UUID):
        self.user_id = user_id

    @abc.abstractmethod
    async def run(self) -> str:
        pass
