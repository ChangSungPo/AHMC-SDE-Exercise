from openai import OpenAI
from .schemas import PatientSnapshotSchema

class ContextRewriterAgent:
    """
    Agent specialized in clinical text features extraction.
    Takes an unstructured, messy multi-line ER/H&P note and synthesizes into a structured snapshot.
    """
    def __init__(self, client: OpenAI, model_name: str = "gpt-4o-mini"):
        self.client = client
        self.model_name = model_name
        
    def _get_system_prompt(self) -> str:
        return (
            "You are an expert Clinical Informatics Specialist and an elite Medical Scribe.\n"
            "Your task is to review a chaotic, unstructured, multi-line Emergency Department (ER) or "
            "History & Physical (H&P) chart note and distill it into a perfect structured medical snapshot.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Extract facts with surgical precision. Do not infer or invent numbers that are not in the notes.\n"
            "2. Pay absolute attention to medication details (e.g., SGLT2 inhibitors like Jardiance, Metformin) "
            "as they drive critical clinical reasoning for specific conditions like Euglycemic DKA.\n"
            "3. Parse vitals and laboratory text streams carefully. Extract exact values like pH, Bicarbonate, Glucose, and Lactic acid.\n"
            "4. Summarize the History of Present Illness (HPI) chronologically and clearly, removing redundant system metadata but preserving all clinical context."
        )

    def rewrite_note(self, raw_note: str) -> PatientSnapshotSchema:
        print("[Context Rewriter Agent] Initiating clinical note surgery and extraction...")
        
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Here is the raw clinical note to process:\n\n{raw_note}"}
            ],
            response_format=PatientSnapshotSchema, # This triggers native Structured Outputs
            temperature=0.5 # Force deterministic extraction
        )
        
        message = response.choices[0].message
        
        if message.refusal:
            raise ValueError(f"[Context Rewriter Error] Model refused to process note: {message.refusal}")
        
        structured_snapshot = message.parsed
        
        if structured_snapshot is None:
            raise ValueError(
                "[Context Rewriter Error] Failed to parse clinical note. "
                "The response was truncated or did not conform to the schema."
            )
        
        print(f"[Context Rewriter Agent] Extraction complete.")
        
        return structured_snapshot