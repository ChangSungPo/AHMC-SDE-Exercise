from openai import OpenAI
from typing import List, Dict, Any
from .schemas import PatientSnapshotSchema, QueryGenerationSchema

class QueryAgent:
    """
    Agent specialized in vector database retrieval operations.
    """
    def __init__(self, client: OpenAI, model_name: str = "gpt-4o-mini"):
        self.client = client
        self.model_name = model_name

    def _get_system_prompt(self) -> str:
        return (
            "You are an expert Clinical Search Engineer and Medical Librarian.\n"
            "Your task is to review a structured patient snapshot (vitals, labs, medications, clinical findings) "
            "and generate 2 to 3 highly targeted semantic search queries to retrieve the exact matching MCG clinical guidelines.\n\n"
            "STRATEGIC INSTRUCTIONS:\n"
            "1. Focus on high-risk triggers. Look for specific drug-disease interactions (e.g., SGLT2 inhibitors like Jardiance causing normal-glucose or euglycemic DKA).\n"
            "2. Formulate phrases that mimic MCG guideline headings, such as 'Inpatient Admission Criteria', 'Observation Care Guidelines', or specific disease pathways like 'Diabetic Ketoacidosis'.\n"
            "3. Do not include patient-specific details like names or specific dates in the search queries; keep the queries focused on the clinical conditions, laboratory abnormalities, and critical thresholds."
        )

    def retrieve_relevant_guidelines(self, snapshot: PatientSnapshotSchema, collection: Any, n_results_per_query: int = 2) -> List[Dict[str, Any]]:
        print("[Query Agent] Analyzing structured patient snapshot to formulate search strategies...")
        
        # Serialize the Pydantic snapshot to a readable text representation for the prompt
        snapshot_json_str = snapshot.model_dump_json(indent=2)
        
        # Structured Output Request to OpenAI to get optimized queries
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Here is the structured patient snapshot:\n\n{snapshot_json_str}"}
            ],
            response_format=QueryGenerationSchema,
            temperature=0.0
        )
        
        generated_payload = response.choices[0].message.parsed
        
        if generated_payload is None:
            raise ValueError("[Query Agent Error] Failed to generate structured search queries.")
            
        print(f"[Query Agent] Clinical Rationale: {generated_payload.clinical_rationale}")
        print(f"[Query Agent] Formulated Queries: {generated_payload.search_queries}")
        
        # Execute queries to ChromaDB
        deduplicated_chunks: Dict[str, Dict[str, Any]] = {}
        
        for query_str in generated_payload.search_queries:
            print(f"[Query Agent] Executing vector lookup for query: '{query_str}'...")
            
            # ChromaDB query execution
            query_results = collection.query(
                query_texts=[query_str],
                n_results=n_results_per_query
            )
            
            # Unpack ChromaDB structure safely
            if not query_results or not query_results.get("ids"):
                continue
                
            ids = query_results["ids"][0]
            documents = query_results["documents"][0]
            metadatas = query_results["metadatas"][0]
            
            for i in range(len(ids)):
                chunk_id = ids[i]
                # If the chunk isn't captured yet, store it under its unique chunk_id
                if chunk_id not in deduplicated_chunks:
                    deduplicated_chunks[chunk_id] = {
                        "chunk_id": chunk_id,
                        "content": documents[i],
                        "metadata": metadatas[i]
                    }
                    
        final_retrieved_list = list(deduplicated_chunks.values())
        print(f"[Query Agent] Vector search completed. Retrieved {len(final_retrieved_list)} unique matching MCG clinical chunks.")
        
        return final_retrieved_list