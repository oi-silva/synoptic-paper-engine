# spe/main.py

import requests
import time
import csv
import sys
import os
from colorama import init, Fore, Style

# Imports relative to the current package (notice the '.')
from . import parse_query as pq
from . import preview_step as ps
from . import help_menu as hm
from . import statistics_analyzer as sa
# ...

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

def get_unique_folder(base_folder):
    """
    Checks for the existence of a folder and prompts the user to
    create a new one or overwrite the existing.
    """
    if not os.path.exists(base_folder):
        print(f"{Fore.GREEN}Creating folder '{base_folder}'.")
        os.makedirs(base_folder)
        return base_folder

    print(f"\n{Fore.YELLOW}⚠️  The folder '{base_folder}' already exists.")
    while True:
        choice = input(f"{Fore.YELLOW}Do you want to (1) Create a new folder or (2) Overwrite existing files?{Style.RESET_ALL} ")
        if choice == "1":
            count = 1
            while os.path.exists(f"{base_folder}-{count}"):
                count += 1
            new_folder = f"{base_folder}-{count}"
            os.makedirs(new_folder)
            print(f"{Fore.GREEN}✅ Creating new folder '{new_folder}'.")
            return new_folder
        elif choice == "2":
            print(f"{Fore.RED}🛑 Warning: Existing files in '{base_folder}' may be overwritten.")
            return base_folder
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please enter 1 or 2.")

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
            print(f"{Fore.RED}❌ Query cannot be empty. Returning to main menu.")
            return # <-- CHANGED THIS LINE
        break

    try:
        queries = pq.parse_query(query_str)
    except Exception as e:
        print(f"{Fore.RED}❌ Error parsing the query: {e}")
        return

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
        return
    else:
        print(f"{Fore.GREEN}✅ Starting the search...")

    headers = {"User-Agent": USER_AGENT}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    output_folder = get_unique_folder("results")
    output_statistics = os.path.join(output_folder, "output_statistics.csv")

    with open(output_statistics, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Query", "Total Articles", "Filtered Articles"])

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
            writer.writerow([query, total_paper, filtered_papers])
    print(f"\n{Fore.GREEN}🏁 Finished.")

def main_menu():
    """Displays the main menu and handles user choices."""
    display_banner()
    while True:
        # Clear the terminal for a cleaner menu view
        os.system('cls' if os.name == 'nt' else 'clear')
        display_banner()
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
            # New logic to choose the results folder to filter
            base_folder = "results"
            all_entries = os.listdir('.')
            potential_folders = [d for d in all_entries if os.path.isdir(d) and d.startswith(base_folder)]
            
            if not potential_folders:
                print(f"{Fore.RED}❌ No 'results' folders found. Please run a search first.")
                input(f"\n{Fore.GREEN}Press Enter to return to the main menu...{Style.RESET_ALL}")
                continue

            print(f"\n{Fore.CYAN}Please choose a 'results' folder to filter:{Style.RESET_ALL}")
            for i, folder_name in enumerate(potential_folders):
                print(f"{Fore.YELLOW}{i+1}. {folder_name}")
            
            while True:
                try:
                    choice_num = int(input(f"\n{Fore.CYAN}Enter your choice: {Style.RESET_ALL}"))
                    if 1 <= choice_num <= len(potential_folders):
                        input_folder = potential_folders[choice_num - 1]
                        break
                    else:
                        print(f"{Fore.RED}Invalid number. Please try again.")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number.")
            
            output_folder = get_unique_folder("llama_filtered")
            print(f"\n{Fore.GREEN}✅ Starting AI-based filtering...")
            try:
                from . import llama_filter as lf
                lf.filter_with_llama(input_folder, output_folder)
                print(f"\n{Fore.GREEN}🏁 AI filtering finished. Check the '{output_folder}' folder for results.")
                input(f"\n{Fore.GREEN}Press Enter to return to the main menu...{Style.RESET_ALL}")
            except ImportError:
                print(f"{Fore.RED}❌ Error: 'llama_filter.py' not found. Make sure the file is in the same directory.")
                input(f"\n{Fore.GREEN}Press Enter to return to the main menu...{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ An error occurred during AI filtering: {e}")
                input(f"\n{Fore.GREEN}Press Enter to return to the main menu...{Style.RESET_ALL}")

        elif choice == "3":
            print(f"\n{Fore.CYAN}--- Choose analysis type ---")
            print(f"{Fore.YELLOW}1. Analyze Bibliographic Search results")
            print(f"{Fore.YELLOW}2. Analyze AI Filter results")
            print(f"{Fore.YELLOW}0. Return to Main Menu")
            analysis_choice = input(f"\n{Fore.CYAN}Enter your choice (0-2): {Style.RESET_ALL}")

            if analysis_choice == "1":
                base_folder = "results"
                
                all_entries = os.listdir('.')
                potential_folders = [d for d in all_entries if os.path.isdir(d) and d.startswith(base_folder)]
                
                if not potential_folders:
                    print(f"{Fore.RED}❌ No 'results' folders found.")
                    continue
                
                print(f"\n{Fore.CYAN}Please choose a folder to analyze:{Style.RESET_ALL}")
                for i, folder_name in enumerate(potential_folders):
                    print(f"{Fore.YELLOW}{i+1}. {folder_name}")
                
                while True:
                    try:
                        choice_num = int(input(f"\n{Fore.CYAN}Enter your choice: {Style.RESET_ALL}"))
                        if 1 <= choice_num <= len(potential_folders):
                            folder_path = potential_folders[choice_num - 1]
                            sa.analyze_autosearch(folder_path)
                            input(f"\n{Fore.GREEN}Press Enter to return to the main menu...{Style.RESET_ALL}")
                            break
                        else:
                            print(f"{Fore.RED}Invalid number. Please try again.")
                    except ValueError:
                        print(f"{Fore.RED}Invalid input. Please enter a number.")
            elif analysis_choice == "2":
                base_folder = "llama_filtered"
                
                all_entries = os.listdir('.')
                potential_folders = [d for d in all_entries if os.path.isdir(d) and d.startswith(base_folder)]
                
                if not potential_folders:
                    print(f"{Fore.RED}❌ No 'llama_filtered' folders found.")
                    continue
                
                print(f"\n{Fore.CYAN}Please choose a folder to analyze:{Style.RESET_ALL}")
                for i, folder_name in enumerate(potential_folders):
                    print(f"{Fore.YELLOW}{i+1}. {folder_name}")

                while True:
                    try:
                        choice_num = int(input(f"\n{Fore.CYAN}Enter your choice: {Style.RESET_ALL}"))
                        if 1 <= choice_num <= len(potential_folders):
                            folder_path = potential_folders[choice_num - 1]
                            sa.analyze_llama_csv_results(folder_path)
                            input(f"\n{Fore.GREEN}Press Enter to return to the main menu...{Style.RESET_ALL}")
                            break
                        else:
                            print(f"{Fore.RED}Invalid number. Please try again.")
                    except ValueError:
                        print(f"{Fore.RED}Invalid input. Please enter a number.")
            elif analysis_choice == "0":
                continue

            else:
                print(f"{Fore.RED}❌ Invalid choice. Please enter 0, 1 or 2.")

        elif choice == "4":
            hm.show_help_menu()
        elif choice == "5":
            print(f"{Fore.BLUE}Exiting. Goodbye!{Style.RESET_ALL}")
            sys.exit()
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please enter a number from 1 to 5.")

if __name__ == "__main__":
    main_menu()
