import os
import re
import shutil
import pypdf
from colorama import Fore, Style, init
from . import parse_query as pq

init(autoreset=True)

# =================CONFIGURATION=================
DEBUG_MODE = False  # Toggles verbose logging for internal logic inspection
PROXIMITY_WINDOW = 50  # Max token distance to consider terms contextually related
SCORE_HIGH_THRESHOLD = 100
SCORE_MEDIUM_THRESHOLD = 50
# ===============================================

def extract_text_from_pdf(pdf_path):
    """
    Extracts raw text content from a PDF file.
    Swallows exceptions to ensure batch processing continuity.
    """
    text = ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    except Exception as e:
        if DEBUG_MODE: 
            print(f"{Fore.RED}[DEBUG] PDF Read Error: {e}")
    return text

def find_term_indices(text_words, term):
    """
    Locates indices of a specific term within the tokenized text.
    Differentiates between exact phrase matching (*term*) and loose substring matching.
    """
    indices = []
    
    # Logic 1: Exact Phrase Matching (*term*)
    if term.startswith("*") and term.endswith("*"):
        clean_phrase = term.strip("*").lower()
        phrase_words = clean_phrase.split()
        
        if not phrase_words: 
            return []
            
        first_word = phrase_words[0]
        phrase_len = len(phrase_words)
        
        # Scan text for the first word, then verify the subsequent sequence
        for i, word in enumerate(text_words):
            if word == first_word:
                if text_words[i:i+phrase_len] == phrase_words:
                    indices.append(i)

    # Logic 2: Loose Token Matching
    else:
        clean_term = term.lower()
        for i, word in enumerate(text_words):
            # Permissive matching strategy: 'in' operator handles substrings 
            # (e.g., '2d' successfully matches inside '2d-materials')
            if clean_term in word: 
                indices.append(i)
                
    return indices

def calculate_relevance_score(text, query_expansion, filename=""):
    """
    Computes a relevance score based on term presence and proximity.
    
    Pipeline:
    1. Tokenize text (alphanumeric split).
    2. Handle Implicit ANDs in query.
    3. Check Forbidden terms (immediate rejection).
    4. Calculate Base Score based on mandatory term coverage.
    5. Apply Proximity Bonus if terms appear within the defined window.
    """
    # Aggressive tokenization: splits on non-alphanumeric (e.g., "2D-Materials" -> "2d", "materials")
    text_words = re.findall(r'[a-zA-Z0-9]+', text.lower()) 

    if DEBUG_MODE and filename:
        print(f"\n{Fore.MAGENTA}[DEBUG] File: {filename}")
        print(f"[DEBUG] First 20 tokens: {text_words[:20]}")

    # Parse query components (Mandatory vs Forbidden)
    if " NOT " in query_expansion:
        parts = query_expansion.split(" NOT ")
        must_have_str = parts[0]
        forbidden_str = parts[1]
    else:
        must_have_str = query_expansion
        forbidden_str = ""

    # --- IMPLICIT AND HANDLING ---
    # Standard split by explicit " AND "
    raw_must_terms = [t.strip() for t in must_have_str.split(" AND ") if t.strip()]
    must_terms = []
    
    # Post-process to handle space-separated terms without asterisks
    for t in raw_must_terms:
        # Preserve exact phrases wrapped in asterisks
        if t.startswith("*") and t.endswith("*"):
            must_terms.append(t)
        # Treat spaces in non-asterisk strings as implicit ANDs
        # e.g., "materials 2d" -> required ["materials", "2d"]
        elif " " in t:
            sub_terms = t.split()
            must_terms.extend(sub_terms)
            if DEBUG_MODE and filename:
                print(f"{Fore.CYAN}[DEBUG] Resolved implicit AND: '{t}' -> {sub_terms}")
        else:
            must_terms.append(t)
    
    forbidden_terms = [t.strip() for t in forbidden_str.split() if t.strip()]

    # 1. Check Forbidden Terms (Immediate Veto)
    for term in forbidden_terms:
        clean = term.strip("*").lower()
        if clean in text.lower():
            if DEBUG_MODE: print(f"{Fore.RED}[DEBUG] Vetoed by forbidden term: {clean}")
            return 0 

    # 2. Check Mandatory Terms & Collect Indices
    term_positions = {}
    missing_terms = []
    
    for term in must_terms:
        indices = find_term_indices(text_words, term)
        if not indices:
            missing_terms.append(term)
        else:
            term_positions[term] = indices

    # 3. Base Scoring (Coverage)
    if missing_terms:
        if DEBUG_MODE: print(f"{Fore.YELLOW}[DEBUG] Missing Terms: {missing_terms}")
        
        # If all terms are missing, score is 0
        if len(missing_terms) == len(must_terms):
            return 0 
        
        # Partial match calculation: Proportional score maxing at 40 (Low Relevance)
        found_count = len(must_terms) - len(missing_terms)
        return int((found_count / len(must_terms)) * 40) 

    # If execution reaches here, all mandatory terms are present.
    if DEBUG_MODE: print(f"{Fore.GREEN}[DEBUG] Full term coverage achieved! {list(term_positions.keys())}")
    score = 60 # Baseline for Medium Relevance
    
    # 4. Proximity Bonus (High Relevance Check)
    if len(must_terms) > 1:
        # Flatten and sort all found indices
        all_indices = []
        for term in term_positions:
            all_indices.extend(term_positions[term])
        all_indices.sort()
        
        # Heuristic: Find the minimum distance between any two found terms
        if len(all_indices) > 1:
            min_dist = float('inf')
            for i in range(len(all_indices) - 1):
                dist = all_indices[i+1] - all_indices[i]
                if dist < min_dist:
                    min_dist = dist
            
            # Apply bonus if terms are clustered within the window
            if min_dist <= PROXIMITY_WINDOW:
                score += 50 
                if DEBUG_MODE: print(f"{Fore.CYAN}[DEBUG] Proximity Bonus Applied (Min Dist: {min_dist})")

    return score

def run_content_filter(input_folder, user_query_string):
    """
    Controller function.
    Expands the query, iterates over PDFs, scores them, and sorts into relevance folders.
    """
    try:
        expanded_queries = pq.parse_query(user_query_string)
    except Exception as e:
        print(f"{Fore.RED}❌ Query Parsing Error: {e}")
        return

    # Prepare output directory structure
    base_output = os.path.join("content_filtered", os.path.basename(os.path.normpath(input_folder)))
    dirs = {
        "High": os.path.join(base_output, "High_Relevance"),
        "Medium": os.path.join(base_output, "Medium_Relevance"),
        "Low": os.path.join(base_output, "Low_Relevance")
    }
    
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    print(f"\n{Fore.CYAN}--- Ranked PDF Filter (DEBUG: {DEBUG_MODE}) ---{Style.RESET_ALL}")
    
    # Locate PDFs (Handle standard directory or 'pdfs' subdirectory)
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    if not pdf_files and os.path.exists(os.path.join(input_folder, "pdfs")):
        input_folder = os.path.join(input_folder, "pdfs")
        pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"{Fore.RED}❌ No PDF files found in target directory.")
        return

    stats = {"High": 0, "Medium": 0, "Low": 0, "Rejected": 0}

    # Main Processing Loop
    for i, filename in enumerate(pdf_files):
        pdf_path = os.path.join(input_folder, filename)
        
        full_text = extract_text_from_pdf(pdf_path)
        
        # Reject empty files (scanned images or corrupted)
        if not full_text or len(full_text) < 10:
            if DEBUG_MODE: print(f"{Fore.RED}[DEBUG] Extraction failed/empty for: {filename}")
            stats["Rejected"] += 1
            continue

        # Evaluate against all query expansions and take the best score
        max_score = 0
        for scenario in expanded_queries:
            score = calculate_relevance_score(full_text, scenario, filename)
            if score > max_score:
                max_score = score

        # Categorize
        category = "Rejected"
        if max_score >= SCORE_HIGH_THRESHOLD:
            category = "High"
            color = Fore.GREEN
        elif max_score >= SCORE_MEDIUM_THRESHOLD:
            category = "Medium"
            color = Fore.YELLOW
        elif max_score > 0:
            category = "Low"
            color = Fore.WHITE
        
        # File Operations
        if category != "Rejected":
            shutil.copy2(pdf_path, os.path.join(dirs[category], filename))
            stats[category] += 1
            print(f"{color}✅ {category.upper()}: {filename[:30]}... (Score: {max_score}){Style.RESET_ALL}")
        else:
            stats["Rejected"] += 1

    print(f"\nStats: {stats}")