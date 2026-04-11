from uuid import UUID

from moira.application.dto.run_dto import (
    CreateRunRequest,
    build_initial_world_state,
)
from moira.application.ports.run_repository import RunRepository
from moira.domain.narrative import AgentRole, CharacterState, NarrativeRun, RunStatus


class RunService:
    def __init__(self, repository: RunRepository):
        self.repository = repository

    async def create_run(self, request: CreateRunRequest) -> NarrativeRun:
        protagonist = CharacterState(
            name=request.protagonist_name,
            role=AgentRole.ACTOR,
            goal=request.protagonist_goal,
            traits=request.protagonist_traits,
        )

        director = CharacterState(
            name="Director",
            role=AgentRole.DIRECTOR,
            goal="Keep narrative tension coherent and escalating.",
            traits=["strategic", "observant"],
        )

        critic = CharacterState(
            name="Critic",
            role=AgentRole.CRITIC,
            goal="Evaluate narrative consistency and emotional payoff.",
            traits=["strict", "reflective"],
        )

        run = NarrativeRun(
            title=request.title,
            status=RunStatus.CREATED,
            world_state=build_initial_world_state(request),
            cast=[protagonist, director, critic],
        )
        return await self.repository.save(run)

    async def get_run(self, run_id: UUID) -> NarrativeRun | None:
        return await self.repository.get(run_id)

    async def list_runs(self) -> list[NarrativeRun]:
        return await self.repository.list_runs()
