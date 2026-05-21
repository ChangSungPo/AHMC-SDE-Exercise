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
from schemas import PatientSnapshotSchema, VitalsSchema, LabsSchema
from relevant_document_agent import RelevantDocumentAgent

# =====================================================================
# Mock Input A: Patient Snapshot (DEFLATED - Missing Bicarbonate data on purpose)
# =====================================================================
MOCK_PASSED_SNAPSHOT_MISSING_DATA = PatientSnapshotSchema(
    age=47,
    gender="male",
    chief_complaint= "Severe nausea and vomiting with diabetes concerns",
    history_of_present_illness="Patient presents with constant emesis. Recently prescribed Jardiance.",
    past_medical_history=["Diabetes Mellitus"],
    current_medications=["Jardiance"],
    key_clinical_findings=["Lethargic", "Dry mucous membranes"],
    vitals=VitalsSchema(blood_pressure="105/67", heart_rate=98, respiratory_rate=18),
    labs=LabsSchema(
        glucose=93, 
        ph=7.20, 
        bicarbonate=None, # 🌟 We left this as None to see if the agent catches the gap!
        lactate=1.9, 
        other_significant_labs={}
    )
)

# =====================================================================
# Mock Input B: Array of retrieved documents from QueryAgent
# =====================================================================
MOCK_RETRIEVED_CHUNKS = [
    {
        "chunk_id": "M-130_chunk_004",
        "metadata": {"header": "Clinical Indications for Admission to Inpatient Care", "section": "Inpatient Admission", "target_disease": "Diabetic Ketoacidosis"},
        "content": (
            "### Clinical Indications for Admission to Inpatient Care\n"
            "* Admission is indicated for 1 or more of the following:\n"
            "  * Diabetic ketoacidosis that requires inpatient management, as indicated by ALL of the following:\n"
            "    * Blood glucose concentration anomaly\n"
            "    * Bicarbonate level of 18 mEq/L or less, or arterial/venous pH less than 7.30\n"
            "    * Hypotension or Altered mental status\n\n"
            "==================================================\n"
            "🔍 Stitched Glossary Context\n"
            "==================================================\n"
            "#### 📌 Hypotension\nAdult systolic blood pressure less than 90 mm Hg.\n"
            "#### 📌 Altered mental status\nConfusional state, Lethargy, Obtundation, or Coma."
        )
    },
    {
        "chunk_id": "M-130_chunk_021",
        "metadata": {"header": "Standard Administrative Discharge Checklist", "section": "Discharge Planning", "target_disease": "General Care"},
        "content": (
            "### Standard Administrative Discharge Checklist\n"
            "Ensure the patient has secured a ride home prior to exiting the facility floor.\n"
            "Verify billing address accuracy and file appropriate paperwork to insurance carriers."
        )
    }
]

# =====================================================================
# Execution Entrypoint
# =====================================================================
def run_auditor_test():
    print("=== [Test Startup] Testing RelevantDocumentAgent ===")
    
    # Initialize OpenAI Client
    openai_client = OpenAI(api_key=settings.openai_api_key)
    
    # Instantiate Agent
    agent = RelevantDocumentAgent(client=openai_client, model_name="gpt-4o-mini")
    
    try:
        # Run cross audit
        report = agent.audit_retrieved_documents(
            snapshot=MOCK_PASSED_SNAPSHOT_MISSING_DATA, 
            retrieved_docs=MOCK_RETRIEVED_CHUNKS
        )
        
        print("\n" + "="*60)
        print("🎉 [Success] Guardrail Report Generated Flawlessly:")
        print("="*60)
        print(report.model_dump_json(indent=2))
        print("="*60)
        
        # Diagnostic Assertions (Verifying Engineering Guardrails)
        print("\n[Test Assertions] Safety Checklist Verification:")
        
        # Check if the agent correctly evaluated chunk 004 as highly relevant and chunk 021 as a mismatch
        eval_map = {e.chunk_id: e for e in report.evaluations}
        
        assert eval_map["M-130_chunk_004"].is_applicable == True, "Failed to recognize DKA chunk applicability!"
        assert eval_map["M-130_chunk_021"].is_applicable == False, "Failed to catch irrelevant Discharge Checklist!"
        
        # Verify if the agent detected our hidden missing bicarbonate measurement trap
        print(f"-> Captured Uncertainties: '{report.uncertainties_or_missing_info}'")
        assert "none" not in report.uncertainties_or_missing_info.lower(), "Agent failed to capture the missing Bicarbonate gap!"
        
        print("\n✅ All automated verification checks passed successfully! Guardrail layer is ironclad.")
        
    except Exception as e:
        print(f"\n❌ [Test Failed] Audit Runtime Error: {str(e)}")

if __name__ == "__main__":
    run_auditor_test()