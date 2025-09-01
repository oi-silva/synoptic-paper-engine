# find_papers.py

import requests
import parse_query as pq
import preview_step as ps
import time
import csv
import sys
import os
from colorama import init, Fore, Style
import help_menu as hm
import statistics_analyzer as sa

# Initializes colorama
init(autoreset=True)

# ======================= Configuration =======================
APP_NAME = "Synoptic Paper Engine"
USER_AGENT = "Synoptic-Paper-Engine/1.0"
API_KEY = None  # If you have an API key, place it here
FIELDS = "title,authors,year,citationCount,url,abstract"


def display_banner():
    """Displays a welcome banner with the tool's name and description."""
    
    banner_art = r"""
                 ██████╗ ██████╗  ███████╗
                 ██╔═══╝ ██╔══██╗ ██╔════╝
                 ██████╗ ██████╔╝ ███████╗
                 ╚═══██║ ██╔═══╝  ██╔════╝
                 ██████║ ██║      ███████║
                 ╚═════╝ ╚═╝      ╚══════╝
"""
    
    # banner_lines = banner_art.strip('\n').split('\n')
    # max_banner_width = max(len(line) for line in banner_lines) if banner_lines else 80

    tool_name = "Synoptic Paper Engine\n"
    desc_lines = [
       "This script is an automated tool for searching and filtering",
        "academic papers using the Semantic Scholar API. It supports",
         " complex queries, citation and year filters, and generates",
                            "organized CSV outputs."
    ]

    banner_lines = desc_lines[0].strip('\n').split('\n')
    max_banner_width = max(len(line) for line in banner_lines) if banner_lines else 80

    # Imprime a arte e o título em CIANO
    print(f"{Fore.CYAN}{Style.BRIGHT}{banner_art}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{tool_name.center(max_banner_width)}{Style.RESET_ALL}")
    
    # Imprime a descrição em BRANCO
    for line in desc_lines:
        print(f"{Fore.WHITE}{line.center(max_banner_width)}{Style.RESET_ALL}")
    
    # Separador final em CIANO
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * max_banner_width}{Style.RESET_ALL}\n")

def get_with_backoff(url, headers, max_retries=5):
    """Performs an HTTP GET request with exponential backoff for rate limiting."""
    delay = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                print(f"{Fore.YELLOW}⚠️  Error 429: Too many requests. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"{Fore.RED}❌ Request error: Code {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Connection error: {e}")
            time.sleep(delay)
            delay *= 2
    print(f"{Fore.RED}❌ Request failed after {max_retries} attempts.")
    return None

def run_bibliographic_search():
    """Main function to run the user interface and the search process."""
    while True:
        query_str = input(f"{Fore.YELLOW}Enter your query {Style.DIM}('help' for guidance):{Style.RESET_ALL}\n> ")
        if query_str.strip().lower() in ["help", "?"]:
            hm.show_autosearch_help()
            continue
        if not query_str.strip():
            print(f"{Fore.RED}❌ Query cannot be empty. Exiting.")
            sys.exit(1)
        break

    try:
        queries = pq.parse_query(query_str)
    except Exception as e:
        print(f"{Fore.RED}❌ Error parsing the query: {e}")
        sys.exit(1)

    use_citation_filter = input(f"\n{Fore.YELLOW}Do you want to set a minimum number of citations? (y/n): ").lower()
    min_citations = 0
    if use_citation_filter == "y":
        try:
            min_citations = int(input(f"{Fore.GREEN}Enter minimum number of citations:{Style.RESET_ALL} "))
        except ValueError:
            print(f"{Fore.YELLOW}⚠️ Invalid input. Using default = 0")

    min_year, max_year = None, None
    use_year_filter = input(f"{Fore.YELLOW}Do you want to filter by year? (y/n): ").lower()
    if use_year_filter == "y":
        try:
            min_year_input = input(f"{Fore.GREEN}Enter minimum year (Press Enter to skip):{Style.RESET_ALL} ")
            min_year = int(min_year_input) if min_year_input.strip() else None
            max_year_input = input(f"{Fore.GREEN}Enter maximum year (Press Enter to skip):{Style.RESET_ALL} ")
            max_year = int(max_year_input) if max_year_input.strip() else None
        except ValueError:
            print(f"{Fore.YELLOW}⚠️ Invalid input. No year filter will be applied.")

    try:
        batch_size = int(input(f"\n{Fore.MAGENTA}Enter batch size {Style.DIM}(default = 100, max = 100):{Style.RESET_ALL} ") or 100)
        if batch_size > 100:
            print(f"{Fore.YELLOW}⚠️ Batch size cannot exceed 100. Using 100.")
            batch_size = 100
    except ValueError:
        batch_size = 100

    try:
        max_batches = int(input(f"{Fore.MAGENTA}Enter number of batches {Style.DIM}(default = 10):{Style.RESET_ALL} ") or 10)
    except ValueError:
        max_batches = 10

    print(f"\n{Fore.LIGHTBLUE_EX}--- Search Summary ---")
    print(f"{Fore.LIGHTBLUE_EX}🔧 Query expanded into {len(queries)} searches.")
    print(f"{Fore.LIGHTBLUE_EX}📊 Each search will run up to {max_batches} batches of {batch_size} papers.")
    print(f"{Fore.LIGHTBLUE_EX}➡️ Maximum total requests: {len(queries) * max_batches}\n")

    if not ps.ask_confirmation(queries, timeout=10):
        print(f"{Fore.RED}❌ Operation canceled by user.")
        sys.exit()
    else:
        print(f"{Fore.GREEN}✅ Starting the search...")

    headers = {"User-Agent": USER_AGENT}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    output_statistics = os.path.join('./', "output_statistics.csv")

    for query in queries:
        print(f"\n{Fore.BLUE}🔎 Searching for articles on: {Style.BRIGHT}{query}{Style.RESET_ALL}")
        total_paper = 0
        filtered_papers = 0
        for batch in range(max_batches):
            offset = batch * batch_size
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={batch_size}&offset={offset}&fields={FIELDS}"
            response = get_with_backoff(url, headers)
            if response is None: break

            data = response.json().get("data", [])
            total_paper += len(data)
            if not data:
                print(f"{Fore.YELLOW}📭 No more articles found for this query.")
                break

            filtered = [p for p in data if (p.get("citationCount", 0) >= min_citations and (min_year is None or p.get("year", 0) >= min_year) and (max_year is None or p.get("year", 0) <= max_year))]
            filtered_papers += len(filtered)

            if filtered:
                output_folder = "results"
                os.makedirs(output_folder, exist_ok=True)
                sanitized_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_file = os.path.join(output_folder, f"{sanitized_query}-{batch + 1}.csv")

                with open(output_file, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Query", "Title", "Year", "Citations", "Authors", "URL", "Abstract"])
                    for paper in filtered:
                        authors = "; ".join([a["name"] for a in paper.get("authors", [])])
                        writer.writerow([query, paper.get("title", ""), paper.get("year", ""), paper.get("citationCount", 0), authors, paper.get("url", ""), paper.get("abstract", "")])
                print(f"{Fore.GREEN}✅ {len(filtered)} articles saved, batch {batch + 1} -> {output_file}")
            else:
                print(f"{Fore.YELLOW}⚠️ No articles in batch {batch + 1} met the filter criteria.")
            time.sleep(3)

        with open(output_statistics, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Query", "Total Articles", "Filtered Articles"])
            writer.writerow([query, total_paper, filtered_papers])
    print(f"\n{Fore.GREEN}🏁 Finished.")

def main_menu():
    """Displays the main menu and handles user choices."""
    display_banner()
    while True:
        print(f"\n{Fore.CYAN}--- Main Menu ---")
        print(f"{Fore.YELLOW}1. Run Bibliographic Search")
        print(f"{Fore.YELLOW}2. Filter Papers with AI (Llama)")
        print(f"{Fore.YELLOW}3. Analyze Results")
        print(f"{Fore.YELLOW}4. Help / Information")
        print(f"{Fore.YELLOW}5. Exit")
        
        choice = input(f"\n{Fore.CYAN}Enter your choice (1-5): {Style.RESET_ALL}")
        
        if choice == "1":
            run_bibliographic_search()
        elif choice == "2":
            input_folder = "results"
            print(f"\n{Fore.GREEN}✅ Starting AI-based filtering...")
            try:
                import llama_filter as lf
                lf.filter_with_llama(input_folder)
                print(f"\n{Fore.GREEN}🏁 AI filtering finished. Check the 'llama_filtered' folder for results.")
            except ImportError:
                print(f"{Fore.RED}❌ Error: 'llama_filter.py' not found. Make sure the file is in the same directory.")
            except Exception as e:
                print(f"{Fore.RED}❌ An error occurred during AI filtering: {e}")
        elif choice == "3":
            sa.run_statistics_analyzer()
        elif choice == "4":
            hm.show_help_menu()
        elif choice == "5":
            print(f"{Fore.BLUE}Exiting. Goodbye!{Style.RESET_ALL}")
            sys.exit()
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please enter a number from 1 to 5.")

if __name__ == "__main__":
    main_menu()