from openai import OpenAI
from typing import List, Dict, Any
from .schemas import PatientSnapshotSchema, ClinicalAuditReportSchema

class RelevantDocumentAgent:
    """
    Agent acting as a Clinical Quality Guard.
    Evaluates retrieved MCG guidelines against the patient's true active clinical state,
    """
    def __init__(self, client: OpenAI, model_name: str = "gpt-4o-mini"):
        self.client = client
        self.model_name = model_name

    def _get_system_prompt(self) -> str:
        return (
            "You are an expert Physician Auditor and Insurance Medical Necessity Director.\n"
            "Your job is to cross-examine a structured patient snapshot against a collection of candidate MCG clinical guidelines.\n\n"
            "CRITICAL AUDITING PROTOCOLS:\n"
            "1. Evaluate medical congruence, not just keyword overlap. Ensure the specific patient diagnostic context matches the guideline's intent.\n"
            "2. Scrutinize required thresholds. If a guideline requires a certain quantitative threshold (e.g., Bicarbonate <= 18 or pH < 7.30) to justify inpatient admission, check if the patient meets it.\n"
            "3. Track missing metrics (Gaps Analysis). If a guideline states that certain criteria are required for evaluation, but the patient profile doesn't mention them at all, flag them as missing. This is vital for clinical uncertainty tracking."
        )

    def audit_retrieved_documents(self, snapshot: PatientSnapshotSchema, retrieved_docs: List[Dict[str, Any]]) -> ClinicalAuditReportSchema:
        print(f"[Relevant Document Agent] Initiating audit on {len(retrieved_docs)} candidate chunks...")
        
        # Serialize patient profile to string
        snapshot_json_str = snapshot.model_dump_json(indent=2)
        
        # Serialize candidate guidelines into a clean consolidated text payload
        docs_payload_list = []
        for doc in retrieved_docs:
            doc_block = (
                f"--- START OF CHUNK: {doc['chunk_id']} ---\n"
                f"Metadata: {doc['metadata']}\n"
                f"Content:\n{doc['content']}\n"
                f"--- END OF CHUNK: {doc['chunk_id']} ---"
            )
            docs_payload_list.append(doc_block)
        consolidated_docs_str = "\n\n".join(docs_payload_list)
        
        # Call OpenAI Structured Outputs API
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {
                    "role": "user", 
                    "content": (
                        f"== PATIENT PROFILE STATE ==\n{snapshot_json_str}\n\n"
                        f"== CANDIDATE MCG GUIDELINES ==\n{consolidated_docs_str}"
                    )
                }
            ],
            response_format=ClinicalAuditReportSchema,
            temperature=0.0 # Force objective clinical evaluation
        )
        
        audit_report = response.choices[0].message.parsed
        
        if audit_report is None:
            raise ValueError("[Relevant Document Agent Error] Failed to generate structured clinical audit report.")
            
        print(f"[Relevant Document Agent] Auditing complete. Successfully synthesized uncertainties/missing info details.")
        return audit_report