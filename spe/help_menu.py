from colorama import Fore, Style, init

init(autoreset=True)

def show_autosearch_help():
    """
    Renders the documentation for the Query Parser and Search Engine.
    Explains Boolean logic, Cartesian expansion, and API differences.
    """
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== AutoSearch: Query & Features Guide ==={Style.RESET_ALL}")
    
    # --- 1. OVERVIEW ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. System Architecture:{Style.RESET_ALL}")
    print("   The engine integrates two primary data sources:")
    print(f"   - {Fore.YELLOW}Semantic Scholar{Style.RESET_ALL}: Best for metadata discovery and citation graphs.")
    print(f"   - {Fore.YELLOW}ArXiv{Style.RESET_ALL}: Best for full-text PDF retrieval and open-access content.")
    print("   Both engines utilize the same query parser for consistent logic.")

    # --- 2. SYNTAX ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Query Syntax:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}AND{Style.RESET_ALL}   : Intersection (e.g., AI AND Physics).")
    print(f"   {Fore.GREEN}OR{Style.RESET_ALL}    : Union (used within parentheses for grouping).")
    print(f"   {Fore.GREEN}NOT{Style.RESET_ALL}   : Exclusion (e.g., NOT Review).")
    
    print(f"   {Fore.GREEN}*...*{Style.RESET_ALL} : {Fore.RED}{Style.BRIGHT}Exact Phrase Delimiter{Style.RESET_ALL}")
    print(f"            - {Fore.GREEN}Correct:{Style.RESET_ALL}   *Machine Learning* (Treats as a single token)")
    print(f"            - {Fore.RED}Wrong:{Style.RESET_ALL}     Machine Learning   (It should be like: Machine AND Learning)")

    # --- 3. EXPANSION LOGIC ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. The Query Expansion Engine:{Style.RESET_ALL}")
    print("   The parser performs a Cartesian product on OR groups to generate")
    print("   optimized atomic queries for the APIs.")
    
    print(f"\n   {Fore.CYAN}Input:{Style.RESET_ALL}   (*Solar* OR *Wind*) AND *Energy*")
    print(f"        {Fore.CYAN}│{Style.RESET_ALL}")
    print(f"        {Fore.CYAN}▼{Style.RESET_ALL}   {Style.DIM}(Splits into specific requests){Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Req 1:{Style.RESET_ALL}   *Solar* AND *Energy*")
    print(f"   {Fore.GREEN}Req 2:{Style.RESET_ALL}   *Wind* AND *Energy*")
    
    print(f"\n   {Fore.YELLOW}⚠️  Note:{Style.RESET_ALL} Nesting multiple OR groups increases API calls exponentially.")

    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_content_filter_help():
    """
    Renders documentation for the Local PDF Content Filter.
    Details the scoring metrics (Proximity/Coverage) and Implicit AND logic.
    """
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Local PDF Content Filter: Guide ==={Style.RESET_ALL}")
    
    # --- 1. MECHANISM ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Mechanism:{Style.RESET_ALL}")
    print("   This tool extracts raw text from downloaded PDFs and applies a")
    print(f"   {Style.BRIGHT}Relevance Scoring System{Style.RESET_ALL} based on your query.")
    print("   It creates three output folders: High, Medium, and Low relevance.")

    # --- 2. RANKING LOGIC ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Ranking Logic (How Score is Calculated):{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}HIGH Relevance{Style.RESET_ALL}   : All terms present + {Fore.YELLOW}Close Proximity{Style.RESET_ALL}.")
    print("                      (Terms appear within a 50-word window).")
    print(f"   {Fore.YELLOW}MEDIUM Relevance{Style.RESET_ALL} : All terms present, but scattered.")
    print(f"   {Fore.WHITE}LOW Relevance{Style.RESET_ALL}    : Partial match (some terms missing).")

    # --- 3. IMPLICIT AND ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. Implicit Logic:{Style.RESET_ALL}")
    print("   If you type words without boolean operators, they are treated as AND.")
    print(f"   Query: {Style.DIM}*materials 2d*{Style.RESET_ALL} -> Parsed as: {Style.DIM}materials AND 2d{Style.RESET_ALL}")

    # --- 4. EXAMPLE ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}4. Practical Example:{Style.RESET_ALL}")
    print("   Target: Find papers specifically about 'DFT' using 'VASP'.")
    print(f"   {Fore.YELLOW}Query:{Style.RESET_ALL}  *DFT* AND *VASP*")
    print(f"   - If 'DFT' and 'VASP' appear in the same paragraph -> {Fore.GREEN}HIGH{Style.RESET_ALL}")
    print(f"   - If 'DFT' is on page 1 and 'VASP' on page 10      -> {Fore.YELLOW}MEDIUM{Style.RESET_ALL}")

    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_analysis_help():
    """
    Renders documentation for the Statistical Analyzer module.
    Explains data consolidation and deduplication strategies.
    """
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Statistical Analyzer: Guide ==={Style.RESET_ALL}")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Purpose:{Style.RESET_ALL}")
    print("   The Analyzer processes raw CSV results to generate insights.")
    print("   It is essential for cleaning up data after multiple search batches.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Deduplication Logic:{Style.RESET_ALL}")
    print("   Since queries often overlap (e.g., 'AI AND Drug' vs 'ML AND Drug'),")
    print("   duplicate papers are common.")
    print(f"   - The analyzer creates a unique key based on the {Style.BRIGHT}Normalized Title{Style.RESET_ALL}.")
    print("   - Case differences and extra spaces are ignored.")
    print(f"   - {Style.DIM}'Graphyne Properties'{Style.RESET_ALL} == {Style.DIM}'graphyne properties'{Style.RESET_ALL}")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. Output Structure:{Style.RESET_ALL}")
    print(f"   Results are saved in the {Style.BRIGHT}log/{Style.RESET_ALL} directory:")
    print(f"   - {Fore.GREEN}top_papers.csv{Style.RESET_ALL}       : Unified list of unique articles.")
    print(f"   - {Fore.GREEN}prolific_authors.csv{Style.RESET_ALL} : Frequency count of authors.")
    print(f"   - {Fore.GREEN}productive_years.csv{Style.RESET_ALL} : Publication timeline analysis.")

    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_author_search_help():
    """Renders documentation for Google Scholar Author Search."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Author Search: Google Scholar Guide ==={Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Strategy:{Style.RESET_ALL}")
    print("   Direct name searching on Google Scholar is prone to IP blocks.")
    print(f"   This tool requires a {Fore.YELLOW}User ID{Style.RESET_ALL} for stability.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Extraction Steps:{Style.RESET_ALL}")
    print(f"   1. Go to {Style.BRIGHT}scholar.google.com{Style.RESET_ALL} and find the author's profile.")
    print("   2. Inspect the URL structure:")
    print(f"      https://scholar.google.com/citations?user={Fore.GREEN}{Style.BRIGHT}qc6CJjYAAAAJ{Style.RESET_ALL}&hl=en")
    print(f"   3. Copy the ID found between 'user=' and '&' ({Fore.GREEN}qc6CJjYAAAAJ{Style.RESET_ALL}).")
    
    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_llama_filter_help():
    """Renders documentation for the LLM-based Semantic Filter."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== AI Filter: Features & Best Practices ==={Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Concept:{Style.RESET_ALL}")
    print("   Uses a quantized local LLM (Qwen/TinyLlama) to perform semantic")
    print("   screening of Titles and Abstracts.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Configuration Parameters:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}a) Persona{Style.RESET_ALL}   : Defines the AI's perspective (e.g., 'Senior Editor').")
    print(f"   {Fore.GREEN}b) Topic{Style.RESET_ALL}     : The core subject (e.g., '2D Materials').")
    print(f"   {Fore.GREEN}c) Criteria{Style.RESET_ALL}  : Explicit inclusion/exclusion rules.")
    print("                   (e.g., 'Must include experimental validation').")

    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_llama_risks():
    """Renders disclaimer regarding AI limitations."""
    print(f"\n{Fore.RED}{Style.BRIGHT}=== AI Filter: Risks & Limitations ==={Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Hallucinations:{Style.RESET_ALL}")
    print(f"   {Fore.YELLOW}The AI provides probabilistic classifications, not facts.{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Model Bias:{Style.RESET_ALL}")
    print("   Decisions depend heavily on the prompt quality and model training data.")
    
    print(f"\n{Fore.RED}{Style.BRIGHT}Usage Advisory:{Style.RESET_ALL}")
    print("   Use this feature to prioritize reading lists, not to systematically")
    print("   exclude literature without human review.")
    
    print(f"{Fore.MAGENTA}\nPress Enter to return...{Style.RESET_ALL}")
    input()

def show_help_menu():
    """Main routing function for the Help System."""
    while True:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Main Help Menu ===")
        print(f"{Fore.WHITE}Select a topic for more information:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}(1) AutoSearch Guide (Queries & APIs)")
        print(f"{Fore.GREEN}(2) Author Search Guide (Google Scholar)")
        print(f"{Fore.GREEN}(3) AI Filter Guide (Semantic Analysis)")
        print(f"{Fore.GREEN}(4) Local PDF Content Filter Guide (Ranking)")
        print(f"{Fore.GREEN}(5) Statistical Analyzer Guide (Deduplication)")
        print(f"{Fore.RED}(6) AI Risks & Limitations")
        print(f"{Fore.YELLOW}(0) Exit Help Menu")
        
        choice = input(f"{Fore.WHITE}> {Style.RESET_ALL}")
        
        if choice == '1': show_autosearch_help()
        elif choice == '2': show_author_search_help()
        elif choice == '3': show_llama_filter_help()
        elif choice == '4': show_content_filter_help() 
        elif choice == '5': show_analysis_help()
        elif choice == '6': show_llama_risks()
        elif choice == '0':
            print(f"{Fore.YELLOW}Exiting help menu...{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid option. Please choose a number from 0 to 6.{Style.RESET_ALL}")