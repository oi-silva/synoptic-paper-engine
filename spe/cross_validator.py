# cross_validator.py

import os
import json
import hashlib
import csv
import re
from colorama import Fore, Style, init

init(autoreset=True)

META_FILENAME = ".dataset_identity.json"

def normalize_title(title):
    """Normalizes title for consistent hashing and comparison."""
    if not title: return ""
    # Remove non-alphanumeric chars and lowercase
    return re.sub(r'[^a-z0-9]', '', title.lower())

def generate_fingerprint(input_folder):
    """
    Creates a unique Hash based on article titles in the INPUT folder.
    Ensures 'results-1' and 'copy-of-results-1' share identity.
    """
    titles = []
    
    # Scan CSVs in input folder (source of truth)
    if os.path.exists(input_folder):
        for f in os.listdir(input_folder):
            # Ignore stats files, process only data CSVs
            if f.endswith(".csv") and not f.startswith("output_statistics"):
                try:
                    with open(os.path.join(input_folder, f), 'r', encoding='utf-8-sig') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            t = row.get("Title") or row.get("title")
                            if t: titles.append(normalize_title(t))
                except:
                    pass
    
    # Sort to ensure file order doesn't affect hash
    titles.sort()
    content_string = "".join(titles)
    
    # Return MD5 hash
    return hashlib.md5(content_string.encode('utf-8')).hexdigest()

def save_metadata(output_folder, input_folder_path, filter_type):
    """Saves dataset identity metadata to the OUTPUT folder."""
    try:
        fingerprint = generate_fingerprint(input_folder_path)
        
        data = {
            "source_fingerprint": fingerprint,
            "filter_type": filter_type, # 'AI' or 'REGEX'
            "source_path": input_folder_path
        }
        
        with open(os.path.join(output_folder, META_FILENAME), 'w') as f:
            json.dump(data, f)
            
        return fingerprint
    except Exception as e:
        print(f"{Fore.RED}[Validator Error] Could not save metadata: {e}")
        return None

def get_approved_titles(folder_path, filter_type):
    """
    Extracts the set of APPROVED titles from a result folder.
    """
    approved = set()
    
    # Logic for AI results
    if filter_type == "AI":
        csv_path = os.path.join(folder_path, "llama_filtered_articles.csv")
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # AI only approves if Decision is YES
                    if row.get("AI_Decision", "").upper() == "YES":
                        approved.add(normalize_title(row.get("Title")))

    # Logic for Regex results
    elif filter_type == "REGEX":
        # Check for CSV files (Both PDF Filter and Metadata Filter now produce these)
        has_csvs = False
        for name in ["High_Relevance.csv", "Medium_Relevance.csv"]:
            csv_path = os.path.join(folder_path, name)
            if os.path.exists(csv_path):
                has_csvs = True
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        approved.add(normalize_title(row.get("Title") or row.get("title")))
        
        # Fallback: Check for Directories (Legacy PDF Filter support)
        if not has_csvs:
            for category in ["High_Relevance", "Medium_Relevance"]:
                dir_path = os.path.join(folder_path, category)
                if os.path.isdir(dir_path):
                    for filename in os.listdir(dir_path):
                        if filename.lower().endswith(".pdf"):
                            # Remove .pdf extension
                            raw_title = os.path.splitext(filename)[0]
                            approved.add(normalize_title(raw_title))
    
    return approved

def run_comparison(current_output_folder, current_filter_type):
    """
    Main function called by filters.
    Checks for a sibling result from the other method and compares.
    """
    print(f"\n{Fore.CYAN}-------------------- Cross-Validation Check --------------------{Style.RESET_ALL}")
    
    # 1. Read current fingerprint
    try:
        with open(os.path.join(current_output_folder, META_FILENAME), 'r') as f:
            current_meta = json.load(f)
    except:
        print(f"{Fore.YELLOW}⚠️  Could not read validation metadata. Skipping comparison.")
        return

    current_fingerprint = current_meta['source_fingerprint']
    target_type = "REGEX" if current_filter_type == "AI" else "AI"
    
    print(f"{Fore.BLUE}🔍 Checking if {target_type} filter was already run on this dataset...{Style.RESET_ALL}")

    match_folder = None
    candidate_paths = []

    # 2. Locate Candidate Folders
    if target_type == "AI":
        # AI folders are stored in root (e.g. llama_filtered*)
        for d in os.listdir('.'):
            if d.startswith("llama_filtered") and os.path.isdir(d):
                candidate_paths.append(d)

    elif target_type == "REGEX":
        # Regex folders are stored inside "content_filtered" (PDFs) or "content_filtered_csv" (CSVs)
        # We check BOTH base directories
        base_dirs = ["content_filtered", "content_filtered_csv"]
        for base in base_dirs:
            if os.path.exists(base):
                for d in os.listdir(base):
                    full_path = os.path.join(base, d)
                    if os.path.isdir(full_path):
                        candidate_paths.append(full_path)

    # 3. Check Candidates for Matching Fingerprint
    for path in candidate_paths:
        meta_path = os.path.join(path, META_FILENAME)
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    candidate_meta = json.load(f)
                
                if candidate_meta.get('source_fingerprint') == current_fingerprint:
                    match_folder = path
                    break
            except:
                continue

    if not match_folder:
        print(f"{Fore.YELLOW}ℹ️  No previous {target_type} run found for this dataset.{Style.RESET_ALL}")
        return

    # 4. Execute Comparison
    print(f"{Fore.GREEN}✅ Match Found! Comparing with: {match_folder}{Style.RESET_ALL}")
    
    titles_current = get_approved_titles(current_output_folder, current_filter_type)
    titles_target = get_approved_titles(match_folder, target_type)
    
    # Set Operations
    agreement = titles_current.intersection(titles_target)
    only_current = titles_current.difference(titles_target)
    only_target = titles_target.difference(titles_current)
    
    # Display Report
    print(f"\n{Fore.WHITE}{Style.BRIGHT}📊 Comparison Report ({current_filter_type} vs {target_type}){Style.RESET_ALL}")
    print(f"   • Total Approved by {current_filter_type:<6}: {len(titles_current)}")
    print(f"   • Total Approved by {target_type:<6}: {len(titles_target)}")
    print(f"   ---------------------------------")
    print(f"   • {Fore.GREEN}AGREEMENT (Both Approved) : {len(agreement)}{Style.RESET_ALL}")
    print(f"   • {Fore.YELLOW}Unique to {current_filter_type:<14}  : {len(only_current)}{Style.RESET_ALL}")
    print(f"   • {Fore.MAGENTA}Unique to {target_type:<14}  : {len(only_target)}{Style.RESET_ALL}")

    # Save report to text file
    report_path = os.path.join(current_output_folder, "comparison_report.txt")
    with open(report_path, "w") as f:
        f.write(f"Comparison Report: {current_filter_type} (Current) vs {target_type}\n")
        f.write("=================================================\n")
        f.write(f"Dataset Identity (Hash): {current_fingerprint}\n\n")
        f.write(f"Agreement Count: {len(agreement)}\n")
        f.write(f"Only in {current_filter_type}: {len(only_current)}\n")
        f.write(f"Only in {target_type}: {len(only_target)}\n")
    
    print(f"\n{Fore.CYAN}📄 Detailed report saved to:\n  {report_path}{Style.RESET_ALL}")