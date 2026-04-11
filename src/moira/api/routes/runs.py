from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from moira.api.dependencies import get_run_service
from moira.application.dto.run_dto import (
    CreateRunRequest,
    CreateRunResponse,
    GetRunResponse,
    RunSummary,
)
from moira.application.services.run_service import RunService

router = APIRouter(prefix="/runs")


@router.post("", response_model=CreateRunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    payload: CreateRunRequest,
    run_service: RunService = Depends(get_run_service),
) -> CreateRunResponse:
    run = await run_service.create_run(payload)
    return CreateRunResponse(run=run)


@router.get("/{run_id}", response_model=GetRunResponse)
async def get_run(
    run_id: UUID,
    run_service: RunService = Depends(get_run_service),
) -> GetRunResponse:
    run = await run_service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return GetRunResponse(run=run)


@router.get("", response_model=list[RunSummary])
async def list_runs(
    run_service: RunService = Depends(get_run_service),
) -> list[RunSummary]:
    runs = await run_service.list_runs()
    return [
        RunSummary(
            run_id=run.run_id,
            title=run.title,
            status=run.status.value,
            location=run.world_state.location,
        )
        for run in runs
    ]
