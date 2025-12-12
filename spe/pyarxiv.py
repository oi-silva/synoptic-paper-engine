# pyarxiv.py

import arxiv
import pandas as pd
import os
import requests
import re
from colorama import Fore, Style
from tqdm import tqdm  # Progress bar support

def sanitize_filename(filename):
    """Clean string for filename usage."""
    clean_name = re.sub(r'[\\/*?:"<>|]', "", filename)
    clean_name = " ".join(clean_name.split())
    return clean_name[:150]

class ArxivTool:
    def __init__(self, max_results_per_query=10):
        self.max_results = max_results_per_query
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=3.0,
            num_retries=3
        )

    def run_search(self, query_list, output_folder, min_year=None, max_year=None, min_citations=0):
        """
        Executes the search, download, and CSV generation logic.
        """
        # Create folders
        pdf_dir = os.path.join(output_folder, "pdfs")
        os.makedirs(pdf_dir, exist_ok=True)
        
        print(f"\n{Fore.GREEN}--> Output directory: {output_folder}")
        print(f"{Fore.GREEN}--> PDF directory: {pdf_dir}")
        
        if min_citations > 0:
            print(f"{Fore.YELLOW}⚠️  Note: The ArXiv API does not provide citation counts natively.")
            print(f"{Fore.YELLOW}    The 'Minimum Citations' filter will be ignored for this search.")

        all_results = {} 

        # 1. Search Phase
        print(f"\n{Fore.CYAN}-------------------- Starting ArXiv Search ---------------------")
        for i, query_str in enumerate(query_list):
            print(f"{Fore.BLUE}Query [{i+1}/{len(query_list)}]: {Style.BRIGHT}{query_str}")
            
            try:
                search = arxiv.Search(
                    query=query_str,
                    max_results=self.max_results,
                    sort_by=arxiv.SortCriterion.Relevance
                )

                results_gen = self.client.results(search)

                for r in results_gen:
                    # Date Filtering
                    pub_year = r.published.year
                    if min_year and pub_year < min_year:
                        continue
                    if max_year and pub_year > max_year:
                        continue

                    # Deduplication
                    if r.entry_id not in all_results:
                        all_results[r.entry_id] = {
                            'arxiv_id': r.entry_id.split('/')[-1],
                            'title': r.title,
                            'authors': ", ".join([a.name for a in r.authors]),
                            'published_date': r.published.date(),
                            'year': pub_year,
                            'summary': r.summary.replace("\n", " "),
                            'pdf_url': r.pdf_url,
                            'query_origin': query_str
                        }
            except Exception as e:
                print(f"{Fore.RED}❌ Error processing query '{query_str}': {e}")

        # 2. Download Phase
        unique_count = len(all_results)
        if unique_count == 0:
            print(f"\n{Fore.RED}❌ No articles found matching the criteria.")
            return
        
        print(f"\n{Fore.YELLOW}This might take a while... grab a coffee! ☕{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}Found {unique_count} unique articles. Starting downloads...")
        
        final_data = []
        
        # --- UPDATE: PROGRESS BAR ---
        # Using tqdm to wrap the loop. 'unit' defines the item label (e.g., 5/10 pdfs)
        # Internal print statements removed to keep the terminal clean.
        with tqdm(total=unique_count, desc="Downloading PDFs", unit="pdf", colour="green", ncols=65, bar_format='{l_bar}{bar}| [{elapsed}]') as pbar:
            for entry_id, data in all_results.items():
                safe_title = sanitize_filename(data['title'])
                pdf_filename = f"{safe_title}.pdf"
                pdf_path = os.path.join(pdf_dir, pdf_filename)
                
                data['local_path'] = pdf_path
                
                try:
                    response = requests.get(data['pdf_url'], timeout=30)
                    if response.status_code == 200:
                        with open(pdf_path, 'wb') as f:
                            f.write(response.content)
                    else:
                        # Silent failure (process continues, file is simply not saved)
                        pass
                except Exception:
                    # Silent exception (network error, timeout, etc.)
                    pass
                
                # Add metadata to final list regardless of download success
                # (Ensures the link exists in CSV for manual retrieval if needed)
                final_data.append(data)
                
                # Update progress bar
                pbar.update(1)

        # 3. Save CSV
        df = pd.DataFrame(final_data)
        csv_path = os.path.join(output_folder, "arxiv_results.csv")

        cols = ['title', 'year', 'authors', 'query_origin', 'pdf_url', 'local_path', 'summary']

        cols = [c for c in cols if c in df.columns]
        df = df[cols]
        
        df.to_csv(csv_path, index=False)
        print(f"\n{Fore.CYAN}🏁 Process finished! CSV saved at: {Style.BRIGHT}{csv_path}{Style.RESET_ALL}")

        print(f"\n{Fore.YELLOW}💡 Recommendation:{Style.RESET_ALL}")
        print(f"   To consolidate data, remove duplicates, and view global statistics,")
        print(f"   please run {Fore.CYAN}Option 6 (Analyze Results){Style.RESET_ALL} from the main menu.")