from abc import ABC, abstractmethod
from uuid import UUID

from moira.domain.narrative import NarrativeRun


class RunRepository(ABC):
    @abstractmethod
    async def save(self, run: NarrativeRun) -> NarrativeRun:
        raise NotImplementedError

    @abstractmethod
    async def get(self, run_id: UUID) -> NarrativeRun | None:
        raise NotImplementedError

    @abstractmethod
    async def list_runs(self) -> list[NarrativeRun]:
        raise NotImplementedError
