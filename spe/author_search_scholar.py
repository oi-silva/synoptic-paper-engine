# author_search_scholar.py

import os
import csv
from colorama import Fore, Style, init
from tqdm import tqdm
from scholarly import scholarly, ProxyGenerator
import traceback

# Importamos a exceção específica para poder capturá-la
from scholarly._proxy_generator import MaxTriesExceededException

init(autoreset=True)

# ==============================================================================
# FUNÇÕES DE FORMATAÇÃO ABNT (COM A MELHORIA)
# ==============================================================================
def format_authors_abnt(author_string: str) -> str:
    """Formata uma string de autores no padrão ABNT."""
    if not isinstance(author_string, str) or not author_string:
        return "AUTORIA DESCONHECIDA"

    authors = author_string.split(' and ')
    formatted_authors = []

    first_author_name = authors[0]
    parts = first_author_name.strip().split()
    if parts:
        fname = " ".join(parts[:-1])
        lname = parts[-1].upper()
        if len(parts) > 1 and parts[-1].lower() in ['junior', 'filho', 'neto']:
            fname = " ".join(parts[:-2])
            lname = f"{parts[-2].upper()} {parts[-1].upper()}"
        formatted_authors.append(f"{lname}, {fname}")

    for author_name in authors[1:]:
        formatted_authors.append(author_name.strip())

    return "; ".join(formatted_authors)

def format_publication_abnt(pub: dict) -> str:
    """Formata uma única publicação no padrão ABNT, incluindo o link."""
    bib = pub.get('bib', {})
    
    authors_abnt = format_authors_abnt(bib.get('author'))
    title = bib.get('title', 'Título desconhecido')
    venue = bib.get('venue', '')
    year = bib.get('pub_year', '')
    url = pub.get('pub_url', '') # Pega o URL da publicação

    # Monta a referência base
    reference = f"{authors_abnt}. {title}."
    if venue:
        reference += f" In: {venue},"
    if year:
        reference += f" {year}."
    
    # --- ALTERAÇÃO AQUI: Adiciona o link no final, se existir ---
    if url:
        reference += f" Disponível em: <{url}>."
    
    return reference

# ==============================================================================

def setup_proxy():
    # ... (código da função setup_proxy inalterado) ...
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
    # ... (código da função get_unique_folder inalterado) ...
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
    """Função principal para buscar um autor e salvar suas publicações."""
    try:
        setup_proxy()
        selected_author = None
        # ... (lógica para escolher busca por ID ou nome inalterada) ...
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
                print(f"\n{Fore.RED}{Style.BRIGHT}❌ BLOQUEIO DETECTADO PELO GOOGLE ❌")
                print(f"{Fore.YELLOW}O Google bloqueou as requisições. Tente novamente mais tarde.")
                return
            except Exception as e:
                print(f"{Fore.RED}❌ Ocorreu um erro inesperado ao buscar pelo ID.")
                traceback.print_exc()
                return
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please enter 1 or 2.")
            return

        if not selected_author:
            print(f"{Fore.RED}❌ Could not retrieve author details.")
            return

        print(f"\n{Fore.CYAN}⏳ Fetching basic publication list for: {selected_author['name']}...{Style.RESET_ALL}")
        author_details = scholarly.fill(selected_author, sections=['publications'])
        publications_stubs = author_details.get('publications', [])
        
        print(f"{Fore.BLUE}ℹ️  Found {len(publications_stubs)} total publications. Now fetching full details for each.")
        print(f"{Fore.YELLOW}⚠️  This next step will be slow and may take several minutes.")

        if not publications_stubs:
            print(f"{Fore.YELLOW}⚠️  Since no publications were found, no files will be generated.")
            return

        filled_publications = []
        for pub_stub in tqdm(publications_stubs, desc="Fetching Full Details"):
            try:
                pub_filled = scholarly.fill(pub_stub)
                filled_publications.append(pub_filled)
            except Exception as e:
                tqdm.write(f"{Fore.RED}❌ Error fetching details for '{pub_stub.get('bib', {}).get('title', 'Unknown Paper')}': {e}")
                continue
        
        filled_publications.sort(key=lambda p: int(p.get('bib', {}).get('pub_year', 0)), reverse=True)

        output_folder = get_unique_folder("author_results")
        sanitized_name = "".join(c for c in selected_author['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(" ", "_")
        
        csv_output_file = os.path.join(output_folder, f"{sanitized_name}_publications.csv")
        print(f"\n{Fore.CYAN}Saving CSV file to '{csv_output_file}'...{Style.RESET_ALL}")
        with open(csv_output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Year", "Citations", "Authors", "Venue", "URL"])
            for pub in filled_publications:
                bib = pub.get('bib', {})
                author_data = bib.get('author', 'N/A')
                if isinstance(author_data, str): authors = author_data.replace(' and ', '; ')
                else: authors = '; '.join(author_data)
                writer.writerow([bib.get('title', 'N/A'), bib.get('pub_year', 'N/A'), pub.get('num_citations', 0), authors, bib.get('venue', 'N/A'), pub.get('pub_url', 'N/A')])

        txt_output_file = os.path.join(output_folder, f"{sanitized_name}_references_ABNT.txt")
        print(f"{Fore.CYAN}Saving ABNT references to '{txt_output_file}'...{Style.RESET_ALL}")
        with open(txt_output_file, mode='w', encoding='utf-8') as file:
            file.write("Referências (Norma ABNT)\n")
            file.write("=========================\n\n")
            for pub in filled_publications:
                abnt_reference = format_publication_abnt(pub)
                file.write(abnt_reference + "\n\n")

        print(f"\n{Fore.GREEN}🏁 Finished. Both CSV and ABNT TXT files saved successfully.{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}")
    
    finally:
        input(f"\n{Fore.MAGENTA}Press Enter to return to the main menu...{Style.RESET_ALL}")