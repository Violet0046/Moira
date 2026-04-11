from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(str, Enum):
    DIRECTOR = "director"
    ACTOR = "actor"
    NPC = "npc"
    CRITIC = "critic"
    MEMORY = "memory"
    WORLD = "world"


class StoryEventType(str, Enum):
    MICRO = "micro"
    DRAMA = "drama"
    INTERVENTION = "intervention"
    JUDGEMENT = "judgement"
    MEMORY = "memory"


class WorldState(BaseModel):
    location: str
    time_label: str
    weather: str | None = None
    tension: float = Field(default=0.0, ge=0.0, le=1.0)


class CharacterState(BaseModel):
    name: str
    role: AgentRole
    goal: str | None = None
    traits: list[str] = Field(default_factory=list)


class SceneState(BaseModel):
    scene_id: UUID = Field(default_factory=uuid4)
    title: str
    objective: str
    status: str = "pending"


class StoryEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    type: StoryEventType
    summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict[str, object] = Field(default_factory=dict)


class NarrativeRun(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    title: str
    status: RunStatus = RunStatus.CREATED
    world_state: WorldState
    cast: list[CharacterState] = Field(default_factory=list)
    active_scene: SceneState | None = None
    events: list[StoryEvent] = Field(default_factory=list)
