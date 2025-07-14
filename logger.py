import logging
import sys

logger = logging.getLogger('agent-runner')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/agent_runner.log', mode='a', encoding='utf-8', delay=True)
    ]
)

handler.setFormatter(formatter)
logger.addHandler(handler)


def log_with_extra(msg, level='info', **extra):
    getattr(logger, level)(msg, extra=extra)
