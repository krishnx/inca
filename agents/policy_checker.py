import asyncio
import random
from agents.base import IAgent
from logger import logger


class PolicyCheckerAgent(IAgent):
    async def run(self) -> str:
        logger.info(f'Hello, I am a policy-checker agent for {self.user_id}')

        await asyncio.sleep(5)

        result = random.choice(['approved', 'rejected'])

        logger.info(f'policy-checker agent for {self.user_id} complete — {result}')

        return result
