from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.agents.schemas import FinalAssessmentSchema

class AnalyzeCaseRequest(BaseModel):
    raw_note: str = Field(
        ..., 
        description="The raw clinical note text."
    )

class SaveRevisionRequest(BaseModel):
    raw_note: str = Field(..., description="The original unstructured medical text.")
    machine_output: FinalAssessmentSchema = Field(..., description="The unedited, pure AI generated baseline.")
    user_output: FinalAssessmentSchema = Field(..., description="The final structured result after human modifications.")

class UpdateCaseRequest(BaseModel):
    user_output: FinalAssessmentSchema = Field(
        ..., 
        description="The modified structured data and edited by the user."
    )

class CaseSummaryResponse(BaseModel):
    id: str = Field(..., description="The unique hexadecimal MongoDB ObjectId string.")
    chief_complaint: str = Field(..., description="The primary complaint extracted from the notes.")
    disposition_recommendation: str = Field(..., description="The clinical disposition (Admit, Observe, Discharge).")
    is_edited: bool = Field(..., description="Flags whether a human has overwritten the machine output.")
    created_at: datetime = Field(..., description="Timestamp of when the case was initiated.")

class CaseDetailResponse(BaseModel):
    id: str = Field(..., description="The unique hexadecimal MongoDB ObjectId string.")
    raw_note: str = Field(..., description="The original unmodified EHR chart note.")
    machine_output: FinalAssessmentSchema = Field(
        ..., 
        description="The canonical READ-ONLY compliance report generated initially by the Multi-Agent system."
    )
    user_output: Optional[FinalAssessmentSchema] = Field(
        None, 
        description="The human-edited snapshot. Returns null if the user hasn't modified the report yet."
    )
    is_edited: bool = Field(..., description="True if user_output is populated and distinct from machine_output.")
    created_at: datetime = Field(..., description="Timestamp of initial analysis.")
    updated_at: datetime = Field(..., description="Timestamp of last human modification modification save.")