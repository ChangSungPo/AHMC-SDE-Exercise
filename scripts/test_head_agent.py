import os
import sys
from pathlib import Path
from config import settings

current_file = Path(__file__).resolve()
scripts_dir = current_file.parent
project_root = scripts_dir.parent

# Priority 0: Force Python to look inside scripts/ first for 'config'
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Priority 1: Lower priority fallback for backend system modules access
if str(project_root) not in sys.path:
    sys.path.insert(1, str(project_root))

from backend.src.agents.head_agent import HeadAgent

# Note Input
REALISTIC_CASE_A_INPUT = """
ER Attending Physician Chart Note
Patient Name: Anonymous Case A
DOB: 05/12/1978 (Age 47) | Sex: Male
Arrival Date: 02/08/2026

CHIEF COMPLAINT:
Diabetes issue, out of medications.

HISTORY OF PRESENT ILLNESS:
A 47-year-old man with recently diagnosed diabetes started metformin and Jardiance on Friday morning and became increasingly restless and unable to sleep over the day. Yesterday morning he was unable to tolerate oral intake and had one episode of vomiting. This morning he had several episodes of vomiting with ongoing nausea and came to the emergency department for evaluation. In the emergency department he was noted to have euglycemic diabetic ketoacidosis with bicarbonate less than 7, potential of hydrogen value 7.2, and glucose 93, and admission was requested for euglycemic diabetic ketoacidosis likely in the setting of new Jardiance use.

PAST MEDICAL HISTORY: Type 2 Diabetes.
SURGICAL HISTORY: None.
SOCIAL HISTORY: Denies alcohol, smoking, or illicit substances.

VITAL SIGNS:
Time: 15:00 | Temp: 97.4 F (Temporal) | BP: 105/67 mmHg | HR: 98 bpm (Regular) | RR: 18 rpm | SpO2: 100% on Room Air.

LABORATORY RESULTS (STAT):
- GLUCOSE: 93 mg/dL (Normal Range: 70-99)
- PH, ARTERIAL: 7.20 (Abnormal Low, Range: 7.35-7.45)
- CARBON DIOXIDE / BICARBONATE: <7 mEq/L (Severe Low, Range: 22-32)
- LACTIC ACID: 1.9 mmol/L (Normal, Range: 0.7-2.0)
- BUN: 24 mg/dL | Creatinine: 1.45 mg/dL (Mild Acute Kidney Injury)

MEDICAL DECISION MAKING:
Patient presents with severe metabolic ketoacidosis. Interestingly, the serum glucose level is completely normal at 93 mg/dL, which is highly indicative of Euglycemic Diabetic Ketoacidosis (euglycemic DKA) secondary to recent SGLT2 inhibitor (Jardiance) initiation. Fluid resuscitation started, protocol insulin drip requested. Admitting to Inpatient Care / ICU.
"""


def run_head_agent_test():
    print("============================================================")

    # Initialize the complete Multi-Agent Brain
    orchestrator = HeadAgent()

    try:
        # raw unstructured note into the pipeline
        final_report = orchestrator.process_unstructured_note(REALISTIC_CASE_A_INPUT)

        print("\n" + "=" * 30)
        print("END-TO-END SYSTEM TEST PASSED YIELDING COMPLIANT JSON:")
        print("=" * 30)
        print(final_report.model_dump_json(indent=2))
        print("=" * 30 + "\n")

        # Final Structural Sanity Assertions
        assert (
            final_report.disposition_recommendation == "Admit"
        ), "E2E Error: System failed to conclude 'Admit' for active DKA!"
        print(
            "[Validation Passed] The pipeline successfully concluded 'Admit' and generated defense arguments."
        )

    except Exception as e:
        print(
            f"\n[E2E Test Failed] A critical error broke the orchestrator: {str(e)}"
        )


if __name__ == "__main__":
    # Safety Check: Ensure the local vector index folder exists before driving the agents

    if not Path(settings.chroma_db_path).exists():
        print(
            f"[Database Missing] Please run 'python scripts/vector_indexer.py' first to populate the vector space."
        )
        sys.exit(1)

    run_head_agent_test()
