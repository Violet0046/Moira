from uuid import UUID

from moira.application.ports.run_repository import RunRepository
from moira.domain.narrative import NarrativeRun


class InMemoryRunRepository(RunRepository):
    def __init__(self) -> None:
        self._runs: dict[UUID, NarrativeRun] = {}

    async def save(self, run: NarrativeRun) -> NarrativeRun:
        self._runs[run.run_id] = run
        return run

    async def get(self, run_id: UUID) -> NarrativeRun | None:
        return self._runs.get(run_id)

    async def list_runs(self) -> list[NarrativeRun]:
        return list(self._runs.values())
