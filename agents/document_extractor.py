import asyncio

from logger import logger
from agents.base import IAgent


class DocumentExtractorAgent(IAgent):
    async def run(self) -> str:
        logger.info(f'Hello, I am a document-extractor agent for {self.user_id}')

        await asyncio.sleep(self.RUN_TIME)

        logger.info(f'document-extractor agent for {self.user_id} complete')

        return 'extracted'
