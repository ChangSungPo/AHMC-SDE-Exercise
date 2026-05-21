import os
import json
import chromadb
from chromadb.utils import embedding_functions

from config import settings

# Import our cleaning pipeline functions from mcg_preprocessor
from mcg_preprocessor import (
    extract_glossary,
    build_navigation_maps,
    perform_html_surgery,
    recursive_html_to_md,
    clean_markdown_whitespace,
    semantic_markdown_chunker,
    enrich_chunks_with_glossary
)

def run_end_to_end_pipeline(data_dir):
    """
    Executes the 4-stage preprocessing pipeline to retrieve finalized clinical documents.
    """
    html_file = os.path.join(data_dir, "M-130__Diabetes.raw.html")
    relations_file = os.path.join(data_dir, "M-130__Diabetes.relations.json")
    links_file = os.path.join(data_dir, "M-130__Diabetes.links.json")
    
    # Stage 1: Build glossary and maps
    glossary = extract_glossary(relations_file)
    _, line_b = build_navigation_maps(links_file)
    
    # Stage 2: Web noise removal and Markdown conversion
    soup_surgery = perform_html_surgery(html_file, line_b)
    md_text = recursive_html_to_md(soup_surgery)
    clean_md = clean_markdown_whitespace(md_text)
    
    # Stage 3: Semantic chunking
    initial_chunks = semantic_markdown_chunker(clean_md)
    
    # Stage 4: Context enrichment via glossary stitching
    final_documents = enrich_chunks_with_glossary(initial_chunks, glossary)
    return final_documents


def index_clinical_chunks_to_vector_db(documents):
    """
    Initializes local persistent ChromaDB, converts text to vectors using OpenAI,
    and stores chunks along with their clinical metadata.
    """
    # Ensure OPENAI_API_KEY is available in environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not found.")
        print("Please set it before running, or ChromaDB will fail to generate embeddings.")
    
    print(f"\n[Vector DB] Initializing persistent storage at: {settings.chroma_db_path}")
    # Initialize the persistent client (creates local files in your repo)
    client = chromadb.PersistentClient(path=settings.chroma_db_path)
    
    # Configure OpenAI Embedding Function (text-embedding-3-small is cheap and highly effective)
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=settings.openai_api_key,
        model_name=settings.embedding_model_name
    )
    
    # Create or get the collection
    print(f"[Vector DB] Creating or locating collection: '{settings.chroma_collection_name,}'...")
    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        embedding_function=openai_ef # type: ignore
    )
    
    # Prepare data payloads for ChromaDB bulk insertion
    ids = []
    texts = []
    metadatas = []
    
    for doc in documents:
        ids.append(doc["chunk_id"])
        texts.append(doc["content"])
        
        # Flatten dictionary values or ensure they conform to Chroma primitive metadata types (str, int, float, bool)
        metadata_payload = {
            "guideline_id": doc["metadata"]["guideline_id"],
            "section": doc["metadata"]["section"],
            "target_disease": doc["metadata"]["target_disease"],
            "header": doc["header"]
        }
        metadatas.append(metadata_payload)
        
    print(f"[Vector DB] Bulk inserting {len(texts)} vectorized documents into ChromaDB...")
    
    # ChromaDB handles bulk upsert safely
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )
    
    print("🎉 [Success] ChromaDB indexing completed successfully!")
    return collection


def verify_database_query(collection):
    """
    Performs a diagnostic search to verify semantic retrieval is fully operational.
    """
    print("\n" + "="*60)
    print("🔎 Running Diagnostic Semantic Search Verification...")
    print("="*60)
    
    # Simulate a query that an Agent might make when inspecting Case B
    test_query = "What are the inpatient admission criteria for diabetic ketoacidosis with low blood pressure?"
    print(f"Mock Agent Query: '{test_query}'\n")
    
    results = collection.query(
        query_texts=[test_query],
        n_results=1  # Fetch the top-1 most relevant clinical chunk
    )
    
    # Extract and display results safely
    if results and results["documents"]:
        retrieved_id = results["ids"][0][0]
        retrieved_doc = results["documents"][0][0]
        retrieved_meta = results["metadatas"][0][0]
        
        print(f"✨ [Match Found] Best Fitting Chunk ID: {retrieved_id}")
        print(f"👉 [Section Tag]: {retrieved_meta['section']}")
        print(f"👉 [Target Disease]: {retrieved_meta['target_disease']}")
        print("-" * 50)
        print("Truncated Chunk Content:")
        # print(retrieved_doc[:500] + "\n\n... [Content continues] ...")
        print(retrieved_doc)
        
        # Check if our stitched glossary is visible to the retriever
        if "Stitched Glossary Context" in retrieved_doc:
            print("\n✅ [Validation Passed] Stitched Glossary Context is present in retrieved text stream!")
    else:
        print("❌ [Error] Diagnostic query returned no matches. Check embedding configuration.")
    print("="*60)


# =====================================================================
# Main Execution Entrypoint
# =====================================================================
if __name__ == "__main__":
    # Path configurations relative to repository setup
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(SCRIPT_DIR)
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DB_DIR = os.path.join(BASE_DIR, "vector_db") # Stores local vector database artifacts
    
    print("=== Starting Vector DB Indexing Script ===")
    
    # 1. Run the preprocessor to fetch finalized clinical chunks
    processed_docs = run_end_to_end_pipeline(DATA_DIR)
    
    # 2. Persist the chunks into local Vector DB
    active_collection = index_clinical_chunks_to_vector_db(processed_docs)
    
    # 3. Perform a semantic query check to verify the database works flawlessly
    verify_database_query(active_collection)