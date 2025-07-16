# Agent Runner System

This project provides a simplified execution framework for AI agents using FastAPI, with concurrency control, background task management, and agent status tracking.

## 🚀 Overview

The system allows users to trigger specific agent types (e.g., `DOCUMENT_EXTRACTOR`, `POLICY_CHECKER`) through an API endpoint. Each agent runs asynchronously as a background task and is designed to simulate long-running or resource-intensive operations.

## ⚙️ Setup Instructions (Docker-Based)

### 1. Prerequisites

- Docker: [Install Docker](https://docs.docker.com/get-docker/)

### 2. Clone the Repository

```bash
git clone https://github.com/krishnx/inca.git
cd inca
```

### 3. Start the Application
```bash
make up
```

### 4. Run Tests
```bash
make test
```

### 5. Code Quality Checks
```bash
make lint
```

### 6. Stop the Application
```bash
make down
```

### 7. Rebuild Containers
```bash
make rebuild
```

---

## 📦 Current Design Highlights

- **Agent types**: Modular agent class structure.
- **Concurrency control**: Prevents the same user from running multiple concurrent agents using per-user locking (`asyncio.Lock()`).
- **Status tracking**: Persisted statuses (e.g., `PENDING`, `COMPLETED`, `FAILED`) for each agent run.
- **Timeouts**: Configurable lock and agent run timeouts.
- **Background execution**: Tasks are scheduled in FastAPI’s `BackgroundTasks`.

---

## 🧠 Expanding to Realistic Integrations

To evolve from this simplified simulation to a production-ready system:

1. **Replace dummy agent logic** with:
   - Calls to external services (e.g., document APIs, LLMs, databases).
   - Real data pipelines with authentication and error handling.
2. **Status persistence** should be backed by:
   - A data store like PostgreSQL or Redis, not in-memory dictionaries.
3. **Background task execution** can transition from `BackgroundTasks` to:
   - A distributed task queue like **Celery**, **Kafka**, or **RabbitMQ** for resilience and retries.
4. **Concurrency control** should migrate to:
   - Redis-backed locks (e.g., Redlock) to support multi-instance deployments.

---

## 💡 Why This Approach?

- **Simplicity**: `asyncio.Lock()` with in-memory tracking was chosen to keep the solution minimal and focused on correctness.
- **Clarity**: Avoided external dependencies or complex infrastructure for easier review and reproducibility.
- **Traceability**: Easier to reason about agent lifecycle and test edge cases like timeouts and lock contention.

---

## 📈 Scaling and Relaxing Constraints

In production, we would:

| Constraint            | Scaled Solution                                |
|----------------------|------------------------------------------------|
| `asyncio.Lock()`     | Use Redis or distributed locking (e.g. Redlock). |
| FastAPI BackgroundTasks | Move to Celery/RabbitMQ + worker pool.         |
| In-memory status     | Use persistent DB (PostgreSQL, Redis).  |
| Agent execution      | Implement real agent logic with retries and error handling. |
| User concurrency     | Implement rate limiting and user isolation.  |

---

## ⚖️ Trade-offs: Serial vs Concurrent Execution

| Aspect             | Current Serial Locking         | Concurrent Execution (Future) |
|-------------------|--------------------------------|-------------------------------|
| Simplicity        | ✅ Very easy to implement        | ❌ Requires careful orchestration |
| Debuggability     | ✅ Easier to reason about bugs   | ❌ Harder to trace race conditions |
| Resource Utilization | ❌ Underutilized CPU / I/O        | ✅ Maximized throughput |
| User Experience   | ❌ Slow if queue is long         | ✅ Parallelism improves response |

---

## ✅ Testing Strategy

### Current Tests

- Unit tests for:
  - Successful agent execution
  - Conflict when an agent is already running
  - Invalid agent type handling
  - Background task execution status updates

### Future Testing Enhancements

- **Integration tests**:
  - With a persistent backend (e.g., PostgreSQL)
  - Task queues (e.g., Celery)
- **Load tests**:
  - Simulate multiple concurrent user requests
- **Security tests**:
  - rate-limiting and lock bypass attempts
  - user authentication and authorization checks
- **Chaos testing**:
  - Agent failures, task retries, and service unavailability
- Performance benchmarks:
  - Measure response times under load
  - Evaluate resource utilization (CPU, memory)

---

## 🔐 Security Considerations for Production

- **Authentication & Authorization**:
  - JWT/OAuth2 to validate users and enforce RBAC on agents.
- **Input Validation**:
  - Strict `pydantic` validation for all request payloads.
- **Rate limiting**:
  - Prevent abuse via tools like **FastAPI-Limiter**.
- **Logging & Auditing**:
  - Structured logging with request IDs and secure storage.
- **Secrets management**:
  - Use Vault, AWS Secrets Manager, or env vars securely.
- **Avoid code injection**:
  - Especially important if agents interact with LLMs or user data.

---

## 🤖 Use of AI Assistance

AI (ChatGPT-4) was used to:

- The initial code generation for the agent runner system
- Suggest patterns for timeout handling and lock management
- logging setup
- Generate this `README.md` outline based on project context
- Terraform code

---

## 🧹 Code Review Process

- **Correctness**:
  - Manual validation of `asyncio` behavior (e.g., lock acquisition and release)
  - Logging and error paths explicitly tested
- **Performance**:
  - Reviewed agent blocking behavior and timing logic
- **Code style**:
  - Refactored AI-suggested code for readability and consistency
- Flake8 checks were run to ensure PEP 8 compliance.

---

## API Usage Examples

### Trigger an Agent Run

Send a POST request to start an agent run. Only one agent can run at a time. If another is running, you'll get an error.

```bash
curl -X POST "http://localhost:8000/agents/run" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "agent_type": "document-extractor",
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  }'
```

#### Response example on success:

```json
{
  "run_id": "8a1f4dca-7a6e-4f45-9a7b-9c1126dcae74",
  "status": "running"
}
```

#### Response example if another agent is already running:

```json
{
  "detail": "An agent is already running"
}
```

#### HTTP status code:** `409 Conflict`

---

### Query Agent Run Status

Use the `run_id` from the trigger response to query the current status and result.

```bash
curl -X 'GET' \
  'http://localhost:8000/agents/status/7b4c830d-f75a-42b0-bf90-68f4cd6f42d7' \
  -H 'accept: application/json'
```

#### Response example while running:

```json
{
  "run_id": "7b4c830d-f75a-42b0-bf90-68f4cd6f42d7",
  "agent_type": "document-extractor",
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "running",
  "result": null,
  "error": null,
  "started_at": "2025-07-15T19:37:02.975197Z",
  "completed_at": "2025-07-15T19:37:07.985241Z"
}
```

#### Response example after completion:

```json
{
  "run_id": "7b4c830d-f75a-42b0-bf90-68f4cd6f42d7",
  "agent_type": "document-extractor",
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "completed",
  "result": "extracted",
  "error": null,
  "started_at": "2025-07-15T19:37:02.975197Z",
  "completed_at": "2025-07-15T19:37:07.985241Z"
}
```

#### Response example if run\_id is not found:

```json
{
  "detail": "Run ID: 7b4c830d-f75a-42b0-bf90-68f4cd6f42d9 not found"
}
```

#### HTTP status code:** `404 Not Found

## Terraform 
### Usage
To deploy the FastAPI application using Terraform, you can use the provided `main.tf` file. This file sets up an AWS EC2 instance with the necessary configurations to run the FastAPI app.
### Prerequisites
- Ensure you have Terraform installed on your machine.
- Configure your AWS credentials using the AWS CLI or by setting environment variables.
- Make sure you have an SSH key pair created in AWS for accessing the EC2 instance.
- Ensure you have the necessary IAM permissions to create EC2 instances, security groups, and other resources.

### Steps to Deploy
```
cd ./infra
terraform init
terraform apply
```