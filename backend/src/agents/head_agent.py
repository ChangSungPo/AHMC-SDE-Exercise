import chromadb
from openai import OpenAI
from config import settings
from agents.schemas import FinalAssessmentSchema
from agents.context_rewriter import ContextRewriterAgent
from agents.query_agent import QueryAgent
from agents.relevant_document_agent import RelevantDocumentAgent
from agents.answer_agent import AnswerAgent
from chromadb.utils import embedding_functions

MODEL_NAME = "gpt-4o"


class HeadAgent:
    """
    The Central Orchestrator of the Multi-Agent Clinical Review System.
    Responsible for centralized resource lifecycle initialization, dependency injection,
    and driving the end-to-end data pipeline across all specialized sub-agents.
    """

    def __init__(self):
        print("[Head Agent] Initializing centralized clinical intelligence framework...")

        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)

        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=settings.openai_api_key, model_name=settings.embedding_model_name)

        # Load the targeted persistent MCG vector store collection
        self.collection = self.chroma_client.get_collection(
            name=settings.chroma_collection_name,
            embedding_function=self.openai_ef,  # type: ignore
        )

        # Pass the centralized client into each worker
        self.context_rewriter = ContextRewriterAgent(client=self.openai_client, model_name=MODEL_NAME)

        self.query_worker = QueryAgent(client=self.openai_client, model_name=MODEL_NAME)

        self.document_auditor = RelevantDocumentAgent(client=self.openai_client, model_name=MODEL_NAME)

        self.final_writer = AnswerAgent(client=self.openai_client, model_name=MODEL_NAME)

        print("[Head Agent] All specialized sub-agents are online and resource-injected.")

    def process_unstructured_note(self, raw_note: str) -> FinalAssessmentSchema:
        """
        Executes the full end-to-end multi-agent pipeline sequentially.
        Transforms chaotic plain text notes into a bulletproof compliance report.
        """
        print("\n=== [Pipeline Start] Head Agent Routing New Clinical Case ===")

        # 1: Text rewrite
        struct_note = self.context_rewriter.rewrite_note(raw_note)

        # 2: Targeted Vector DB Querying
        candidate_guidelines = self.query_worker.retrieve_relevant_guidelines(
            snapshot=struct_note,
            collection=self.collection,
            n_results_per_query=4,  # Ample retrieval window to prevent missing thresholds
        )

        # 3: Cross-Checking
        audit_report = self.document_auditor.audit_retrieved_documents(snapshot=struct_note, retrieved_docs=candidate_guidelines)

        document_map = {eval_item.chunk_id: eval_item.is_applicable for eval_item in audit_report.evaluations}

        filtered_guidelines = [doc for doc in candidate_guidelines if document_map.get(doc["chunk_id"], False) == True]

        # 4: Final Document Synthesis
        final_assessment_report = self.final_writer.synthesize_final_report(snapshot=struct_note, audit_report=audit_report, filtered_guidelines=filtered_guidelines)

        print("=== [Pipeline Success] Head Agent Successfully Compiled Final Artifacts ===\n")
        return final_assessment_report
