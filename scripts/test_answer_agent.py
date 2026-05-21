import os
import sys
from openai import OpenAI
from pathlib import Path

# =====================================================================
# Path Alignment Layer using Pathlib
# =====================================================================
CURRENT_SCRIPT = Path(__file__).resolve()
REPO_ROOT = CURRENT_SCRIPT.parent.parent
BACKEND_SRC = REPO_ROOT / "backend" / "src"
AGENTS_DIR = BACKEND_SRC / "agents"

sys.path.append(str(BACKEND_SRC))
sys.path.append(str(AGENTS_DIR))

from config import settings
from schemas import (
    PatientSnapshotSchema, VitalsSchema, LabsSchema,
    ClinicalAuditReportSchema, DocumentRelevanceSchema
)
from answer_agent import AnswerAgent

# =====================================================================
# Mock Injected Data from upstream pipeline
# =====================================================================
MOCK_SNAPSHOT = PatientSnapshotSchema(
    age=47, gender="male",
    chief_complaint="Diabetes issue",
    history_of_present_illness="47M with history of new onset diabetes, started on Jardiance, presents with persistent vomiting and deep sighing breaths.",
    past_medical_history=["Diabetes Mellitus"],
    current_medications=["Jardiance", "Metformin"],
    key_clinical_findings=["Lethargic", "Kussmaul breathing signs", "Severe nausea"],
    vitals=VitalsSchema(blood_pressure="105/67", heart_rate=98, respiratory_rate=18, spo2=100),
    labs=LabsSchema(glucose=93, ph=7.20, bicarbonate=7, lactate=1.9)
)

MOCK_AUDIT_REPORT = ClinicalAuditReportSchema(
    evaluations=[
        DocumentRelevanceSchema(
            chunk_id="M-130_chunk_004",
            is_applicable=True,
            relevance_score=1.0,
            audit_justification="Patient meets strict inpatient criteria for DKA. Even though glucose is normal (93), the arterial pH is 7.20 (MCG threshold < 7.30) and bicarbonate is 7 (MCG threshold <= 18). Patient also shows altered mental status via lethargy.",
            missing_required_metrics=[]
        )
    ],
    uncertainties_or_missing_info="None. All objective metrics matching M-130 inpatient criteria were fully documented."
)

MOCK_FILTERED_GUIDELINES = [
    {
        "chunk_id": "M-130_chunk_004",
        "metadata": {"header": "Clinical Indications for Admission to Inpatient Care", "section": "Inpatient Admission", "target_disease": "Diabetic Ketoacidosis"},
        "content": (
            "### Clinical Indications for Admission to Inpatient Care\n"
            "* Admission is indicated for 1 or more of the following:\n"
            "  * Diabetic ketoacidosis that requires inpatient management, as indicated by ALL of the following:\n"
            "    * Blood glucose concentration anomaly\n"
            "    * Bicarbonate level of 18 mEq/L or less, or arterial/venous pH less than 7.30\n"
            "    * Hypotension or Altered mental status"
        )
    }
]

# =====================================================================
# Execution Entrypoint
# =====================================================================
def run_answer_agent_test():
    print("=== [Test Startup] Testing AnswerAgent Compilation ===")
    
    openai_client = OpenAI(api_key=settings.openai_api_key)
    
    # Instantiate Answer Agent with gpt-4o for optimal medical prose generation
    agent = AnswerAgent(client=openai_client, model_name="gpt-4o")
    
    try:
        final_output = agent.synthesize_final_report(
            snapshot=MOCK_SNAPSHOT,
            audit_report=MOCK_AUDIT_REPORT,
            filtered_guidelines=MOCK_FILTERED_GUIDELINES
        )
        
        print("\n" + "="*60)
        print("[GRAND FINALE] Final Compliant JSON Report Structure:")
        print("="*60)
        print(final_output.model_dump_json(indent=2))
        print("="*60)
        
        # Diagnostic Assertions
        print("\n[Test Assertions] Final Compliance Verification:")
        assert final_output.disposition_recommendation == "Admit", "Failed to carry over 'Admit' recommendation decision!"
        assert len(final_output.revised_hpi) > 100, "Revised HPI narrative was unacceptably brief or empty."
        
        print("\n[Validation Passed] AnswerAgent successfully orchestrated and composed the production-ready medical defense file!")
        
    except Exception as e:
        print(f"\n[Test Failed] Synthesis Runtime Error: {str(e)}")

if __name__ == "__main__":
    run_answer_agent_test()