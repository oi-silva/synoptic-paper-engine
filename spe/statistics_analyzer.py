# statistics_analyzer.py

import os
import csv
from collections import Counter
from colorama import init, Fore, Style

# Try to import matplotlib for plotting capabilities
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

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

def get_output_filepath(directory, filename):
    """
    Returns the file path. Ensures the directory exists.
    Does NOT add unique suffixes, allowing files to be overwritten.
    """
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, filename)

def display_header(title):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 64}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(64)}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 64}{Style.RESET_ALL}")

def display_top_items(title, counter, top_n=5):
    print(f"\n{Fore.YELLOW}--- {title} (Top {top_n}) ---{Style.RESET_ALL}")
    if not counter:
        print(f"{Fore.WHITE}No data to display.")
        return
    for item, count in counter.most_common(top_n):
        print(f"{Fore.GREEN}{item}: {Style.BRIGHT}{count} mentions")

def save_stats_to_csv(data_list, filename, fieldnames):
    """Saves a list of dictionaries to a CSV file."""
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_list)
    print(f"{Fore.GREEN}✅ Statistics saved to '{filename}'")

def save_counter_to_csv(counter_obj, directory, filename, fieldnames):
    """Converts a Counter object to a list of dictionaries and saves it to a CSV file."""
    if not counter_obj:
        return
        
    # Convert Counter to a list of dictionaries
    data_list = [{fieldnames[0]: item, fieldnames[1]: count} for item, count in counter_obj.most_common()]
    
    # Get the file path (overwriting existing)
    filepath = get_output_filepath(directory, filename)
    save_stats_to_csv(data_list, filepath, fieldnames)

def plot_year_distribution(year_counter, output_folder, title_suffix=""):
    """
    Generates and saves a bar chart showing the distribution of papers per year.
    Requires matplotlib.
    """
    if not HAS_MATPLOTLIB or not year_counter:
        return

    # Filter out invalid years (non-numeric) and sort chronologically
    valid_years = {k: v for k, v in year_counter.items() if str(k).isdigit()}
    
    if not valid_years:
        return

    sorted_years = sorted(valid_years.keys(), key=lambda x: int(x))
    counts = [valid_years[y] for y in sorted_years]

    plt.figure(figsize=(10, 6))
    
    # Create bar chart
    bars = plt.bar(sorted_years, counts, color='skyblue', edgecolor='navy', alpha=0.7)
    
    # Add labels and title in English
    plt.xlabel('Publication Year', fontsize=16)
    plt.ylabel('Number of Articles', fontsize=16)
    plt.title(f'Publication Trend', fontsize=16)
    plt.xticks(rotation=90, fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Annotate bars with values
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height}',
                 ha='center', va='bottom', fontsize=12)

    plt.tight_layout()
    
    # Save the plot
    filename = "timeline_plot.png"
    save_path = os.path.join(output_folder, filename)
    plt.savefig(save_path, dpi=300)
    plt.close() # Close figure to free memory
    
    print(f"{Fore.GREEN}📊 Chart saved to: {save_path}{Style.RESET_ALL}")

def plot_top_authors(author_counter, output_folder, top_n=10):
    """
    Generates a horizontal bar chart for the most prolific authors.
    """
    if not HAS_MATPLOTLIB or not author_counter:
        return

    # Get top N authors
    most_common = author_counter.most_common(top_n)
    if not most_common:
        return

    # Unpack data (reverse to have top author at the top of chart)
    authors = [x[0] for x in most_common][::-1]
    counts = [x[1] for x in most_common][::-1]

    plt.figure(figsize=(10, 8))
    
    # Horizontal bar chart
    bars = plt.barh(authors, counts, color='lightgreen', edgecolor='darkgreen', alpha=0.8)
    
    plt.xlabel('Number of Articles', fontsize=16)
    plt.title(f'Top {top_n} Prolific Authors', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis='x', linestyle='--', alpha=0.5)

    # Annotate values
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                 f' {width}',
                 va='center', fontsize=12)

    plt.tight_layout()
    
    filename = "top_authors_plot.png"
    save_path = os.path.join(output_folder, filename)
    plt.savefig(save_path, dpi=300)
    plt.close()
    
    print(f"{Fore.GREEN}📊 Chart saved to: {save_path}{Style.RESET_ALL}")

def plot_citation_distribution(papers_list, output_folder):
    """
    Generates a histogram showing how citations are distributed among papers.
    """
    if not HAS_MATPLOTLIB or not papers_list:
        return

    # Extract citations (exclude 0 if you want, or keep them to show uncited papers)
    citations = [p['citations'] for p in papers_list if p.get('citations') is not None]
    
    if all(x == 0 for x in citations):
        return

    plt.figure(figsize=(10, 6))
    
    # Histogram
    plt.hist(citations, bins=30, color='salmon', edgecolor='black', alpha=0.7)
    
    plt.xlabel('Number of Citations', fontsize=16)
    plt.ylabel('Frequency (Number of Papers)', fontsize=16)
    plt.title('Citation Distribution', fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    
    plt.tight_layout()
    
    filename = "citation_histogram.png"
    save_path = os.path.join(output_folder, filename)
    plt.savefig(save_path, dpi=300)
    plt.close()
    
    print(f"{Fore.GREEN}📊 Chart saved to: {save_path}{Style.RESET_ALL}")

def analyze_general_csv_folder(folder_path):
    """
    Analyzes generic CSV folders (Raw results, ArXiv results, or Content Filtered CSVs).
    Capable of normalizing different column names across data sources.
    """
    display_header(f"Statistics for '{folder_path}'")
    
    if not os.path.exists(folder_path):
        print(f"{Fore.RED}❌ Folder '{folder_path}' does not exist.")
        return

    # Look for all CSVs in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    if not csv_files:
        print(f"{Fore.RED}❌ No CSV files found in '{folder_path}'.")
        return

    year_counts = Counter()
    author_counts = Counter()
    all_papers = []
    processed_titles = set()
    total_articles = 0
    contains_arxiv_data = False
    
    # Check context based on folder name/path to determine source type
    folder_name = os.path.basename(os.path.normpath(folder_path))
    is_arxiv_folder = "arxiv" in folder_name.lower()

    print(f"Analyzing {len(csv_files)} files...")
    for filename in csv_files:
        filepath = os.path.join(folder_path, filename)
        
        # Additional check if individual file is arxiv-related
        if filename.startswith("arxiv_"): 
            contains_arxiv_data = True
        elif is_arxiv_folder:
            contains_arxiv_data = True

        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # ---------------------------------------------------------
                # DATA NORMALIZATION (Handles Semantic Scholar, ArXiv, and Content Filtered)
                # ---------------------------------------------------------
                # Title: Try various common keys
                raw_title = row.get("Title") or row.get("title") or ""
                
                # Year
                raw_year = row.get("Year") or row.get("year") or "0"
                
                # Authors
                raw_authors = row.get("Authors") or row.get("authors") or ""
                
                # Citations
                raw_citations = row.get("Citations") or row.get("citationCount") or row.get("citations") or 0
                
                # URL
                raw_url = row.get("URL") or row.get("url") or row.get("pdf_url") or ""

                title = raw_title.strip()
                if not title or title.upper() == "N/A":
                    continue
                
                # Deduplication logic using normalized title
                title_key = " ".join(title.lower().split())
                if title_key in processed_titles:
                    continue
                
                processed_titles.add(title_key)
                total_articles += 1

                # Update Counters
                if raw_year and str(raw_year).isdigit(): 
                    year_counts[raw_year] += 1
                
                if raw_authors: 
                    normalized_authors = raw_authors.replace(";", ",")
                    author_list = [a.strip() for a in normalized_authors.split(',') if a.strip()]
                    author_counts.update(author_list)

                try:
                    paper_data = {
                        "title": title,
                        "citations": int(float(raw_citations)), # Handle strings like "10.0"
                        "authors": raw_authors,
                        "url": raw_url,
                        "source": "ArXiv" if contains_arxiv_data else "Semantic/Filtered"
                    }
                    all_papers.append(paper_data)
                except (ValueError, TypeError):
                    continue

    sorted_papers = sorted(all_papers, key=lambda p: p['citations'], reverse=True)
    
    # -----------------------------------------------------------
    # DEFINE LOG DIRECTORY
    # -----------------------------------------------------------
    log_directory = os.path.join("log", folder_name)
    os.makedirs(log_directory, exist_ok=True)
    
    print(f"\n{Fore.CYAN}📂 Saving statistics to: {Style.BRIGHT}{log_directory}")

    # Save CSV Data
    if sorted_papers:
        save_stats_to_csv(
            sorted_papers, 
            get_output_filepath(log_directory, "top_papers.csv"), # CHANGE: Use overwrite function
            ["title", "citations", "authors", "url", "source"]
        )
    
    save_counter_to_csv(year_counts, log_directory, "productive_years.csv", ["Year", "Article_Count"])
    save_counter_to_csv(author_counts, log_directory, "prolific_authors.csv", ["Author", "Article_Count"])

    # Generate Plots
    if HAS_MATPLOTLIB:
        plot_year_distribution(year_counts, log_directory, title_suffix=folder_name)
        plot_top_authors(author_counts, log_directory)
        plot_citation_distribution(all_papers, log_directory)
    else:
        print(f"{Fore.YELLOW}⚠️ Matplotlib not found. Charts will not be generated.")

    # Output Summary to Console
    print(f"\n{Fore.WHITE}--- Overall Summary ---")
    print(f"{Fore.GREEN}Total Articles Analyzed: {Style.BRIGHT}{total_articles}")
    print(f"{Fore.GREEN}Unique Articles Found: {Style.BRIGHT}{len(processed_titles)}")

    display_top_items("Most Productive Years", year_counts)
    display_top_items("Most Prolific Authors", author_counts)

    print(f"\n{Fore.YELLOW}--- Top {5} Most Cited Papers ---{Style.RESET_ALL}")
    
    if contains_arxiv_data and not any(p['citations'] > 0 for p in sorted_papers):
        print(f"{Fore.WHITE}Note: ArXiv papers do not contain citation data via API.")
        print(f"{Fore.WHITE}Showing most recent papers instead:")
        recent_papers = sorted(all_papers, key=lambda x: x.get('year', 0), reverse=True)[:5]
        for i, paper in enumerate(recent_papers):
             print(f"{Fore.WHITE}{i+1}. {Fore.GREEN}{paper['title'][:67]}... \n   {Style.DIM}{Fore.WHITE}└─ Source: {paper['source']}{Style.RESET_ALL}")
    
    elif not sorted_papers:
        print(f"{Fore.WHITE}No papers found.")
    else:
        for i, paper in enumerate(sorted_papers[:5]):
            title = paper['title']
            if len(title) > 70: title = title[:67] + "..."
            cit_info = f"Citations: {paper['citations']}"
            print(f"{Fore.WHITE}{i+1}. {Fore.GREEN}{title} \n   {Style.DIM}{Fore.WHITE}└─ {cit_info} | Source: {paper['source']}{Style.RESET_ALL}")

def analyze_llama_csv_results(folder_path):
    """
    Analyzes the specific CSV file generated by the AI Llama filter.
    """
    display_header("AI Filter Results Statistics")

    csv_file = os.path.join(folder_path, "llama_filtered_articles.csv")
    if not os.path.exists(csv_file):
        print(f"{Fore.RED}❌ File '{csv_file}' not found. Please run the AI filter first.")
        return

    year_counts = Counter()
    author_counts = Counter()
    all_papers = []
    processed_titles = set()
    total_articles = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_articles += 1
            # Keys in Llama output are standard: Title, Year, Authors, Citations
            title = row.get("Title", row.get("title", "")).strip()
            
            if not title or title.upper() == "N/A": continue

            title_key = " ".join(title.lower().split())
            if title_key in processed_titles: continue

            processed_titles.add(title_key)

            year = row.get("Year", row.get("year", ""))
            if year: year_counts[year] += 1
            
            authors = row.get("Authors", row.get("authors", ""))
            if authors: 
                 normalized_authors = authors.replace(";", ",")
                 author_counts.update([a.strip() for a in normalized_authors.split(',') if a.strip()])
            
            try:
                cit_val = row.get("Citations", row.get("citations", 0))
                all_papers.append({
                    "title": title,
                    "citations": int(float(cit_val)),
                    "authors": authors,
                    "url": row.get("URL", row.get("pdf_url", "N/A"))
                })
            except (ValueError, TypeError):
                continue
    
    sorted_papers = sorted(all_papers, key=lambda p: p['citations'], reverse=True)

    folder_name = os.path.basename(os.path.normpath(folder_path))
    log_directory = os.path.join("log", folder_name)
    os.makedirs(log_directory, exist_ok=True)

    print(f"\n{Fore.CYAN}📂 Saving statistics to: {Style.BRIGHT}{log_directory}")

    # Save CSV Data
    if sorted_papers:
        save_stats_to_csv(
            sorted_papers, 
            get_output_filepath(log_directory, "top_papers.csv"), # CHANGE: Use overwrite function
            ["title", "citations", "authors", "url"]
        )

    save_counter_to_csv(year_counts, log_directory, "productive_years.csv", ["Year", "Article_Count"])
    save_counter_to_csv(author_counts, log_directory, "prolific_authors.csv", ["Author", "Article_Count"])
    
    # Generate Plots
    if HAS_MATPLOTLIB:
        plot_year_distribution(year_counts, log_directory, title_suffix="AI Filter (Llama)")
        plot_top_authors(author_counts, log_directory)
        plot_citation_distribution(all_papers, log_directory)

    print(f"\n{Fore.WHITE}--- Overall Summary ---")
    print(f"{Fore.GREEN}Total Articles Approved by AI: {Style.BRIGHT}{total_articles}")
    print(f"{Fore.GREEN}Unique Articles Found: {Style.BRIGHT}{len(processed_titles)}")

    display_top_items("Most Productive Years", year_counts)
    display_top_items("Most Prolific Authors", author_counts)

    print(f"\n{Fore.YELLOW}--- Top {5} Most Cited Papers ---{Style.RESET_ALL}")
    if not sorted_papers:
        print(f"{Fore.WHITE}No papers with citation data found.")
    else:
        for i, paper in enumerate(sorted_papers[:5]):
            title = paper['title']
            if len(title) > 70: title = title[:67] + "..."
            print(f"{Fore.WHITE}{i+1}. {Fore.GREEN}{title} \n   {Style.DIM}{Fore.WHITE}└─ Citations: {Style.BRIGHT}{paper['citations']}{Style.RESET_ALL}")

def run_analysis_interface():
    """
    Main entry point for the Analysis Module.
    Allows user to choose between Raw Data or Filtered Data.
    Dynamically scans folders to populate the menu.
    """
    print(f"\n{Fore.CYAN}--------------- Analyze Results (Graphs & Stats) ---------------\n")
    print(f"{Fore.YELLOW}1. Analyze Raw Search Data (results / arxiv_results)")
    print(f"{Fore.YELLOW}2. Analyze Filtered Data (content_filtered_csv / llama_filtered)")
    
    choice = input(f"\n{Fore.CYAN}Select data type: {Style.RESET_ALL}")
    

    potential_folders = []

    # === OPTION 1: RAW DATA (Root Directory) ===
    if choice == '1':
        print(f"\n{Fore.BLUE}🔍 Scanning for Raw Search folders...{Style.RESET_ALL}")
        
        # Search for folders starting with 'results' or 'arxiv_results' in root
        for entry in os.listdir('.'):
            if os.path.isdir(entry):
                if entry.startswith('results') or entry.startswith('arxiv_results'):
                    potential_folders.append(entry)

    # === OPTION 2: FILTERED DATA (Llama root OR CSV subfolders) ===
    elif choice == '2':
        print(f"\n{Fore.BLUE}🔍 Scanning for Filtered folders...{Style.RESET_ALL}")
        
        # 1. Look for 'llama_filtered' in root
        for entry in os.listdir('.'):
            if os.path.isdir(entry) and entry.startswith('llama_filtered'):
                potential_folders.append(entry)
        
        # 2. Look for subfolders inside 'content_filtered_csv'
        # Structure: content_filtered_csv/results-1/High_Relevance.csv
        cf_dir = 'content_filtered_csv'
        if os.path.exists(cf_dir) and os.path.isdir(cf_dir):
            for sub in os.listdir(cf_dir):
                full_path = os.path.join(cf_dir, sub)
                # Check if it is a directory before adding
                if os.path.isdir(full_path):
                    potential_folders.append(full_path)
    
    else:
        print(f"{Fore.RED}Invalid selection.")
        return

    # === DISPLAY AND SELECTION ===
    if not potential_folders:
        print(f"{Fore.RED}❌ No matching folders found for this category.")
        return

    print(f"\n{Fore.CYAN}Available Folders:{Style.RESET_ALL}")
    for i, folder in enumerate(potential_folders):
        # Display full path to differentiate subfolders
        print(f"{Fore.YELLOW}{i+1}. {folder}")

    try:
        sel_idx = int(input(f"\n{Fore.CYAN}Enter your choice: {Style.RESET_ALL}")) - 1
        if 0 <= sel_idx < len(potential_folders):
            selected_folder = potential_folders[sel_idx]
            
            # Dispatch to correct analyzer based on folder name/type
            if "llama_filtered" in selected_folder:
                analyze_llama_csv_results(selected_folder)
            else:
                # Handles 'results', 'arxiv_results' and subfolders in 'content_filtered_csv'
                analyze_general_csv_folder(selected_folder)
                
            input(f"\n{Fore.GREEN}Press Enter to return...{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid number.")
    except ValueError:
        print(f"{Fore.RED}Invalid input. Please enter a number.")