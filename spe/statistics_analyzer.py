# statistics_analyzer.py

import os
import csv
import json
from collections import Counter
from colorama import init, Fore, Style

init(autoreset=True)

# Basic English stopwords for keyword analysis
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
    'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
    'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
    'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should',
    'now', 'paper', 'study', 'results', 'research', 'method', 'methods', 'introduction', 'conclusion',
    'abstract', 'figure', 'table', 'data', 'analysis', 'based', 'using', 'also', 'however'
}


def display_header(title):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(80)}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 80}{Style.RESET_ALL}")

def display_top_items(title, counter, top_n=5):
    print(f"\n{Fore.YELLOW}--- {title} (Top {top_n}) ---{Style.RESET_ALL}")
    if not counter:
        print(f"{Fore.WHITE}No data to display.")
        return
    for item, count in counter.most_common(top_n):
        print(f"{Fore.GREEN}{item}: {Style.BRIGHT}{count} mentions")

def analyze_autosearch():
    """
    Finds available results folders, asks the user to choose one,
    and then analyzes the CSV files within it.
    """
    try:
        all_entries = os.listdir('.')
        potential_folders = [d for d in all_entries if os.path.isdir(d) and not d.startswith('.') and not d.startswith('__')]
        
        if not potential_folders:
            print(f"{Fore.RED}❌ No result folders found in the current directory.")
            return

        print(f"\n{Fore.CYAN}Please choose a folder to analyze:{Style.RESET_ALL}")
        for i, folder_name in enumerate(potential_folders):
            print(f"{Fore.YELLOW}{i+1}. {folder_name}")
        print(f"{Fore.YELLOW}0. Cancel")

        while True:
            try:
                choice_str = input(f"\n{Fore.CYAN}Enter your choice: {Style.RESET_ALL}")
                if choice_str == '0':
                    print("Analysis canceled.")
                    return
                
                choice_num = int(choice_str)
                if 1 <= choice_num <= len(potential_folders):
                    folder_path = potential_folders[choice_num - 1]
                    break
                else:
                    print(f"{Fore.RED}Invalid number. Please try again.")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a number.")
    
    except Exception as e:
        print(f"{Fore.RED}❌ An error occurred while listing folders: {e}")
        return
    
    display_header(f"Statistics for '{folder_path}' Folder")

    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    if not csv_files:
        print(f"{Fore.RED}❌ No CSV files found in '{folder_path}'.")
        return

    year_counts = Counter()
    author_counts = Counter()
    all_papers = []
    total_articles = 0

    print(f"Analyzing {len(csv_files)} files...")
    for filename in csv_files:
        filepath = os.path.join(folder_path, filename)
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_articles += 1
                if row.get("Year"): year_counts[row["Year"]] += 1
                if row.get("Authors"): author_counts.update([author.strip() for author in row["Authors"].split(';')])
                
                try:
                    all_papers.append({
                        "title": row.get("Title", "N/A"),
                        "citations": int(row.get("Citations", 0))
                    })
                except (ValueError, TypeError):
                    continue

    sorted_papers = sorted(all_papers, key=lambda p: p['citations'], reverse=True)
    top_papers = sorted_papers[:5]

    print(f"\n{Fore.WHITE}--- Overall Summary ---")
    print(f"{Fore.GREEN}Total Articles Collected: {Style.BRIGHT}{total_articles}")

    display_top_items("Most Productive Years", year_counts)
    display_top_items("Most Prolific Authors", author_counts)

    print(f"\n{Fore.YELLOW}--- Top {len(top_papers)} Most Cited Papers ---{Style.RESET_ALL}")
    if not top_papers:
        print(f"{Fore.WHITE}No papers with citation data found.")
    else:
        for i, paper in enumerate(top_papers):
            title = paper['title']
            if len(title) > 70:
                title = title[:67] + "..."
            
            print(f"{Fore.WHITE}{i+1}. {Fore.GREEN}{title} \n   {Style.DIM}{Fore.WHITE}└─ Citations: {Style.BRIGHT}{paper['citations']}{Style.RESET_ALL}")


def analyze_llama_filter(file_path="llama_filtered/llama_filtered_articles.jsonl"):
    """Analyzes the JSONL file generated by the AI filter."""
    display_header("AI Filter Results Statistics")

    if not os.path.exists(file_path):
        print(f"{Fore.RED}❌ File '{file_path}' not found. Please run the AI filter first.")
        return

    query_counts = Counter()
    word_counts = Counter()
    total_articles = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            total_articles += 1
            data = json.loads(line)
            if data.get("query"): query_counts[data["query"]] += 1
            text_content = data.get("title", "") + " " + data.get("abstract", "")
            words = text_content.lower().split()
            for word in words:
                cleaned_word = ''.join(filter(str.isalpha, word))
                if cleaned_word and cleaned_word not in STOPWORDS:
                    word_counts[cleaned_word] += 1
    
    print(f"\n{Fore.WHITE}--- Overall Summary ---")
    print(f"{Fore.GREEN}Total Articles Approved by AI: {Style.BRIGHT}{total_articles}")

    display_top_items("Most Relevant Source Queries", query_counts)
    display_top_items("Top Keywords in Relevant Papers", word_counts, top_n=10)


def run_statistics_analyzer():
    """Displays the statistics menu and calls the appropriate analysis function."""
    while True:
        print(f"\n{Fore.CYAN}--- Statistics Analyzer Menu ---")
        print(f"{Fore.YELLOW}1. Analyze AutoSearch Results")
        print(f"{Fore.YELLOW}2. Analyze AI Filter Results")
        print(f"{Fore.YELLOW}3. Return to Main Menu")
        
        choice = input(f"\n{Fore.CYAN}Enter your choice (1-3): {Style.RESET_ALL}")
        
        if choice == "1":
            analyze_autosearch()
        elif choice == "2":
            analyze_llama_filter()
        elif choice == "3":
            break
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please enter 1, 2, or 3.")