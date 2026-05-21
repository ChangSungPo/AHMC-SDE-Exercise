import os
import sys
from openai import OpenAI
from pathlib import Path

# =====================================================================
# Path Alignment Layer (Ensures Python can find backend modules)
# =====================================================================
CURRENT_SCRIPT = Path(__file__).resolve()
REPO_ROOT = CURRENT_SCRIPT.parent.parent
BACKEND_SRC = REPO_ROOT / "backend" / "src"
AGENTS_DIR = BACKEND_SRC / "agents"

sys.path.append(str(BACKEND_SRC))
sys.path.append(str(AGENTS_DIR))

# Now safely import our validated modules
from config import settings
from context_rewriter import ContextRewriterAgent

# =====================================================================
# Mock Chaotic Clinical Input (Extracted directly from your Case A doc)
# =====================================================================
MOCK_RAW_ER_NOTE = """
ER Attending: Dr. Nick Kwan
Chief Complaint: Diabetes issue

HPI: this is a 47-year-old male with recent diagnosis of diabetes, on Jardiance metformin, presents ED for 1 day history of inability to take deep breaths, sleep well, nausea, and vomiting. Pt denies chest pain, unilateral leg swelling, fever, chills, bloody emesis, abdominal pain.

Past Medical History: Diabetes
Past Surgical History: patient denies prior surgeries 
Family History: positive for hypertension

VITALS:
02/08/2026 15:00,105/67,Lying/Right Arm,80,98,Monitor,18, , ,100 %, , , ,Room Air 21%

LABS STAT RECORD:
GLUCOSE,93,mg/dL,L=70 H=99,02/08/2026 10:33,02/08/2026 10:36,final
CARBON DIOXIDE / BICARB,<7,mEq/L,L=22 H=32,02/08/2026 10:33,02/08/2026 10:36,final
pH, ARTERIAL,7.20,L=7.35 H=7.45,02/08/2026 10:45,02/08/2026 10:50,final
LACTIC ACID,1.9,mmol/L,L=0.7 H=2.0,02/08/2026 11:14,02/08/2026 10:36,final

MEDICAL DECISION:
47-year-old male presents ED for nausea, vomiting, inability to tolerate PO intake. Signs consistent with severe metabolic acidosis.
"""

# =====================================================================
# Execution and Verification Execution
# =====================================================================
def run_agent_test():
    print("=== [Test Startup] Testing ContextRewriterAgent ===")
    
    # 1. Initialize the official OpenAI Client using our centralized settings
    print(f"[Test] Initializing OpenAI Client with model: {settings.embedding_model_name}")
    client = OpenAI(api_key=settings.openai_api_key)
    
    # 2. Instantiate our Sub-Agent (Injecting the client)
    # We use gpt-4o-mini here as it is extremely fast and natively supports strict schemas
    agent = ContextRewriterAgent(client=client, model_name="gpt-4o-mini")
    
    try:
        # 3. Fire the raw note at the agent
        structured_snapshot = agent.rewrite_note(MOCK_RAW_ER_NOTE)
        
        # 4. Beautifully print out the resulting Pydantic object as formatted JSON
        print("\n" + "="*60)
        print("🎉 [Success] Agent Returned Perfect Structured Output:")
        print("="*60)
        
        # model_dump_json() is a built-in Pydantic method that serializes the object beautifully
        print(structured_snapshot.model_dump_json(indent=2))
        print("="*60)
        
        # 5. Diagnostic sanity assertions (Defensive Test Check)
        print("\n[Test Assertions] Verification Checklist:")
        assert structured_snapshot.age == 47, f"Expected age 47, got {structured_snapshot.age}"
        assert "jardiance" in [m.lower() for m in structured_snapshot.current_medications], "Failed to extract Jardiance!"
        assert structured_snapshot.labs.ph == 7.20, f"Expected pH 7.20, got {structured_snapshot.labs.ph}"
        print("✅ All automated verification checks passed successfully!")
        
    except Exception as e:
        print(f"\n❌ [Test Failed] An error occurred during agent execution: {str(e)}")

if __name__ == "__main__":
    run_agent_test()