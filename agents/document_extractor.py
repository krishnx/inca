import asyncio

from logger import logger
from agents.base import IAgent


class DocumentExtractorAgent(IAgent):
    async def run(self) -> str:
        logger.info(f'Hello, I am a document-extractor agent for {self.user_id}')

        await asyncio.sleep(5)

        logger.info(f'document-extractor agent for {self.user_id} complete')

        return 'extracted'
