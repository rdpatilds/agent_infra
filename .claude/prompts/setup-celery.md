Using Celery official docs (https://docs.celeryq.dev/en/stable/) and best practices, set up Celery with Redis for async task processing.

Reference best practices:
- https://denibertovic.com/posts/celery-best-practices/
- https://docs.celeryq.dev/en/stable/userguide/tasks.html

Install dependencies:
```bash
uv add celery flower
```

Create these files:

1. `app/core/celery.py` with:
   - Factory function `create_celery_app()` that returns configured Celery instance
   - Use Redis as broker and backend from settings.redis_url
   - Config: `task_acks_late=True`, `task_reject_on_worker_lost=True`, `result_expires=3600`
   - Task autodiscovery pattern for `app.*.tasks` modules

2. `app/core/celery_utils.py` with:
   - Helper to get current celery app instance
   - Type hints for celery tasks

3. UPDATE `app/core/config.py`:
   - Add celery_broker_url and celery_result_backend (both default to redis_url)
   - Add celery_task_always_eager for testing (default False)

4. `app/example/tasks.py` (example task module):
   - Example task: `send_email(to: str, subject: str, body: str)`
   - Use proper logging, retries with exponential backoff
   - Task should be idempotent, demonstrate best practices

5. `app/example/routes.py` (example endpoint):
   - POST endpoint to trigger async task
   - Returns task_id for tracking
   - GET endpoint to check task status by task_id

6. UPDATE `app/main.py`:
   - Import and initialize celery app in lifespan
   - Log celery initialization

7. UPDATE `docker-compose.yml`:
   - Add celery worker service (use same app image, different command)
   - Add flower service on port 5555
   - Both depend on redis and app services

8. `app/core/tests/test_celery.py`:
   - Test celery app creation
   - Test task registration
   - Use task_always_eager for sync execution

Test requirements:

Unit tests (with task_always_eager=True):
- Test celery config loads correctly
- Test example task executes synchronously
- Expected: 3+ tests passing

Manual E2E:
- Start all services: `docker compose up`
- Trigger task via POST endpoint
- Check Flower UI at http://localhost:5555
- Verify task completion
- Expected: Task appears in Flower, completes successfully

All linting (ruff check ., mypy app/, pyright app/) must pass with strict type hints.

When tests pass and linting is clean, ready to commit.

Output format:
Summary: [what was accomplished]
Files created: [list]
Files modified: [list]
Services added: [celery worker, flower]
Next steps: [how to use celery in other features]
