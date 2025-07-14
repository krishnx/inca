# Minimal Python Agent Runner

## Overview
This service simulates insurance agents that perform mock tasks like document extraction and policy checking.

## Features
- Async FastAPI service
- One-agent-at-a-time constraint (using in-memory flag)
- Structured logging
- Error simulation & recovery
- Integration tests
- Config via `.env`

## Scaling and Trade-offs
**Current Constraint:** Only one agent runs at a time (via in-memory flag).

**Reason:** Prevent concurrent execution for simplicity and safety (no race conditions, simplified logs).

**To Scale:**
- Move state tracking to Redis or a DB.
- Use task queues (e.g., Celery, RQ) with concurrency control.
- Enable multiple agent runners behind a job scheduler.

**Trade-offs:**
- Simpler logic, fewer bugs in dev mode.
- Not horizontally scalable yet.
- All state is lost on restart.

## Error Handling
- Handles unknown agent types or runtime exceptions.
- Clear logs and HTTP 4xx/5xx error codes returned.
- Service remains resilient.

## Security
- Secrets/configs loaded via environment variables.
- In production: use Vault or cloud secret managers.

## Testing
Integration tests use `httpx` + `pytest` to simulate:
- Successful run
- Agent busy rejection
- Invalid agent input

## AI Use
AI (ChatGPT) was used to scaffold file structure and refactor the code. All output was reviewed, debugged, and adjusted for clarity and alignment with requirements.
