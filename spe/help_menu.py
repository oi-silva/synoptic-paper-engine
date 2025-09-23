# help_menu.py

from colorama import Fore, Style, init

init(autoreset=True)

def show_autosearch_help():
    """Displays a guide for the AutoSearch query features."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== AutoSearch: Query & Features Guide ==={Style.RESET_ALL}")
    print(f"\n{Fore.WHITE}{Style.BRIGHT}1. Purpose:{Style.RESET_ALL}")
    print("   AutoSearch performs large-scale academic searches using the Semantic Scholar API.")
    print("   It automates fetching papers based on complex queries and pre-filtering by year and citations.")
    
    print(f"\n{Fore.WHITE}{Style.BRIGHT}2. Query Construction Rules:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}- AND{Style.RESET_ALL} : requires both terms (e.g., AI AND Physics)")
    print(f"   {Fore.GREEN}- OR{Style.RESET_ALL}  : allows either term (e.g., Graphene OR Nanotubes)")
    print(f"   {Fore.GREEN}- NOT{Style.RESET_ALL} : excludes terms (e.g., AI NOT Classical)")
    print(f"   {Fore.GREEN}- (...) {Style.RESET_ALL}: group terms to control precedence (e.g., AI AND (Physics OR Chemistry))")
    # --- NOVA EXPLICAÇÃO DO ASTERISCO ---
    print(f"   {Fore.GREEN}- *...* {Style.RESET_ALL}: treats multi-word phrases as a single, exact term.")
    print(f"           (e.g., {Style.DIM}*Machine Learning* is treated as the phrase \"Machine Learning\",")
    print(f"            while {Style.DIM}Machine Learning is treated as Machine AND Learning){Style.RESET_ALL}")

    # --- NOVO EXEMPLO COMPLETO ---
    print(f"\n{Fore.WHITE}{Style.BRIGHT}3. Complete Example:{Style.RESET_ALL}")
    print("   Imagine you want papers about the use of 'Artificial Intelligence' or 'Machine Learning'")
    print("   in 'Drug Discovery', but you want to exclude review articles.")
    print(f"\n   {Fore.YELLOW}Query:{Style.RESET_ALL} (*Artificial Intelligence* OR *Machine Learning*) AND *Drug Discovery* NOT Review")
    print(f"\n   {Fore.WHITE}Breakdown:{Style.RESET_ALL}")
    print(f"   - {Style.BRIGHT}(*Artificial Intelligence* OR *Machine Learning*){Style.RESET_ALL}: Finds papers that contain the exact phrase")
    print("     'Artificial Intelligence' OR the exact phrase 'Machine Learning'.")
    print(f"   - {Style.BRIGHT}AND *Drug Discovery*{Style.RESET_ALL}: The results MUST ALSO contain the exact phrase 'Drug Discovery'.")
    print(f"   - {Style.BRIGHT}NOT Review{Style.RESET_ALL}: From that list, any paper with the word 'Review' is excluded.")

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
        print(f"{Fore.GREEN}(1) AutoSearch Guide (Semantic Scholar)")
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