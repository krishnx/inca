import logging
import os
import sys

logger = logging.getLogger('agent-runner')
handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%SZ',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/agent_runner.log', mode='a', encoding='utf-8', delay=True)
    ]
)

logger.addHandler(handler)
