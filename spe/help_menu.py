# help_menu.py

from colorama import Fore, Style, init

init(autoreset=True)

def show_autosearch_help():
    """
    Renders the documentation for the Query Parser and Search Engine.
    Explains Boolean logic, Cartesian expansion, and API differences.
    """
    print(f"\n{Fore.CYAN}-------------- AutoSearch: Query & Features Guide --------------{Style.RESET_ALL}")
    
    # --- 1. OVERVIEW ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. System Architecture:{Style.RESET_ALL}")
    print("   The engine integrates two primary data sources:")
    print(f"   - {Fore.YELLOW}Semantic Scholar{Style.RESET_ALL}: Best for metadata discovery")
    print("     and citation graphs.")
    print(f"   - {Fore.YELLOW}ArXiv{Style.RESET_ALL}: Best for full-text PDF retrieval and")
    print("     open-access content.")
    print("   Both engines utilize the same query parser for logic.")

    # --- 2. SYNTAX ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Query Syntax:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}AND{Style.RESET_ALL}   : Intersection (e.g., AI AND Physics).")
    print(f"   {Fore.GREEN}OR{Style.RESET_ALL}    : Union (used within parentheses for grouping).")
    print(f"   {Fore.GREEN}NOT{Style.RESET_ALL}   : Exclusion (e.g., NOT Review).")
    
    print(f"   {Fore.GREEN}*...*{Style.RESET_ALL} : {Fore.RED}{Style.BRIGHT}Exact Phrase Delimiter{Style.RESET_ALL}")
    print(f"            - {Fore.GREEN}Correct:{Style.RESET_ALL}   *Machine Learning*")
    print("              (Treats as a single token)")
    print(f"            - {Fore.RED}Wrong:{Style.RESET_ALL}     Machine Learning")
    print("              (Should be: Machine AND Learning)")

    # --- 3. EXPANSION LOGIC ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. The Query Expansion Engine:{Style.RESET_ALL}")
    print("   The parser performs a Cartesian product on OR groups")
    print("   to generate optimized atomic queries for the APIs.")
    
    print(f"\n   {Fore.CYAN}Input:{Style.RESET_ALL}   (*Solar* OR *Wind*) AND *Energy*")
    print(f"        {Fore.CYAN}│{Style.RESET_ALL}")
    print(f"        {Fore.CYAN}▼{Style.RESET_ALL}   {Style.DIM}(Splits into specific requests){Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Req 1:{Style.RESET_ALL}   *Solar* AND *Energy*")
    print(f"   {Fore.GREEN}Req 2:{Style.RESET_ALL}   *Wind* AND *Energy*")
    
    print(f"\n   {Fore.YELLOW}⚠️  Note:{Style.RESET_ALL} Nesting multiple OR groups increases")
    print("   API calls exponentially.")

    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_content_filter_help():
    """
    Renders documentation for the Content Filter (PDF & CSV).
    Details the scoring metrics and dual-mode operation.
    """
    print(f"\n{Fore.CYAN}----------- Content Filter by Regex: PDF & CSV Guide -----------{Style.RESET_ALL}")
    
    # --- 1. DUAL MODE ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Dual Mode Operation:{Style.RESET_ALL}")
    print("   This tool works on two types of data:")
    print(f"   {Fore.YELLOW}A) Local PDFs:{Style.RESET_ALL} Scans full text of downloaded files.")
    print(f"   {Fore.YELLOW}B) CSV Metadata:{Style.RESET_ALL} Scans 'Title' + 'Abstract'.")
    print("      (Useful for screening Semantic Scholar results")
    print("      before downloading PDFs).")

    # --- 2. RANKING LOGIC ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Relevance Scoring System:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}HIGH Relevance{Style.RESET_ALL}   : All terms present + {Fore.YELLOW}Close Proximity{Style.RESET_ALL}.")
    print("                      (Terms appear within a 50-word window).")
    print(f"   {Fore.YELLOW}MEDIUM Relevance{Style.RESET_ALL} : All terms present, but scattered.")
    print(f"   {Fore.WHITE}LOW Relevance{Style.RESET_ALL}    : Partial match (some terms missing).")

    # --- 3. OUTPUT ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. Output Organization:{Style.RESET_ALL}")
    print("   - For PDFs: Files copied to `High/Medium/Low_Relevance`.")
    print("   - For CSVs: New CSVs created in `content_filtered_csv/`.")

    # --- 4. EXAMPLE ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}4. Practical Example:{Style.RESET_ALL}")
    print("   Target: Find papers specifically about 'DFT' using 'VASP'.")
    print(f"   {Fore.YELLOW}Query:{Style.RESET_ALL}  *DFT* AND *VASP*")
    print(f"   - If 'DFT' & 'VASP' are in same abstract -> {Fore.GREEN}HIGH{Style.RESET_ALL}")

    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_analysis_help():
    """
    Renders documentation for the Statistical Analyzer & Visualization.
    """
    print(f"\n{Fore.CYAN}---------------- Statistical Analyzer & Graphs -----------------{Style.RESET_ALL}")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Purpose:{Style.RESET_ALL}")
    print("   The Analyzer processes raw or filtered CSVs to generate")
    print("   insights. It consolidates data, removes duplicates,")
    print("   and generates visualizations.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Data Visualization (Matplotlib):{Style.RESET_ALL}")
    print("   The tool automatically generates PNG images in `log/`:")
    print(f"   - {Fore.GREEN}timeline_plot.png{Style.RESET_ALL}       : Bar chart of pubs per year.")
    print(f"   - {Fore.GREEN}top_authors_plot.png{Style.RESET_ALL}    : Most prolific authors.")
    print(f"   - {Fore.GREEN}citation_histogram.png{Style.RESET_ALL}  : Citation count dist.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. Important Limitations:{Style.RESET_ALL}")
    print(f"   {Fore.RED}⚠️  ArXiv Citation Data:{Style.RESET_ALL}")
    print("   The ArXiv API does NOT provide citation counts.")
    print("   - Citation graphs will not be generated for research on ArXiv.")
    print("   - Use Semantic Scholar (Option 2) for citation metrics.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}4. Deduplication Logic:{Style.RESET_ALL}")
    print(f"   - Uses {Style.BRIGHT}Normalized Title{Style.RESET_ALL} as a unique key.")
    print(f"   - {Style.DIM}'Graphyne Props'{Style.RESET_ALL} == {Style.DIM}'graphyne props'{Style.RESET_ALL}")

    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_author_search_help():
    """Renders documentation for Google Scholar Author Search."""
    print(f"\n{Fore.CYAN}------------- Author Search: Google Scholar Guide --------------{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Strategy:{Style.RESET_ALL}")
    print("   Direct name searching on Google Scholar is prone to IP")
    print(f"   blocks. This tool requires a {Fore.YELLOW}User ID{Style.RESET_ALL} for stability.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Extraction Steps:{Style.RESET_ALL}")
    print(f"   1. Go to {Style.BRIGHT}scholar.google.com{Style.RESET_ALL} and find the profile.")
    print("   2. Inspect the URL structure:")
    print("      https://scholar.google.com/citations?")
    print(f"      user={Fore.GREEN}{Style.BRIGHT}qc6CJjYAAAAJ{Style.RESET_ALL}&hl=en")
    print(f"   3. Copy the ID between 'user=' and '&' ({Fore.GREEN}qc6CJjYAAAAJ{Style.RESET_ALL}).")
    
    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_bibtex_help():
    """Renders documentation for the BibTeX Generator."""
    print(f"\n{Fore.CYAN}------------------- BibTeX Generator: Guide --------------------{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Purpose:{Style.RESET_ALL}")
    print("   Converts CSV results into a `.bib` file for LaTeX.")
    print("   Creates citation keys automatically (e.g., `Silva2024DFT`).")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Workflow:{Style.RESET_ALL}")
    print("   You can choose to generate references from:")
    print(f"   - {Fore.YELLOW}RAW Data:{Style.RESET_ALL} All results in `results/` and `arxiv_results/`.")
    print(f"   - {Fore.GREEN}FILTERED Data:{Style.RESET_ALL} Only papers approved by AI or")
    print("     Content Filter by Regex.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. Features:{Style.RESET_ALL}")
    print("   - Smart Detection: Finds 'Title', 'Year', 'Authors'.")
    print("   - Venue Support: Extracts Journal/Conference names.")
    print("   - LaTeX Sanitization: Escapes chars like `&`, `%`, `_`.")

    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_llama_filter_help():
    """Renders documentation for the LLM-based Semantic Filter."""
    print(f"\n{Fore.CYAN}------------- AI Filter: Features & Best Practices -------------{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Concept:{Style.RESET_ALL}")
    print("   Uses a quantized local LLM (Qwen/TinyLlama) to perform")
    print("   semantic screening of Titles and Abstracts.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Configuration Parameters:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}a) Persona{Style.RESET_ALL}   : Defines AI perspective (e.g., 'Senior Editor').")
    print(f"   {Fore.GREEN}b) Topic{Style.RESET_ALL}     : The core subject (e.g., '2D Materials').")
    print(f"   {Fore.GREEN}c) Criteria{Style.RESET_ALL}  : Explicit inclusion/exclusion rules.")
    print("                   (e.g., 'Must include experimental")
    print("                   validation').")

    print(f"\n{Fore.MAGENTA}Press Enter to return...{Style.RESET_ALL}")
    input()

def show_llama_risks():
    """Renders disclaimer regarding AI limitations."""
    print(f"\n{Fore.RED}---------------- AI Filter: Risks & Limitations ----------------{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Hallucinations:{Style.RESET_ALL}")
    print(f"   {Fore.YELLOW}The AI provides probabilistic classifications, not facts.{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Model Bias:{Style.RESET_ALL}")
    print("   Decisions depend heavily on the prompt quality and")
    print("   model training data.")
    
    print(f"\n{Fore.RED}{Style.BRIGHT}Usage Advisory:{Style.RESET_ALL}")
    print("   Use this feature to prioritize reading lists, not to")
    print("   systematically exclude literature without human review.")
    
    print(f"{Fore.MAGENTA}\nPress Enter to return...{Style.RESET_ALL}")
    input()

def show_help_menu():
    """Main routing function for the Help System."""
    while True:
        print(f"\n{Fore.CYAN}------------------------ Main Help Menu ------------------------\n")
        print(f"{Fore.WHITE}Select a topic for more information:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. AutoSearch Guide (Queries & APIs)")
        print(f"{Fore.GREEN}2. Author Search Guide (Google Scholar)")
        print(f"{Fore.GREEN}3. AI Filter Guide (Semantic Analysis)")
        print(f"{Fore.GREEN}4. Content Filter by Regex Guide (PDF & CSV Ranking)")
        print(f"{Fore.GREEN}5. Stats & Graphs Guide (Analysis)")
        print(f"{Fore.GREEN}6. BibTeX Generator Guide (LaTeX)")
        print(f"{Fore.RED}7. AI Risks & Limitations")
        print(f"{Fore.YELLOW}0. Exit Help Menu")
        
        choice = input(f"{Fore.WHITE}> {Style.RESET_ALL}")
        
        if choice == '1': show_autosearch_help()
        elif choice == '2': show_author_search_help()
        elif choice == '3': show_llama_filter_help()
        elif choice == '4': show_content_filter_help() 
        elif choice == '5': show_analysis_help()
        elif choice == '6': show_bibtex_help()
        elif choice == '7': show_llama_risks()
        elif choice == '0':
            print(f"{Fore.YELLOW}Exiting help menu...{Style.RESET_ALL}")
            break
        elif choice.strip() == '':
            return
        else:
            print(f"{Fore.RED}Invalid option. Please choose a number from 0 to 7.{Style.RESET_ALL}")