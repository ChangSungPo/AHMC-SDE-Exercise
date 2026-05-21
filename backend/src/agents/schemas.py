from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict

class VitalsSchema(BaseModel):
    blood_pressure: Optional[str] = Field(default=None, description="Original BP string, e.g., '105/67'")
    systolic_bp: Optional[int] = Field(default=None, description="Extracted systolic blood pressure number")
    diastolic_bp: Optional[int] = Field(default=None, description="Extracted diastolic blood pressure number")
    heart_rate: Optional[int] = Field(default=None, description="Heart rate in beats per minute (bpm)")
    respiratory_rate: Optional[int] = Field(default=None, description="Respiratory rate (rpm)")
    temperature_f: Optional[float] = Field(default=None, description="Body temperature in Fahrenheit")
    spo2: Optional[int] = Field(default=None, description="Oxygen saturation percentage (%)")

class LabsSchema(BaseModel):
    glucose: Optional[int] = Field(default=None, description="Blood glucose level in mg/dL")
    ph: Optional[float] = Field(default=None, description="Blood pH level (arterial or venous)")
    bicarbonate: Optional[int] = Field(default=None, description="Serum bicarbonate / CO2 level in mEq/L")
    lactate: Optional[float] = Field(default=None, description="Lactic acid level in mmol/L")
    other_significant_labs: Optional[Dict[str, str]] = Field(
        default_factory=dict, 
        description="Any other abnormal or highly relevant lab values found in the notes"
    )

class PatientSnapshotSchema(BaseModel):
    age: Optional[int] = Field(None, description="Patient's age")
    gender: Optional[str] = Field(None, description="Patient's gender, e.g., 'male', 'female'")
    chief_complaint: str = Field(..., description="The primary chief complaint of the visit")
    history_of_present_illness: str = Field(..., description="A concise chronological narrative summary of the present illness timeline. Must be clear, dense, and strictly under 300 words. Do not repeat text or enter infinite generation loops.")
    past_medical_history: List[str] = Field(default_factory=list, description="List of established chronic conditions")
    current_medications: List[str] = Field(default_factory=list, description="Medications the patient is taking, especially high-risk or relevant ones (e.g., Jardiance, Metformin)")
    key_clinical_findings: List[str] = Field(default_factory=list, description="Key symptoms and physical exam findings, e.g., lethargic, persistent vomiting, deep breaths")
    vitals: VitalsSchema = Field(..., description="Extracted structured vital signs")
    labs: LabsSchema = Field(..., description="Extracted structured laboratory results")
    
class QueryGenerationSchema(BaseModel):
    search_queries: List[str] = Field(
        ..., 
        description="A list of 2 to 3 distinct, highly targeted semantic search strings optimized for clinical guideline retrieval (e.g., 'Diabetic Ketoacidosis inpatient admission criteria')."
    )
    clinical_rationale: str = Field(
        ..., 
        description="Brief medical justification explaining why these specific search strings were formulated based on the patient's critical findings."
    )

class DocumentRelevanceSchema(BaseModel):
    chunk_id: str = Field(..., description="The unique identification code of the evaluated MCG chunk.")
    is_applicable: bool = Field(..., description="Set to True if the medical logic inside this chunk directly applies to the patient's active diagnosis and age/gender group.")
    relevance_score: float = Field(..., description="Confidence score ranging from 0.0 (completely irrelevant) to 1.0 (perfect clinical match).")
    audit_justification: str = Field(..., description="Granular clinical reasoning explaining why this chunk aligns or mismatches with the patient's presentation.")
    missing_required_metrics: List[str] = Field(
        default_factory=list, 
        description="Specific objective metrics (e.g., 'Anion gap value', 'Arterial blood gas test') that this guideline mandates for decision-making but are completely missing or vague in the current chart notes."
    )

class ClinicalAuditReportSchema(BaseModel):
    evaluations: List[DocumentRelevanceSchema] = Field(..., description="Individual medical auditing results for each candidate document.")
    uncertainties_or_missing_info: str = Field(
        ..., 
        description="A synthesized narrative summary of all clinical missing links, missing laboratory measurements, or ambiguous tracking data across the matched guidelines. This maps directly to the required compliance output. If no gaps exist, explicitly write 'None'."
    )
    
class FinalAssessmentSchema(BaseModel):
    chief_complaint: str = Field(
        ..., 
        description="The validated primary reason for the patient's emergency department visit."
    )
    hpi_summary: str = Field(
        ..., 
        description="A concise chronological medical summary of the events leading up to the evaluation."
    )
    key_findings: List[str] = Field(
        ..., 
        description="A list of critical objective metrics, abnormal lab values, and significant clinical observations."
    )
    suspected_conditions: List[str] = Field(
        ..., 
        description="Differential diagnoses or confirmed acute medical conditions identified during this visit."
    )
    disposition_recommendation: Literal["Admit", "Observe", "Discharge", "Unknown"] = Field(
        ..., 
        description="The strict legal medical necessity determination based on MCG criteria alignment."
    )
    uncertainties_or_missing_info: str = Field(
        ..., 
        description="Inherited narrative tracking missing charts, metrics, or clinical gaps. Pass 'None' if completely clear."
    )
    revised_hpi: str = Field(
        ..., 
        description="A highly strategic, analytical, sentence-by-sentence medical narrative that aligns the patient's acute findings directly with MCG criteria to maximize insurance defense, matching the gold-standard style of Case A."
    )