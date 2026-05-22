import os
import sys
from openai import OpenAI
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

current_file = Path(__file__).resolve()
scripts_dir = current_file.parent
project_root = scripts_dir.parent

# Priority 0: Force Python to look inside scripts/ first for 'config'
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Priority 1: Lower priority fallback for backend system modules access
if str(project_root) not in sys.path:
    sys.path.insert(1, str(project_root))

from config import settings
from backend.src.agents.schemas import PatientSnapshotSchema, VitalsSchema, LabsSchema
from backend.src.agents.query_agent import QueryAgent

# =====================================================================
# Pre-structured Snapshot (Simulating ContextRewriterAgent output for Case A)
# =====================================================================
MOCK_PASSED_SNAPSHOT = PatientSnapshotSchema(
    age=47,
    gender="male",
    chief_complaint="Diabetes issue with severe nausea and breathing discomfort",
    history_of_present_illness="Patient is a 47yo male presenting with progressive vomiting and shortness of breath after starting Jardiance.",
    past_medical_history=["Type 2 Diabetes Mellitus"],
    current_medications=["Jardiance", "Metformin"],
    key_clinical_findings=["Inability to take deep breaths", "Lethargic appearance", "Persistent emesis"],
    vitals=VitalsSchema(
        blood_pressure="105/67", systolic_bp=105, diastolic_bp=67, heart_rate=98, respiratory_rate=18, spo2=100
    ),
    labs=LabsSchema(
        glucose=93, ph=7.20, bicarbonate=7, lactate=1.9, other_significant_labs={}
    )
)

def run_query_agent_test():
    print("=== [Test Startup] Testing QueryAgent with Local ChromaDB ===")
    
    # 1. Initialize official clients using validated configs
    openai_client = OpenAI(api_key=settings.openai_api_key)
    chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)
    
    print(f"[Test] Loading ChromaDB collection: '{settings.chroma_collection_name}'...")
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=settings.openai_api_key,
        model_name=settings.embedding_model_name
    )
    
    collection = chroma_client.get_collection(name=settings.chroma_collection_name, 
                                              embedding_function=openai_ef  # type: ignore
                                              )
    
    # 2. Instantiate our QueryAgent
    agent = QueryAgent(client=openai_client, model_name="gpt-4o-mini")
    
    try:
        # 3. Trigger the retrieval workflow
        retrieved_docs = agent.retrieve_relevant_guidelines(
            snapshot=MOCK_PASSED_SNAPSHOT, 
            collection=collection,
            n_results_per_query=5
        )
        
        print("\n" + "="*60)
        print("[Success] Retrieved Documents via QueryAgent Logic:")
        print("="*60)
        
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"[{i}] Chunk ID : {doc['chunk_id']}")
            print(f"    Header   : {doc['metadata']['header']}")
            print(f"    Section  : {doc['metadata']['section']}")
            print(f"    Disease  : {doc['metadata']['target_disease']}")
            print(f"    Snippet  : {doc['content'].strip()}...\n")
            
        print("="*60)
        
        # 4. Verification Assertion Check (Ensure our key DKA chunk is captured)
        retrieved_ids = [doc["chunk_id"] for doc in retrieved_docs]
        assert "M-130_chunk_004" in retrieved_ids, "Critical Error: Gold DKA admission chunk was missed by the search queries!"
        print("[Validation Passed] QueryAgent generated accurate queries that extracted the golden DKA guideline!")
        
    except Exception as e:
        print(f"\n[Test Failed] Runtime Error: {str(e)}")

if __name__ == "__main__":
    # Quick sanity check: Ensure vector database directory exists before querying
    if not Path(settings.chroma_db_path).exists():
        print(f"[Error] Local vector storage not found at {settings.chroma_db_path}. Please execute vector_indexer.py first.")
        sys.exit(1)
        
    run_query_agent_test()