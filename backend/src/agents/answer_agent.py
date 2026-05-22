from openai import OpenAI
from typing import List, Dict, Any
from .schemas import PatientSnapshotSchema, ClinicalAuditReportSchema, FinalAssessmentSchema


class AnswerAgent:
    """
    Agent specialized in final documentation synthesis and medical writing.
    Combines the processed patient features with the audited MCG criteria report
    to generate the the Revised HPI.
    """

    def __init__(self, client: OpenAI, model_name: str = "gpt-4o"):
        self.client = client
        self.model_name = model_name

    def _get_system_prompt(self) -> str:
        return (
            "You are an expert Chief Medical Officer and a Senior Utilization Review Physician Advisor.\n"
            "Your task is to compile the final structured clinical determination report by fusing the patient snapshot "
            "with the audited MCG guidelines report and their corresponding text contents.\n\n"
            "CRITICAL WRITING SPECIFICATIONS FOR REVISED_HPI:\n"
            "1. Avoid passive listing. Write a highly analytical, objective clinical narrative.\n"
            "2. Adopt a rigorous 'Sentence-by-Sentence Evidence Cross-Examination' mechanism. Explicitly contrast "
            "the patient's quantitative results directly against the retrieved MCG thresholds (e.g., instead of writing "
            "'the patient had metabolic acidosis', write 'The patient presented with a severe metabolic acidosis "
            "as evidenced by an arterial pH of 7.20, which directly satisfies the retrieved MCG threshold of pH less than 7.30').\n"
            "3. Highlight physiological high-risk interactions. Explicitly document how specific medications or complex drug-disease "
            "mechanisms drove severe physiological decompression, even if baseline screening flags appeared misleadingly normal "
            "(such as a near-normal serum glucose level masking the presence of a severe euglycemic DKA state).\n"
            "4. Ensure that the 'disposition_recommendation' matches the audited guidelines logic strictly. If key criteria are satisfied, "
            "the recommendation of 'Admit' or 'Observe' must be robustly justified in the core narrative prose."
        )

    def synthesize_final_report(self, snapshot: PatientSnapshotSchema, audit_report: ClinicalAuditReportSchema, filtered_guidelines: List[Dict[str, Any]]) -> FinalAssessmentSchema:
        print("[Answer Agent] Synthesizing final compliance artifacts and composing revised HPI narrative...")

        snapshot_json = snapshot.model_dump_json(indent=2)
        audit_json = audit_report.model_dump_json(indent=2)

        guidelines_context_list = []
        for doc in filtered_guidelines:
            guidelines_context_list.append(f"=== GOLDEN CLINICAL GUIDELINE: {doc['chunk_id']} ===\n" f"Content:\n{doc['content']}")
        consolidated_guidelines_text = "\n\n".join(guidelines_context_list)

        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {
                    "role": "user",
                    "content": (
                        f"== EXTRACTED PATIENT SNAPSHOT ==\n{snapshot_json}\n\n"
                        f"== AUDITED MCG GUIDELINES EVALUATION ==\n{audit_json}"
                        f"== VERIFIED MCG GUIDELINE TEXTS ==\n{consolidated_guidelines_text}"
                    ),
                },
            ],
            response_format=FinalAssessmentSchema,
            temperature=0.2,  # Lower temperature for stable clinical adherence with writing flexibility
        )

        final_report = response.choices[0].message.parsed

        if final_report is None:
            raise ValueError("[Answer Agent Error] Failed to generate structured final assessment report.")

        print(f"[Answer Agent] Final artifact compilation successful. Recommendation finalized as: {final_report.disposition_recommendation}")
        return final_report
