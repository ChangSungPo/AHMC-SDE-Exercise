from fastapi import APIRouter, HTTPException, Path, status
from typing import List
from src.services.revision_service import revision_service
from src.schemas.api_schemas import (
    AnalyzeCaseRequest,
    SaveRevisionRequest,
    UpdateCaseRequest,
    CaseSummaryResponse,
    CaseDetailResponse,
)
from src.agents.schemas import FinalAssessmentSchema

router = APIRouter(prefix="/api/revisions", tags=["Cases revisions Controller"])


@router.post(
    "/analyze",
    response_model=FinalAssessmentSchema,
    summary="Analyze raw not by Multi-Agent Clinical Pipeline",
)
async def analyze_new_case(payload: AnalyzeCaseRequest):
    print(f"Received payload for analysis. Note size: {len(payload.raw_note)}.")

    return revision_service.analyze(payload.raw_note)


@router.post(
    "/save",
    response_model=CaseDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save structed note to DB",
)
def save_new_case(payload: SaveRevisionRequest):
    return revision_service.create(
        raw_note=payload.raw_note,
        machine_output=payload.machine_output,
        user_output=payload.user_output
    )


@router.get("", response_model=List[CaseSummaryResponse], summary="List all review cases from DB")
async def list_all_cases():
    return revision_service.get_summary_list()


@router.get("/{case_id}", response_model=CaseDetailResponse, summary="Get case details by case ID")
async def get_case_by_id(
    case_id: str = Path(..., description="The 24-character hexadecimal MongoDB ObjectId string.")
):
    result = revision_service.get_detail_by_id(case_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Revision file with ID {case_id} could not be located.",
        )
    return result


@router.put(
    "/{case_id}",
    response_model=CaseDetailResponse,
    summary="Save edited outputs and revised HPI narratives",
)
async def save_user_edits(
    payload: UpdateCaseRequest,
    case_id: str = Path(..., description="The 24-character hexadecimal MongoDB ObjectId string."),
):
    print(f"[API] Saving manual adjustments for case ID: {case_id}")

    result = revision_service.save_human_edits(case_id, payload.user_output)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target revision record missing. Commit aborted for ID {case_id}.",
        )

    return result
