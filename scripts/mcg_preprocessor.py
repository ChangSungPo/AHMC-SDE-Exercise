import json
import os
import re
from bs4 import BeautifulSoup, NavigableString

# =====================================================================
# [Stage 1] Knowledge and Navigation Map Extraction
# =====================================================================
def extract_glossary(relations_json_path):
    """
    1.1 Extract "Glossary Mapping"
    Target definitions block in relations.json, filter out UI layout, 
    and build a plaintext quantitative lookup table for medical terms.
    """
    if not os.path.exists(relations_json_path):
        return {}
    with open(relations_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    glossary_map = {}
    for def_id, content in data.get("definitions", {}).items():
        label = content.get("label", "").strip()
        definition_text = content.get("definition_text", "").strip()
        if label and definition_text:
            # Use lowercase as the key to facilitate case-insensitive matching with raw clinical notes later
            glossary_map[label.lower()] = {
                "def_id": def_id,
                "label": label,
                "definition": definition_text
            }
    print(f"Successfully built glossary dictionary! Extracted {len(glossary_map)} core medical terms.")
    return glossary_map

def build_navigation_maps(links_json_path):
    """
    1.2 Build "Neural Navigation and Citation Map"
    Iterate through links.json and precisely split into:
    - Line A (Internal Citations & Definitions): Medical term definitions and journal citations
    - Line B (Cross-Guideline Jumps): Routing flags pointing outside the main guideline (e.g., Observation Care)
    """
    if not os.path.exists(links_json_path):
        return [], []
    with open(links_json_path, 'r', encoding='utf-8') as f:
        links_list = json.load(f)
    line_a_internal = []
    line_b_cross_reference = []
    # Define characteristic keywords triggering Line B cross-references
    cross_ref_keywords = ["observation care", "see diabetes:", "cross-guideline", "discharge"]
    
    for link in links_list:
        text = link.get("text", "") or ""
        onclick = link.get("onclick", "") or ""
        context = link.get("context", "") or ""
        href = link.get("href", "") or ""
        
        # Establish basic characteristics of Line A: contains popup definitions, journal citations, or purely numeric citation subscripts
        is_citation = "popup_citation" in onclick or text.isdigit()
        is_definition = "popup_definition" in onclick
        # Establish basic characteristics of Line B: text or context mentions "observation care/discharge/cross-guideline", or points to external links outside the official domain
        is_cross_ref = (
            any(kw in text.lower() for kw in cross_ref_keywords) or
            any(kw in context.lower() for kw in cross_ref_keywords) or
            ("http" in href and "careguidelines.com" not in href)
        )
        
        info = {"link_id": link.get("link_id"), "text": text, "onclick": onclick}
        if is_cross_ref:
            line_b_cross_reference.append(info)
        elif is_definition or is_citation:
            line_a_internal.append(info)
            
    print(f"Successfully completed neural navigation network routing split!")
    print(f" -> Line A (Internal Citations/Pop-up Definitions) Total: {len(line_a_internal)} lines")
    print(f" -> Line B (Cross-Guideline Jump Routing) Total: {len(line_b_cross_reference)} lines")
    return line_a_internal, line_b_cross_reference

# =====================================================================
# [Stage 2] HTML Translation and Network Dynamic Injection
# =====================================================================
def perform_html_surgery(html_path, line_b_cross_ref):
    """
    2.1 & 2.2: Remove webpage noise and dynamically rewrite hyperlinks
    """
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"Original HTML file not found: {html_path}")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # --- 2.1 Remove Webpage Noise ---
    # Extract UI tags that interfere with tokens
    for noise in soup(["script", "style", "button", "meta", "link", "input"]):
        noise.extract()
    # Extract hidden blocks of pop-up dialogs repeating at the bottom (to avoid duplicate data interference)
    for dialog in soup.find_all("div"):
        classes = dialog.get("class", [])
        div_id = dialog.get("id", "") or ""
        if any("ui-dialog" in c for c in classes) or "def_" in div_id or "DEF" in div_id:
            dialog.extract()

    # --- 2.2 Neural Network Dynamic Rewrite ---
    # Iterate through all hyperlinks and rewrite them against the maps
    for a_tag in soup.find_all("a"):
        onclick_attr = a_tag.get("onclick", "") or ""
        text_content = a_tag.get_text().strip()
        
        # Check if it belongs to Line B (cross-guideline routing)
        is_cross_ref = any(kw in text_content.lower() for kw in ["observation care", "discharge", "cross-guideline"]) or \
                       any(kw in onclick_attr.lower() for kw in ["observation", "discharge"])
                       
        if is_cross_ref:
            # Case 2: Encounter cross-guideline routing -> Inject high-visibility semantic flags
            flag_type = "Observation_Care_Guideline"
            if "discharge" in text_content.lower() or "discharge" in onclick_attr.lower():
                flag_type = "Discharge_Pathway"
            semantic_flag = f" {text_content} [CROSS_REF_TRIGGER: {flag_type}] "
            a_tag.replace_with(soup.new_string(semantic_flag))
        elif "popup_citation" in onclick_attr or text_content.isdigit():
            # Case 1: Encounter journal citation -> Rewrite as a clean Markdown footnote tag to prevent numerical confusion
            footnote_style = f"[^{text_content}]"
            a_tag.replace_with(soup.new_string(footnote_style))
        else:
            # Other general terms, directly restore to plain text, washing away webpage tags
            a_tag.replace_with(soup.new_string(text_content))
    return soup

def recursive_html_to_md(node, depth=0, in_list=False):
    """
    2.3 Semantic Translation: Recursively convert cleaned DOM tree into Markdown
    Engineering rule: Must strictly preserve nested list indentation whitespace to maintain the MCG logic tree structure.
    """
    if isinstance(node, NavigableString):
        return node.string or ""
    tag = node.name
    
    # Process inline bold and italic
    if tag in ["b", "strong"]:
        inner = "".join(recursive_html_to_md(c, depth, in_list) for c in node.children).strip()
        return f" **{inner}** " if inner else ""
    if tag in ["i", "em"]:
        inner = "".join(recursive_html_to_md(c, depth, in_list) for c in node.children).strip()
        return f" *{inner}* " if inner else ""
        
    # Process headers
    if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        level = int(tag[1])
        inner = "".join(recursive_html_to_md(c, depth, in_list) for c in node.children).strip()
        return f"\n\n{'#' * level} {inner}\n\n"
        
    # Process paragraphs
    if tag == "p":
        inner = "".join(recursive_html_to_md(c, depth, in_list) for c in node.children).strip()
        return f"\n\n{inner}\n\n"
        
    # Process list containers (ul, ol)
    if tag in ["ul", "ol"]:
        # If already inside a list, it represents a "nested indentation", increase depth
        new_depth = depth + 1 if in_list else depth
        inner = "".join(recursive_html_to_md(c, new_depth, in_list=True) for c in node.children)
        return f"\n{inner}\n"
        
    # Process list item (li)
    if tag == "li":
        indent = "    " * depth  # Each level indents 4 spaces
        inner = "".join(recursive_html_to_md(c, depth, in_list) for c in node.children).strip()
        # Keep indentation aligned during line breaks
        inner = re.sub(r'\n+', '\n' + indent + "  ", inner)
        return f"{indent}* {inner}\n"
        
    # Remaining non-semantic tags (span, div, body) pass through for deeper parsing
    return "".join(recursive_html_to_md(c, depth, in_list) for c in node.children)

def clean_markdown_whitespace(md_text):
    """
    Final trim: Remove consecutive redundant empty lines to keep the layout extremely compact and clean
    """
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)  # Keep a maximum of two newlines
    md_text = re.sub(r'\n ++\n', '\n\n', md_text)  # Clear spaces within empty lines
    return md_text.strip()


# =====================================================================
# [Stage 3] Clinical Semantic Chunking
# =====================================================================
def semantic_markdown_chunker(md_text, guideline_id="M-130"):
    """
    Perform macro-section semantic slicing based on Markdown headers (# to ####).
    Ensure the entire logical chain of clinical diagnosis is completely preserved in the same block.
    """
    # Use lookahead regex to slice at header lines less than or equal to h4 while keeping the content intact.
    pattern = r'\n(?=#{1,4} )'
    sections = re.split(pattern, "\n" + md_text)
    
    chunks = []
    chunk_index = 1
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Parse the first line of the block to grab the actual header
        lines = section.split("\n")
        first_line = lines[0].strip()
        
        header_title = first_line.strip("# ").strip() if first_line.startswith("#") else "General Information"
        
        # --- Automated Clinical Metadata Alignment Logic ---
        section_type = "General Guidance"
        header_lower = header_title.lower()
        
        if any(k in header_lower for k in ["clinical indication", "admission", "criteria"]):
            section_type = "Inpatient Admission"
        elif any(k in header_lower for k in ["discharge", "destination", "planning"]):
            section_type = "Discharge Planning"
        elif any(k in header_lower for k in ["alternative", "observation"]):
            section_type = "Alternatives to Admission"
        elif any(k in header_lower for k in ["length of stay", "recovery course"]):
            section_type = "Optimal Recovery Course"
            
        # Determine target disease: This guideline is Diabetes (M-130); if ketoacidosis is mentioned, precisely align to DKA
        target_disease = "Diabetes"
        if "ketoacidosis" in section.lower() or "dka" in section.lower():
            target_disease = "Diabetic Ketoacidosis"
            
        chunks.append({
            "chunk_id": f"{guideline_id}_chunk_{chunk_index:03d}",
            "header": header_title,
            "content": section,
            "metadata": {
                "guideline_id": guideline_id,
                "section": section_type,
                "target_disease": target_disease
            }
        })
        chunk_index += 1
        
    print(f"Successfully executed Stage 3 semantic chunking! Precisely split the complete guideline into {len(chunks)} clinical chunks.")
    return chunks


# =====================================================================
# [Stage 4] Context Enrichment
# =====================================================================
def enrich_chunks_with_glossary(chunks, glossary_map):
    """
    Perform keyword scanning for each semantic chunk, dynamically stitching Stage 1 
    medical term quantitative indicators onto the text tail.
    """
    enriched_chunks = []
    stitched_count = 0
    
    for chunk in chunks:
        content_lower = chunk["content"].lower()
        matched_definitions = []
        
        # Iterate through the dictionary built in Stage 1
        for term, info in glossary_map.items():
            # Use the \b word boundary regex to ensure a precise match of the "entire medical term", preventing partial word mismatches.
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, content_lower):
                matched_text = f"#### 📌 {info['label']}\n{info['definition']}"
                matched_definitions.append(matched_text)
                
        # If the chunk contains terms from the guideline, initiate surgical stitching
        if matched_definitions:
            stitched_count += 1
            enrichment_section = (
                "\n\n"
                "==================================================\n"
                "🔍 Stitched Glossary Context\n"
                "==================================================\n"
                + "\n\n".join(matched_definitions)
            )
            # Dynamically stitch quantitative indicators to the text tail
            chunk["content"] += enrichment_section
            
        enriched_chunks.append(chunk)
        
    print(f"Successfully executed Stage 4 context enrichment! Total of {stitched_count} chunks completed medical glossary dynamic reinforcement.")
    return enriched_chunks


# =====================================================================
# [Main] Program Execution and End-to-End Verification
# =====================================================================
if __name__ == "__main__":
    # Configure paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    
    HTML_FILE = os.path.join(DATA_DIR, "M-130__Diabetes.raw.html")
    RELATIONS_FILE = os.path.join(DATA_DIR, "M-130__Diabetes.relations.json")
    LINKS_FILE = os.path.join(DATA_DIR, "M-130__Diabetes.links.json")
    
    print("=== [End-to-End Startup] Clinical-Grade RAG Data Preprocessing Pipeline ===")
    
    # Execute Stage 1
    glossary = extract_glossary(RELATIONS_FILE)
    line_a, line_b = build_navigation_maps(LINKS_FILE)
    
    # Execute Stage 2
    print("\n[Step 1] Removing HTML noise and dynamically rewriting neural network...")
    soup_surgery = perform_html_surgery(HTML_FILE, line_b)
    
    print("[Step 2] Executing semantic translation, restoring nested logic tree...")
    md_text = recursive_html_to_md(soup_surgery)
    clean_md = clean_markdown_whitespace(md_text)
    
    # Execute Stage 3
    initial_chunks = semantic_markdown_chunker(clean_md)
    
    # Execute Stage 4
    final_documents = enrich_chunks_with_glossary(initial_chunks, glossary)
    
    # --- Verification and Results Unboxing ---
    print("\n" + "="*60)
    print("🏆 Verification: Random Check of Gold Chunk Containing DKA Admission Criteria 🏆")
    print("="*60)
    
    for doc in final_documents:
        if doc["metadata"]["section"] == "Inpatient Admission" and "ketoacidosis" in doc["content"].lower():
            print(f"[Chunk ID]: {doc['chunk_id']}")
            print(f"[Section Classification]: {doc['metadata']['section']}")
            print(f"[Target Disease]: {doc['metadata']['target_disease']}")
            print(f"[Header Title]: {doc['header']}")
            print("-" * 40)
            
            content = doc["content"]
            # Fixed print logic: use .find() to locate header position, printing all the way to the end of the string
            if "🔍 Stitched Glossary Context" in content:
                idx = content.find("🔍 Stitched Glossary Context")
                print(content[:600] + "\n\n... [Intermediate clauses omitted] ...\n")
                print(content[idx:])
            else:
                print(content[:1000] + "\n... Content too long, omitted ...")
            break
            
    print("="*60)
    print("Finish")