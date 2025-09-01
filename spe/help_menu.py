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
    print(f"\n{Fore.MAGENTA}Press Enter to continue...{Style.RESET_ALL}")
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
        print(f"{Fore.GREEN}(1) AutoSearch Guide (Querying & Features)")
        print(f"{Fore.GREEN}(2) AI Filter Guide (How to Use It)")
        print(f"{Fore.GREEN}(3) AI Risks & Limitations (Important!)")
        print(f"{Fore.YELLOW}(4) Exit Help Menu")
        
        choice = input(f"{Fore.WHITE}> {Style.RESET_ALL}")
        if choice == '1': show_autosearch_help()
        elif choice == '2': show_llama_filter_help()
        elif choice == '3': show_llama_risks()
        elif choice == '4':
            print(f"{Fore.YELLOW}Exiting help menu...{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid option. Please choose a number from 1 to 4.{Style.RESET_ALL}")