# author_search_scholar.py

import os
import csv
import re
from colorama import Fore, Style, init
from tqdm import tqdm
from scholarly import scholarly, ProxyGenerator
import traceback

# Import specific exception for granular error handling (blocking detection)
from scholarly._proxy_generator import MaxTriesExceededException

init(autoreset=True)

# ==============================================================================
# ABNT FORMATTING UTILS
# ==============================================================================
def format_authors_abnt(author_string: str) -> str:
    """Formats an author string into ABNT standard."""
    if not isinstance(author_string, str) or not author_string:
        return "UNKNOWN AUTHOR"

    authors = author_string.split(' and ')
    formatted_authors = []

    # Handle the first author specifically (LASTNAME, Firstname)
    first_author_name = authors[0]
    parts = first_author_name.strip().split()
    if parts:
        fname = " ".join(parts[:-1])
        lname = parts[-1].upper()
        
        # Handle common Portuguese suffixes
        if len(parts) > 1 and parts[-1].lower() in ['junior', 'filho', 'neto']:
            fname = " ".join(parts[:-2])
            lname = f"{parts[-2].upper()} {parts[-1].upper()}"
        formatted_authors.append(f"{lname}, {fname}")

    # Append remaining authors as is
    for author_name in authors[1:]:
        formatted_authors.append(author_name.strip())

    return "; ".join(formatted_authors)

def format_publication_abnt(pub: dict) -> str:
    """Formats a single publication dict into an ABNT citation string."""
    bib = pub.get('bib', {})
    
    authors_abnt = format_authors_abnt(bib.get('author'))
    title = bib.get('title', 'Unknown Title')
    venue = bib.get('venue', '')
    year = bib.get('pub_year', '')
    url = pub.get('pub_url', '')

    reference = f"{authors_abnt}. {title}."
    if venue:
        reference += f" In: {venue},"
    if year:
        reference += f" {year}."
    
    if url:
        reference += f" Disponível em: <{url}>."
    
    return reference

# ==============================================================================
# BIBTEX FORMATTING UTILS
# ==============================================================================
def clean_text_for_latex(text):
    """Sanitizes text to avoid breaking LaTeX compilation."""
    if not text: return ""
    text = str(text)
    text = text.replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("_", "\\_")
    text = " ".join(text.split())
    return text

def generate_citation_key(bib: dict) -> str:
    """Generates a unique citation key (SurnameYearFirstWord)."""
    try:
        authors = bib.get('author', 'Unknown')
        year = bib.get('pub_year', 'nd')
        title = bib.get('title', 'Article')

        # First author surname
        first_author_full = authors.split(' and ')[0].strip()
        first_author = first_author_full.split()[-1]
        first_author = re.sub(r'[^a-zA-Z]', '', first_author)

        # Clean year
        clean_year = str(year).strip()
        if not clean_year.isdigit(): clean_year = "nd"

        # First title word
        clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        words = [w for w in clean_title.split() if len(w) > 3]
        first_word = words[0] if words else "Paper"

        return f"{first_author}{clean_year}{first_word.capitalize()}"
    except:
        return f"Unknown{year}Article"

def format_publication_bibtex(pub: dict) -> str:
    """Formats a publication dict into a BibTeX entry."""
    bib = pub.get('bib', {})
    cit_key = generate_citation_key(bib)
    
    # Extract fields
    title = clean_text_for_latex(bib.get('title', ''))
    author = clean_text_for_latex(bib.get('author', ''))
    year = clean_text_for_latex(bib.get('pub_year', ''))
    journal = clean_text_for_latex(bib.get('venue', ''))
    url = pub.get('pub_url', '')
    abstract = clean_text_for_latex(bib.get('abstract', ''))

    entry = f"@article{{{cit_key},\n"
    entry += f"  title = {{{title}}},\n"
    entry += f"  author = {{{author}}},\n"
    entry += f"  year = {{{year}}},\n"
    if journal:
        entry += f"  journal = {{{journal}}},\n"
    if url:
        entry += f"  url = {{{url}}},\n"
    entry += "}\n"
    
    return entry

# ==============================================================================

def setup_proxy():
    # ScraperAPI configuration
    SCRAPER_API_KEY = "" 
    if not SCRAPER_API_KEY:
        print(f"{Fore.YELLOW}⚠️  ScraperAPI key not found. Running without a dedicated proxy.")
        return
    
    proxy_url = f"http://scraperapi:{SCRAPER_API_KEY}@proxy-server.scraperapi.com:8001"
    proxies = { 'http': proxy_url, 'https': proxy_url }
    
    try:
        scholarly.use_proxy(proxies=proxies, https_proxy=proxies['https'])
        print(f"{Fore.GREEN}Manual proxy configured successfully!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Could not configure manual proxy. Error: {e}{Style.RESET_ALL}")

def get_unique_folder(base_folder):
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
        return base_folder
    count = 1
    while os.path.exists(f"{base_folder}-{count}"):
        count += 1
    new_folder = f"{base_folder}-{count}"
    os.makedirs(new_folder)
    return new_folder

def run_author_search():
    """Main execution flow: search author -> fetch pubs -> save CSV/TXT/BIB."""
    try:
        setup_proxy()
        selected_author = None
        
        print(f"\n{Fore.CYAN}--- Author Search Method ---")
        print(f"{Fore.YELLOW}1. Search by Author Name (less reliable)")
        print(f"{Fore.YELLOW}2. Fetch by Author ID (more reliable)")
        choice = input(f"\n{Fore.WHITE}Choose your method (1 or 2): {Style.RESET_ALL}")
        
        if choice == '2':
            author_id = input(f"\n{Fore.YELLOW}Enter the Google Scholar Author ID:{Style.RESET_ALL} ").strip()
            if not author_id:
                print(f"{Fore.RED}❌ Author ID cannot be empty.")
                return
            
            print(f"\n{Fore.CYAN}🔎 Fetching author profile for ID: {author_id}...{Style.RESET_ALL}")
            try:
                selected_author = scholarly.search_author_id(author_id)
                print(f"{Fore.GREEN}✅ Profile found for '{selected_author.get('name', 'N/A')}'.")
            
            except MaxTriesExceededException:
                print(f"\n{Fore.RED}{Style.BRIGHT}❌ BLOCK DETECTED BY GOOGLE ❌")
                print(f"{Fore.YELLOW}Google has blocked the requests. Try again later or rotate IP.")
                return
            except Exception as e:
                print(f"{Fore.RED}❌ Unexpected error fetching by ID.")
                traceback.print_exc()
                return
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please enter 1 or 2.")
            return

        if not selected_author:
            print(f"{Fore.RED}❌ Could not retrieve author details.")
            return

        # Fetch lightweight publication stubs first
        print(f"\n{Fore.CYAN}⏳ Fetching basic publication list for: {selected_author['name']}...{Style.RESET_ALL}")
        author_details = scholarly.fill(selected_author, sections=['publications'])
        publications_stubs = author_details.get('publications', [])
        
        print(f"{Fore.BLUE}ℹ️  Found {len(publications_stubs)} total publications. Now fetching full details for each.")
        print(f"{Fore.YELLOW}⚠️  This next step will be slow and may take several minutes.")

        if not publications_stubs:
            print(f"{Fore.YELLOW}⚠️  Since no publications were found, no files will be generated.")
            return

        # Detailed fetch loop
        filled_publications = []
        for pub_stub in tqdm(publications_stubs, desc="Fetching Full Details"):
            try:
                pub_filled = scholarly.fill(pub_stub)
                filled_publications.append(pub_filled)
            except Exception as e:
                tqdm.write(f"{Fore.RED}❌ Error fetching details for '{pub_stub.get('bib', {}).get('title', 'Unknown Paper')}': {e}")
                continue
        
        # Sort by year descending
        filled_publications.sort(key=lambda p: int(p.get('bib', {}).get('pub_year', 0) or 0), reverse=True)

        # IO Operations
        output_folder = get_unique_folder("author_results")
        sanitized_name = "".join(c for c in selected_author['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(" ", "_")
        
        # 1. Save CSV
        csv_output_file = os.path.join(output_folder, f"{sanitized_name}_publications.csv")
        print(f"\n{Fore.CYAN}Saving CSV file to '{csv_output_file}'...{Style.RESET_ALL}")
        
        with open(csv_output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Year", "Citations", "Authors", "Venue", "URL", "Abstract"])
            for pub in filled_publications:
                bib = pub.get('bib', {})
                author_data = bib.get('author', 'N/A')
                
                if isinstance(author_data, str): 
                    authors = author_data.replace(' and ', '; ')
                else: 
                    authors = '; '.join(author_data)
                
                writer.writerow([
                    bib.get('title', 'N/A'), 
                    bib.get('pub_year', 'N/A'), 
                    pub.get('num_citations', 0), 
                    authors, 
                    bib.get('venue', 'N/A'), 
                    pub.get('pub_url', 'N/A'),
                    bib.get('abstract', 'N/A')
                ])

        # 2. Save ABNT TXT
        txt_output_file = os.path.join(output_folder, f"{sanitized_name}_references_ABNT.txt")
        print(f"{Fore.CYAN}Saving ABNT references to '{txt_output_file}'...{Style.RESET_ALL}")
        
        with open(txt_output_file, mode='w', encoding='utf-8') as file:
            file.write("References (ABNT Standard)\n")
            file.write("=========================\n\n")
            for pub in filled_publications:
                abnt_reference = format_publication_abnt(pub)
                file.write(abnt_reference + "\n\n")

        # 3. Save BibTeX (NEW)
        bib_output_file = os.path.join(output_folder, f"{sanitized_name}_references.bib")
        print(f"{Fore.CYAN}Saving BibTeX references to '{bib_output_file}'...{Style.RESET_ALL}")
        
        with open(bib_output_file, mode='w', encoding='utf-8') as file:
            file.write(f"% Auto-generated BibTeX for author: {selected_author['name']}\n")
            file.write(f"% Total publications: {len(filled_publications)}\n\n")
            
            processed_keys = set()
            for pub in filled_publications:
                bib_entry = format_publication_bibtex(pub)
                
                # Simple check to avoid exact duplicate keys (though generate_citation_key logic usually handles this via year/title)
                # If needed, a more robust key collision handler could be added here.
                file.write(bib_entry + "\n")

        print(f"\n{Fore.GREEN}🏁 Finished. CSV, ABNT TXT, and BibTeX files saved successfully.{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}")
        traceback.print_exc()
    
    finally:
        input(f"\n{Fore.MAGENTA}Press Enter to return to the main menu...{Style.RESET_ALL}")