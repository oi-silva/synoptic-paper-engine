# bibtex_generator.py

import os
import csv
import re
from colorama import Fore, Style, init

init(autoreset=True)

# Files that MUST be ignored to prevent duplication or reading garbage data
IGNORE_FILES = ["output_statistics.csv", "productive_years.csv", "prolific_authors.csv"]
IGNORE_FOLDERS = ["log", "models", "__pycache__"]

def clean_text_for_latex(text):
    """Sanitizes text to avoid breaking LaTeX compilation."""
    if not text: return ""
    # Escape reserved characters
    text = text.replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("_", "\\_")
    text = " ".join(text.split())
    return text

def extract_year_robust(row):
    """Extracts a 4-digit year from any column that looks like a date."""
    val_found = None
    
    # Scan all keys looking for 'year', 'date', 'published'
    for key, value in row.items():
        if not key: continue
        clean_key = key.strip().lower()
        if clean_key in ['year', 'pub_year', 'published', 'date']:
            if value and str(value).strip():
                val_found = str(value).strip()
                break
    
    if not val_found: return "n.d."

    # Regex to catch 19XX or 20XX
    match = re.search(r'(19|20)\d{2}', val_found)
    return match.group(0) if match else "n.d."

def generate_citation_key(authors, year, title):
    """Generates a unique key: SurnameYearFirstWord"""
    try:
        if not authors: authors = "Unknown"
        clean_authors = authors.replace("{", "").replace("}", "").replace("\\", "")
        # Get the first author before comma or 'and'
        first_author_full = re.split(r',| and |;', clean_authors)[0].strip()
        first_author = first_author_full.split(" ")[-1].strip() # Surname
        first_author = re.sub(r'[^a-zA-Z]', '', first_author)
        
        clean_year = str(year).strip()
        if not clean_year.isdigit(): clean_year = "nd"
            
        if not title: title = "Article"
        clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        words = [w for w in clean_title.split() if len(w) > 3 and w.lower() not in ['with', 'from', 'using', 'study', 'analysis']]
        first_word = words[0] if words else "Paper"
        
        return f"{first_author}{clean_year}{first_word.capitalize()}"
    except:
        return f"Unknown{year}Article"

def row_to_bibtex(row):
    """Converts a CSV row into a formatted BibTeX string."""
    # 1. Find Title
    title = None
    for k, v in row.items():
        if k and k.strip().lower() == 'title':
            title = v
            break
            
    if not title or title.lower() == "n/a" or not title.strip():
        return None, None

    # 2. Extract Data
    year = extract_year_robust(row)
    
    authors = "Unknown"
    for k, v in row.items():
        if k and k.strip().lower() == 'authors':
            authors = v
            break

    url = ""
    for k, v in row.items():
        if k and k.strip().lower() in ['url', 'pdf_url', 'link']:
            url = v
            break
    
    journal = None
    for k, v in row.items():
        if k and k.strip().lower() in ['venue', 'journal']:
            journal = v
            break
    
    if not journal:
        if "arxiv.org" in str(url): journal = "arXiv preprint"
        else: journal = "N/A"

    # 3. Generate Key and Entry
    cit_key = generate_citation_key(authors, year, title)
    
    bib_entry = f"@article{{{cit_key},\n"
    bib_entry += f"  title = {{{clean_text_for_latex(title)}}},\n"
    bib_entry += f"  author = {{{clean_text_for_latex(authors)}}},\n"
    bib_entry += f"  year = {{{year}}},\n"
    if journal and journal != "N/A":
        bib_entry += f"  journal = {{{clean_text_for_latex(journal)}}},\n"
    if url:
        bib_entry += f"  url = {{{url}}},\n"
    bib_entry += "}\n"

    unique_id = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
    return unique_id, bib_entry

def get_target_files(mode, selected_folder=None):
    """
    Locates the correct files based on user choice.
    Explicitly ignores the 'log' folder.
    """
    found_files = []
    
    # If a specific folder was selected, look only there (recursively)
    search_roots = [selected_folder] if selected_folder else ["."]
    
    for search_root in search_roots:
        for root, dirs, files in os.walk(search_root):
            # Explicitly block unwanted folders
            if any(ignore in root.split(os.sep) for ignore in IGNORE_FOLDERS):
                continue
            
            for file in files:
                if not file.endswith(".csv"): continue
                if file in IGNORE_FILES: continue

                full_path = os.path.join(root, file)
                parent_folder = os.path.basename(root)

                is_target = False

                # Selection Logic
                if mode == "raw":
                    # Accepts files in results* and arxiv_results*
                    if "arxiv_results" in root or parent_folder.startswith("results"):
                        # Avoid getting processed files if mixed in
                        if "Relevance" not in file and "llama" not in file:
                            is_target = True

                elif mode == "filtered":
                    # Accepts files from Llama or Content Filter (Relevance)
                    if "llama_filtered" in root or "content_filtered" in root:
                        is_target = True
                    # Or loose files with specific suffixes
                    elif file.endswith("_Relevance.csv") or "llama_filtered" in file:
                        is_target = True
                
                if is_target:
                    found_files.append(full_path)
    
    return found_files

def scan_and_generate_bibtex():
    """Main Menu for BibTeX Generator."""
    print(f"\n{Fore.CYAN}---------------- BibTeX Generator Configuration ----------------{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1. Generate from RAW Data (Everything found in 'results' & 'arxiv')")
    print(f"{Fore.YELLOW}2. Generate from FILTERED Data (Only AI/Content filtered papers)")
    
    choice = input(f"\n{Fore.CYAN}Select source type (1 or 2): {Style.RESET_ALL}")
    
    mode = "raw" if choice == "1" else "filtered" if choice == "2" else None
    
    if not mode:
        return

    # List relevant folders to offer as options
    all_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d not in IGNORE_FOLDERS]
    relevant_dirs = []
    
    if mode == "raw":
        relevant_dirs = [d for d in all_dirs if "results" in d or "arxiv" in d]
    else:
        relevant_dirs = [d for d in all_dirs if "filtered" in d]

    print(f"\n{Fore.CYAN}Select specific folder or All:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}0. ALL Folders (Combine everything)")
    for i, d in enumerate(relevant_dirs):
        print(f"{Fore.YELLOW}{i+1}. {d}")

    try:
        sel = int(input(f"\n{Fore.CYAN}Enter your choice: {Style.RESET_ALL}"))
        selected_folder = None
        if sel > 0 and sel <= len(relevant_dirs):
            selected_folder = relevant_dirs[sel-1]
        elif sel != 0:
            print(f"{Fore.RED}Invalid selection.")
            return
    except ValueError:
        print(f"{Fore.RED}Invalid input.")
        return

    # Execute scan
    print(f"\n{Fore.BLUE}🔍 Scanning for CSVs...{Style.RESET_ALL}")
    target_files = get_target_files(mode, selected_folder)

    if not target_files:
        print(f"{Fore.RED}❌ No matching CSV files found.{Style.RESET_ALL}")
        return

    # Processing
    processed_ids = set()
    total_entries = 0
    output_filename = "references_raw.bib" if mode == "raw" else "references_filtered.bib"

    try:
        with open(output_filename, "w", encoding="utf-8") as bib_file:
            bib_file.write(f"% Auto-generated by Synoptic Paper Engine\n")
            bib_file.write(f"% Mode: {mode.upper()}\n")
            
            for file_path in target_files:
                file_entries = [] # Temporary buffer for the current file
                
                try:
                    # Detect encoding (utf-8-sig handles BOM from Excel)
                    with open(file_path, "r", encoding="utf-8-sig") as f:
                        reader = csv.DictReader(f)
                        
                        # Minimal column validation
                        if not reader.fieldnames: continue
                        
                        # Check for title column (case insensitive)
                        has_title = any("title" in h.lower() for h in reader.fieldnames)
                        if not has_title: continue

                        for row in reader:
                            unique_id, bib_entry = row_to_bibtex(row)
                            
                            # Global Deduplication check
                            if unique_id and unique_id not in processed_ids:
                                file_entries.append(bib_entry)
                                processed_ids.add(unique_id)
                                total_entries += 1
                        
                        # Only write the block if this file actually contributed new entries
                        if file_entries:
                            rel_path = os.path.relpath(file_path, ".")
                            
                            # Write visual separator and source filename in BibTeX
                            bib_file.write(f"\n% =========================================\n")
                            bib_file.write(f"% Source: {rel_path}\n")
                            bib_file.write(f"% =========================================\n")
                            
                            for entry in file_entries:
                                bib_file.write(entry + "\n")

                            print(f"{Fore.GREEN}   + Added {len(file_entries)} entries from: {Style.DIM}{rel_path}{Style.RESET_ALL}")

                except Exception as e:
                    print(f"{Fore.RED}   ! Error reading {file_path}: {e}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{Style.BRIGHT}✅ Success!{Style.RESET_ALL}")
        print(f"{Fore.WHITE}File created: {Fore.GREEN}{output_filename}")
        print(f"{Fore.WHITE}Total unique references: {Fore.GREEN}{total_entries}")

    except Exception as e:
         print(f"{Fore.RED}❌ Critical error writing bib file: {e}{Style.RESET_ALL}")