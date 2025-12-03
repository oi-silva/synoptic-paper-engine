# help_menu.py

from colorama import Fore, Style, init

init(autoreset=True)

def show_autosearch_help():
    """Displays a guide for the AutoSearch query features."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== AutoSearch: Query & Features Guide ==={Style.RESET_ALL}")
    
    # --- 1. VISÃO GERAL ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Purpose:{Style.RESET_ALL}")
    print("   AutoSearch performs systematic searches using {Fore.YELLOW}Semantic Scholar{Style.RESET_ALL} and {Fore.YELLOW}ArXiv{Style.RESET_ALL}." .format(Fore=Fore, Style=Style))
    print("   It handles boolean logic and automatic query expansion.")

    # --- 2. SINTAXE BÁSICA (CORRIGIDA) ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Basic Syntax Rules:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}AND{Style.RESET_ALL}   : Both terms required (e.g., AI AND Physics)")
    print(f"   {Fore.GREEN}OR{Style.RESET_ALL}    : Either term allowed (used within parentheses)")
    print(f"   {Fore.GREEN}NOT{Style.RESET_ALL}   : Exclude term (e.g., NOT Review)")
    
    # --- DESTAQUE PARA O ASTERISCO E O ERRO ---
    print(f"   {Fore.GREEN}*...*{Style.RESET_ALL} : {Fore.RED}{Style.BRIGHT}REQUIRED for Multi-Word Phrases{Style.RESET_ALL}")
    print(f"            - {Fore.GREEN}Correct:{Style.RESET_ALL}   *Machine Learning*")
    print(f"            - {Fore.RED}Incorrect:{Style.RESET_ALL} Machine Learning  {Fore.RED}(Will cause an error!){Style.RESET_ALL}")
    print("              (The parser requires asterisks to group words together)")

    # --- 3. A LÓGICA DE EXPANSÃO ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. The 'Expansion' Engine:{Style.RESET_ALL}")
    print("   The tool automatically expands groups in parentheses into separate queries.")
    
    print(f"\n   {Fore.CYAN}Input Logic:{Style.RESET_ALL}   (*Solar* OR *Wind*) AND *Energy*")
    print(f"         {Fore.CYAN}│{Style.RESET_ALL}")
    print(f"         {Fore.CYAN}▼{Style.RESET_ALL}  {Style.DIM}(Expands to){Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Query 1:{Style.RESET_ALL}      *Solar* AND *Energy*")
    print(f"   {Fore.GREEN}Query 2:{Style.RESET_ALL}      *Wind* AND *Energy*")
    
    print(f"\n   {Fore.YELLOW}⚠️  Warning:{Style.RESET_ALL} Avoid excessive OR groups to prevent rate-limiting.")

    # --- 4. EXEMPLO PRÁTICO ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}4. Practical Example:{Style.RESET_ALL}")
    print("   Goal: Find papers on 'Deep Learning' OR 'Neural Networks' applied to")
    print("   'Drug Discovery', excluding 'Reviews'.")
    
    print(f"\n   {Fore.YELLOW}Query String:{Style.RESET_ALL}")
    print("   (*Deep Learning* OR *Neural Networks*) AND *Drug Discovery* NOT Review")

    print(f"\n{Fore.MAGENTA}Press Enter to return to the help menu...{Style.RESET_ALL}")
    input()


def show_author_search_help():
    """Displays a guide for the Author Search feature on Google Scholar."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Author Search: Google Scholar Guide ==={Style.RESET_ALL}")
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Purpose:{Style.RESET_ALL}")
    print("   This feature downloads the complete list of publications from a specific author's")
    print("   profile on Google Scholar.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Why Use an Author ID? (IMPORTANT){Style.RESET_ALL}")
    print(f"   Searching by name can be unreliable due to Google's anti-scraping measures, often")
    print(f"   resulting in temporary IP blocks or no results found. Searching directly by the")
    print(f"   author's unique Google Scholar ID is a much more {Fore.GREEN}stable and reliable{Style.RESET_ALL} method.")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. How to Find an Author's Google Scholar ID:{Style.RESET_ALL}")
    print("   1. Open a web browser and go to: {Style.BRIGHT}https://scholar.google.com{Style.RESET_ALL}")
    print("   2. Search for the author's name (e.g., 'Yoshua Bengio').")
    print("   3. Click on the author's profile link in the search results.")
    print("   4. Look at the URL in your browser's address bar.")
    print("   5. The ID is the string of letters and numbers after {Style.BRIGHT}user={Style.RESET_ALL} and before {Style.BRIGHT}&{Style.RESET_ALL}.")
    print(f"\n   {Fore.YELLOW}Example URL:{Style.RESET_ALL} https://scholar.google.com/citations?user={Fore.GREEN}{Style.BRIGHT}qc6CJjYAAAAJ{Style.RESET_ALL}&hl=en")
    print(f"   In this example, the ID is: {Fore.GREEN}{Style.BRIGHT}qc6CJjYAAAAJ{Style.RESET_ALL}")
    print("\n   Simply copy this ID and paste it into the script when prompted.")
    
    print(f"\n{Fore.MAGENTA}Press Enter to return to the help menu...{Style.RESET_ALL}")
    input()


def show_llama_filter_help():
    """Displays a guide on how the Llama filter works."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== AI Filter: Features & Best Practices ==={Style.RESET_ALL}")
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Purpose:{Style.RESET_ALL}")
    print("   The AI Filter performs a contextual analysis on the articles found by AutoSearch.")
    print("   It uses an AI model to 'read' the title and abstract and decide if an article is relevant.")
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. How It Works:{Style.RESET_ALL}")
    print("   You will define three key elements:")
    print(f"   {Fore.GREEN}a) Expert Persona:{Style.RESET_ALL} The role the AI should adopt (e.g., 'a materials scientist').")
    print(f"   {Fore.GREEN}b) Research Topic:{Style.RESET_ALL} The specific subject of interest (e.g., 'the use of AI in drug discovery').")
    print(f"   {Fore.GREEN}c) Criteria:{Style.RESET_ALL} A list of specific rules for evaluation (e.g., 'The study must involve human trials').")
    print("\n   The script combines these into a prompt and asks the AI to return **True** or **False** for each article.")
    print(f"\n{Fore.MAGENTA}Press Enter to return to the help menu...{Style.RESET_ALL}")
    input()

def show_llama_risks():
    """Displays important risks and limitations when using the AI filter."""
    print(f"\n{Fore.RED}{Style.BRIGHT}=== AI Filter: Risks & Limitations ==={Style.RESET_ALL}")
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. It Is Not a Fact-Checker:{Style.RESET_ALL}")
    print(f"   {Fore.YELLOW}The AI's decision is a probabilistic assessment, not a guarantee of relevance.{Style.RESET_ALL}")
    print("   It can make mistakes or 'hallucinate' understanding. Always double-check its outputs.")
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Inherent Bias:{Style.RESET_ALL}")
    print("   The model may contain biases from its training data, which could influence its decisions.")
    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. Prompt Sensitivity:{Style.RESET_ALL}")
    print("   The filter's performance is highly dependent on the quality of your prompt criteria.")
    print(f"\n{Fore.RED}{Style.BRIGHT}Conclusion: Use the AI as an Assistant, Not a Replacement.{Style.RESET_ALL}")
    print("   This tool is designed to accelerate the initial screening process, not to replace expert human judgment.")
    print(f"{Fore.MAGENTA}\nPress Enter to return to the help menu...{Style.RESET_ALL}")
    input()

def show_help_menu():
    """Displays the main help menu and navigates to different sections."""
    while True:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Main Help Menu ===")
        print(f"{Fore.WHITE}Select a topic for more information:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}(1) AutoSearch Guide (arXiv & Semantic Scholar)")
        print(f"{Fore.GREEN}(2) Author Search Guide (Google Scholar)")
        print(f"{Fore.GREEN}(3) AI Filter Guide (How to Use It)")
        print(f"{Fore.GREEN}(4) AI Risks & Limitations (Important!)")
        print(f"{Fore.YELLOW}(5) Exit Help Menu")
        
        choice = input(f"{Fore.WHITE}> {Style.RESET_ALL}")
        if choice == '1': show_autosearch_help()
        elif choice == '2': show_author_search_help()
        elif choice == '3': show_llama_filter_help()
        elif choice == '4': show_llama_risks()
        elif choice == '5':
            print(f"{Fore.YELLOW}Exiting help menu...{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid option. Please choose a number from 1 to 5.{Style.RESET_ALL}")