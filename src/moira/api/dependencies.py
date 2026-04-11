from moira.application.services.run_service import RunService
from moira.infrastructure.repositories.in_memory_run_repository import InMemoryRunRepository

_run_repository = InMemoryRunRepository()
_run_service = RunService(repository=_run_repository)


def get_run_service() -> RunService:
    return _run_service
