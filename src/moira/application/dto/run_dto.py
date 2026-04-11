from uuid import UUID

from pydantic import BaseModel, Field

from moira.domain.narrative import AgentRole, NarrativeRun, WorldState


class CharacterSeed(BaseModel):
    name: str
    role: AgentRole
    goal: str | None = None
    traits: list[str] = Field(default_factory=list)


class CreateRunRequest(BaseModel):
    title: str
    location: str
    time_label: str
    weather: str | None = None
    protagonist_name: str
    protagonist_goal: str | None = None
    protagonist_traits: list[str] = Field(default_factory=list)


class CreateRunResponse(BaseModel):
    run: NarrativeRun


class GetRunResponse(BaseModel):
    run: NarrativeRun


class RunSummary(BaseModel):
    run_id: UUID
    title: str
    status: str
    location: str


def build_initial_world_state(request: CreateRunRequest) -> WorldState:
    return WorldState(
        location=request.location,
        time_label=request.time_label,
        weather=request.weather,
    )
