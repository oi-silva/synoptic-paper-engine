import os
import re
import shutil
import pypdf
import csv
import logging
from colorama import Fore, Style, init
from tqdm import tqdm
from . import parse_query as pq
from . import cross_validator as cv

init(autoreset=True)

logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)

# =================CONFIGURATION=================
DEBUG_MODE = False  
PROXIMITY_WINDOW = 50  
SCORE_HIGH_THRESHOLD = 100
SCORE_MEDIUM_THRESHOLD = 50
# ===============================================

def extract_text_from_pdf(pdf_path):
    """Extracts raw text content from a PDF file."""
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
    """Locates indices of a specific term within the tokenized text."""
    indices = []
    # Logic 1: Exact Phrase Matching (*term*)
    if term.startswith("*") and term.endswith("*"):
        clean_phrase = term.strip("*").lower()
        phrase_words = clean_phrase.split()
        if not phrase_words: return []
        first_word = phrase_words[0]
        phrase_len = len(phrase_words)
        for i, word in enumerate(text_words):
            if word == first_word:
                if text_words[i:i+phrase_len] == phrase_words:
                    indices.append(i)
    # Logic 2: Loose Token Matching
    else:
        clean_term = term.lower()
        for i, word in enumerate(text_words):
            if clean_term in word: 
                indices.append(i)
    return indices

def calculate_relevance_score(text, query_expansion, filename=""):
    """Computes a relevance score based on term presence and proximity."""
    text_words = re.findall(r'[a-zA-Z0-9]+', text.lower()) 

    if " NOT " in query_expansion:
        parts = query_expansion.split(" NOT ")
        must_have_str = parts[0]
        forbidden_str = parts[1]
    else:
        must_have_str = query_expansion
        forbidden_str = ""

    # Implicit AND handling
    raw_must_terms = [t.strip() for t in must_have_str.split(" AND ") if t.strip()]
    must_terms = []
    for t in raw_must_terms:
        if t.startswith("*") and t.endswith("*"):
            must_terms.append(t)
        elif " " in t:
            must_terms.extend(t.split())
        else:
            must_terms.append(t)
    
    forbidden_terms = [t.strip() for t in forbidden_str.split() if t.strip()]

    # 1. Check Forbidden
    for term in forbidden_terms:
        clean = term.strip("*").lower()
        if clean in text.lower():
            return 0 

    # 2. Check Mandatory
    term_positions = {}
    missing_terms = []
    for term in must_terms:
        indices = find_term_indices(text_words, term)
        if not indices:
            missing_terms.append(term)
        else:
            term_positions[term] = indices

    # 3. Base Scoring
    if missing_terms:
        if len(missing_terms) == len(must_terms): return 0 
        found_count = len(must_terms) - len(missing_terms)
        return int((found_count / len(must_terms)) * 40) 

    score = 60 # Baseline Medium
    
    # 4. Proximity Bonus
    if len(must_terms) > 1:
        all_indices = []
        for term in term_positions:
            all_indices.extend(term_positions[term])
        all_indices.sort()
        
        if len(all_indices) > 1:
            min_dist = float('inf')
            for i in range(len(all_indices) - 1):
                dist = all_indices[i+1] - all_indices[i]
                if dist < min_dist:
                    min_dist = dist
            if min_dist <= PROXIMITY_WINDOW:
                score += 50 

    return score

def display_stats(stats):
    """Displays filtering statistics in a clean, list-based format."""
    total = sum(stats.values())
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Filtering Summary ==={Style.RESET_ALL}")
    print(f"   {Fore.GREEN}• High Relevance   : {stats['High']:>4}")
    print(f"   {Fore.YELLOW}• Medium Relevance : {stats['Medium']:>4}")
    print(f"   {Fore.WHITE}• Low Relevance    : {stats['Low']:>4}")
    print(f"   {Fore.RED}• Rejected         : {stats['Rejected']:>4}")
    print(f"   {Fore.CYAN}--------------------------")
    print(f"   {Style.BRIGHT}Total Processed    : {total:>4}{Style.RESET_ALL}")

def run_csv_content_filter(input_folder, user_query_string):
    """
    Filters rows in CSV files based on Title + Abstract content.
    """
    try:
        expanded_queries = pq.parse_query(user_query_string)
    except Exception as e:
        print(f"{Fore.RED}❌ Query Parsing Error: {e}")
        return

    # Output setup
    base_output = os.path.join("content_filtered_csv", os.path.basename(os.path.normpath(input_folder)))
    os.makedirs(base_output, exist_ok=True)
    
    csv_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.csv')]
    if not csv_files:
        print(f"{Fore.RED}❌ No CSV files found in target directory.")
        return

    print(f"\n{Fore.CYAN}--- CSV Content Filter (Abstract Analysis) ---{Style.RESET_ALL}")
    
    # Pre-count total rows for progress bar
    print(f"{Fore.YELLOW}📊 Calculating workload...{Style.RESET_ALL}")
    total_rows = 0
    for filename in csv_files:
        try:
            with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
                # Count lines minus header
                total_rows += sum(1 for _ in f) - 1
        except: pass

    stats = {"High": 0, "Medium": 0, "Low": 0, "Rejected": 0}
    
    # Prepare output files
    out_files = {
        "High": open(os.path.join(base_output, "High_Relevance.csv"), 'w', newline='', encoding='utf-8'),
        "Medium": open(os.path.join(base_output, "Medium_Relevance.csv"), 'w', newline='', encoding='utf-8'),
        "Low": open(os.path.join(base_output, "Low_Relevance.csv"), 'w', newline='', encoding='utf-8')
    }
    
    writers = {}
    headers_written = {"High": False, "Medium": False, "Low": False}

    # Initialize Progress Bar
    with tqdm(total=total_rows, desc="Filtering Content", unit="paper", colour="green") as pbar:
        for filename in csv_files:
            filepath = os.path.join(input_folder, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    
                    if not fieldnames: continue

                    out_fieldnames = fieldnames + ["Relevance_Score"]

                    for row in reader:
                        title = row.get("Title", row.get("title", ""))
                        abstract = row.get("Abstract", row.get("abstract", row.get("summary", "")))
                        
                        full_text = f"{title} . {abstract}"
                        
                        if len(full_text) < 10:
                            stats["Rejected"] += 1
                            pbar.update(1)
                            continue

                        max_score = 0
                        for scenario in expanded_queries:
                            score = calculate_relevance_score(full_text, scenario)
                            if score > max_score:
                                max_score = score

                        category = "Rejected"
                        if max_score >= SCORE_HIGH_THRESHOLD:
                            category = "High"
                        elif max_score >= SCORE_MEDIUM_THRESHOLD:
                            category = "Medium"
                        elif max_score > 0:
                            category = "Low"

                        if category != "Rejected":
                            row["Relevance_Score"] = max_score
                            
                            if not headers_written[category]:
                                writers[category] = csv.DictWriter(out_files[category], fieldnames=out_fieldnames)
                                writers[category].writeheader()
                                headers_written[category] = True
                            
                            writers[category].writerow(row)
                            stats[category] += 1
                        else:
                            stats["Rejected"] += 1
                        
                        # Update progress & stats
                        pbar.update(1)
                        pbar.set_postfix(High=stats['High'], Med=stats['Medium'])

                except Exception as e:
                    pbar.write(f"{Fore.RED}Error reading {filename}: {e}")

    for f in out_files.values():
        f.close()

    # Cleanup empty files
    for cat, count in stats.items():
        if cat != "Rejected" and count == 0:
            file_to_remove = os.path.join(base_output, f"{cat}_Relevance.csv")
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)

    display_stats(stats)
    print(f"\n{Fore.CYAN}Results saved in: {base_output}{Style.RESET_ALL}")

    # --- CROSS VALIDATION STEP ---
    cv.save_metadata(base_output, input_folder, filter_type="REGEX")
    cv.run_comparison(base_output, current_filter_type="REGEX")

def run_content_filter(input_folder, user_query_string):
    """
    Controller function for PDFs.
    Now generates both Folders (with copies) AND CSV logs.
    """
    # Save the original path for the Cross-Validator
    original_input_folder = input_folder

    try:
        expanded_queries = pq.parse_query(user_query_string)
    except Exception as e:
        print(f"{Fore.RED}❌ Query Parsing Error: {e}")
        return

    base_output = os.path.join("content_filtered", os.path.basename(os.path.normpath(input_folder)))
    dirs = {
        "High": os.path.join(base_output, "High_Relevance"),
        "Medium": os.path.join(base_output, "Medium_Relevance"),
        "Low": os.path.join(base_output, "Low_Relevance")
    }
    
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    print(f"\n{Fore.CYAN}--- Ranked PDF Filter ---{Style.RESET_ALL}")
    
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    if not pdf_files and os.path.exists(os.path.join(input_folder, "pdfs")):
        input_folder = os.path.join(input_folder, "pdfs")
        pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"{Fore.RED}❌ No PDF files found in target directory.")
        return

    stats = {"High": 0, "Medium": 0, "Low": 0, "Rejected": 0}

    # --- CSV WRITERS SETUP (NEW) ---
    out_files = {
        "High": open(os.path.join(base_output, "High_Relevance.csv"), 'w', newline='', encoding='utf-8'),
        "Medium": open(os.path.join(base_output, "Medium_Relevance.csv"), 'w', newline='', encoding='utf-8'),
        "Low": open(os.path.join(base_output, "Low_Relevance.csv"), 'w', newline='', encoding='utf-8')
    }
    writers = {}
    headers_written = {"High": False, "Medium": False, "Low": False}
    # We map 'Filename' to 'Title' so CrossValidator works automatically
    csv_fieldnames = ["Title", "Relevance_Score", "Original_Path"] 

    # --- PROGRESS BAR ---
    with tqdm(total=len(pdf_files), desc="Scanning PDFs", unit="pdf", colour="green") as pbar:
        for i, filename in enumerate(pdf_files):
            pdf_path = os.path.join(input_folder, filename)
            full_text = extract_text_from_pdf(pdf_path)
            
            if not full_text or len(full_text) < 10:
                stats["Rejected"] += 1
                pbar.update(1)
                continue

            max_score = 0
            for scenario in expanded_queries:
                score = calculate_relevance_score(full_text, scenario, filename)
                if score > max_score:
                    max_score = score

            category = "Rejected"
            if max_score >= SCORE_HIGH_THRESHOLD:
                category = "High"
            elif max_score >= SCORE_MEDIUM_THRESHOLD:
                category = "Medium"
            elif max_score > 0:
                category = "Low"
            
            if category != "Rejected":
                # 1. Copy File
                shutil.copy2(pdf_path, os.path.join(dirs[category], filename))
                
                # 2. Write to CSV (NEW)
                if not headers_written[category]:
                    writers[category] = csv.DictWriter(out_files[category], fieldnames=csv_fieldnames)
                    writers[category].writeheader()
                    headers_written[category] = True
                
                # We strip .pdf from Title for cleaner CSVs, though not strictly required
                clean_title = os.path.splitext(filename)[0]
                writers[category].writerow({
                    "Title": clean_title,
                    "Relevance_Score": max_score,
                    "Original_Path": pdf_path
                })

                stats[category] += 1
            else:
                stats["Rejected"] += 1
            
            pbar.update(1)
            pbar.set_postfix(High=stats['High'], Med=stats['Medium'])

    # Close CSVs
    for f in out_files.values():
        f.close()

    # Cleanup empty CSVs
    for cat, count in stats.items():
        if cat != "Rejected" and count == 0:
            file_to_remove = os.path.join(base_output, f"{cat}_Relevance.csv")
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)

    display_stats(stats)
    print(f"\n{Fore.CYAN}Results saved in: {base_output}{Style.RESET_ALL}")

    # --- CROSS VALIDATION STEP ---
    cv.save_metadata(base_output, original_input_folder, filter_type="REGEX")
    cv.run_comparison(base_output, current_filter_type="REGEX")