# llama_filter.py

import os
import csv
import sys
import shutil # Added for file copying
from colorama import Fore, Style, init
from tqdm import tqdm

from . import cross_validator as cv

# Attempt imports with specific error handling for llama-cpp-python
try:
    from llama_cpp import Llama
except ImportError:
    print(f"{Fore.RED}❌ Error: 'llama-cpp-python' is not installed.")
    print("Please select Option 6 in the main menu to install it.")
    sys.exit(1)

# Optional dependency: huggingface_hub
try:
    from huggingface_hub import hf_hub_download
except ImportError:
    # Silent fallback; specific errors handled in download function
    pass

init(autoreset=True)

# --- MODEL CONFIGURATION ---
# Using a lightweight, CPU-capable model (Qwen 2.5 1.5B)
REPO_ID = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
FILENAME = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_DIR = "models"

def download_model_if_needed():
    """Auto-download GGUF model from HuggingFace if missing locally."""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    model_path = os.path.join(MODEL_DIR, FILENAME)
    
    if not os.path.exists(model_path):
        print(f"\n{Fore.YELLOW}⚠️  Model not found locally.")
        print(f"{Fore.CYAN}⬇️  Downloading concise AI model ({FILENAME})... This happens only once.")
        try:
            from huggingface_hub import hf_hub_download
            model_path = hf_hub_download(
                repo_id=REPO_ID, 
                filename=FILENAME, 
                local_dir=MODEL_DIR, 
                local_dir_use_symlinks=False
            )
            print(f"{Fore.GREEN}✅ Model downloaded to: {model_path}")
        except ImportError:
            print(f"{Fore.RED}❌ Error: 'huggingface_hub' library missing.")
            print("Run: pip install huggingface_hub")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}❌ Download failed: {e}")
            sys.exit(1)
            
    return model_path

def get_user_criteria():
    """Collects filter criteria via CLI."""
    print(f"\n{Fore.CYAN}------------------- AI Filter Configuration --------------------{Style.RESET_ALL}")
    
    print(f"{Fore.WHITE}Define the persona for the AI (e.g., 'Senior Material Scientist'):")
    persona = input(f"{Fore.GREEN}> {Style.RESET_ALL}") or "Researcher"
    
    print(f"\n{Fore.WHITE}What is the specific Research Topic? (e.g., 'Graphene production'):")
    topic = input(f"{Fore.GREEN}> {Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}List inclusion criteria (e.g., 'Must focus on experimental \nresults, not theory'):")
    criteria = input(f"{Fore.GREEN}> {Style.RESET_ALL}")
    
    return persona, topic, criteria

def construct_prompt(persona, topic, criteria, title, abstract):
    """Builds the prompt template for Llama."""
    return f"""<|im_start|>system
You are a {persona}. Your task is to screen academic papers for a literature review on "{topic}".
Criteria for inclusion: {criteria}.
Reply ONLY with "YES" if the paper is relevant, or "NO" if it is not. Do not provide explanations.<|im_end|>
<|im_start|>user
Paper Title: {title}
Abstract: {abstract}

Is this paper relevant based on the criteria? Reply YES or NO.<|im_end|>
<|im_start|>assistant
"""

def filter_with_llama(input_folder, output_folder):
    """
    Main entry point. 
    Iterates through CSVs, runs inference, saves approved entries, 
    and copies relevant PDFs to the output folder.
    """
    # 1. Setup Model
    model_path = download_model_if_needed()
    
    print(f"\n{Fore.CYAN}🚀 Loading AI Model... (This may take a moment){Style.RESET_ALL}")
    # n_ctx=4096 covers abstract + prompt. verbose=False suppresses low-level logs.
    llm = Llama(model_path=model_path, n_ctx=4096, verbose=False, n_gpu_layers=-1) 
    
    # 2. Input Collection
    persona, topic, criteria = get_user_criteria()
    
    # 3. File Setup & Pre-counting for Progress Bar
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv') and not f.startswith("output_statistics")]
    
    if not csv_files:
        print(f"{Fore.RED}❌ No valid article CSV files found to process.")
        return

    print(f"\n{Fore.YELLOW}📊 Calculating total workload...{Style.RESET_ALL}")
    total_articles = 0
    for filename in csv_files:
        try:
            with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
                # Count lines minus header (if file not empty)
                row_count = sum(1 for _ in f) - 1
                total_articles += max(0, row_count)
        except Exception:
            continue

    output_csv = os.path.join(output_folder, "llama_filtered_articles.csv")
    
    # Create subfolder for approved PDFs
    if input_folder.startswith("arxiv_"):
        approved_pdfs_dir = os.path.join(output_folder, "approved_pdfs")
        os.makedirs(approved_pdfs_dir, exist_ok=True)

    total_processed = 0
    approved_count = 0
    copied_pdfs = 0
    
    print(f"\n{Fore.GREEN}⚡ Starting Inference on {total_articles} articles...{Style.RESET_ALL}")
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        # Initialize Writer
        # Added 'Local_PDF_Copy' to track where the file went
        fieldnames = ["Title", "Year", "Citations", "Authors", "URL", "Abstract", "AI_Decision", "Local_PDF_Copy"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Initialize Progress Bar
        with tqdm(total=total_articles, unit="paper", desc="AI Analysis", colour="green", ncols=65, bar_format='{l_bar}{bar}| [{elapsed}]') as pbar:
            for filename in csv_files:
                file_path = os.path.join(input_folder, filename)
                
                with open(file_path, 'r', encoding='utf-8') as infile:
                    reader = csv.DictReader(infile)
                    
                    for row in reader:
                        # --- NORMALIZATION ---
                        title = row.get("Title") or row.get("title")
                        abstract = row.get("Abstract") or row.get("summary") or row.get("abstract")
                        local_path = row.get("local_path") # ArXiv results usually have this
                        
                        if not title or not abstract:
                            pbar.update(1) 
                            continue
                            
                        save_row = {
                            "Title": title,
                            "Year": row.get("Year") or row.get("year"),
                            "Citations": row.get("Citations") or row.get("citationCount") or 0,
                            "Authors": row.get("Authors") or row.get("authors"),
                            "URL": row.get("URL") or row.get("pdf_url") or row.get("url"),
                            "Abstract": abstract,
                            "Local_PDF_Copy": "" # Default empty
                        }

                        # --- INFERENCE ---
                        prompt = construct_prompt(persona, topic, criteria, title, abstract)
                        
                        output = llm(prompt, max_tokens=5, stop=["<|im_end|>", "\n"], echo=False)
                        decision = output['choices'][0]['text'].strip().upper()
                        
                        clean_decision = "YES" if "YES" in decision else "NO"
                        
                        if clean_decision == "YES":
                            save_row["AI_Decision"] = "YES"
                            
                            # --- PDF COPY LOGIC ---
                            # If the original CSV indicates a local PDF path and the file exists
                            if local_path and os.path.exists(local_path):
                                try:
                                    pdf_filename = os.path.basename(local_path)
                                    dest_path = os.path.join(approved_pdfs_dir, pdf_filename)
                                    shutil.copy2(local_path, dest_path)
                                    save_row["Local_PDF_Copy"] = dest_path
                                    copied_pdfs += 1
                                except Exception as e:
                                    # Non-blocking error logging
                                    pass

                            writer.writerow(save_row)
                            outfile.flush()
                            approved_count += 1
                            
                        total_processed += 1
                        pbar.update(1)

    print(f"\n{Fore.GREEN}🏁 Filtering Complete!{Style.RESET_ALL}")
    print(f"Processed: {total_processed}")
    print(f"Approved: {approved_count}")
    if input_folder.startswith("arxiv_"):
        print(f"PDFs Copied: {copied_pdfs}")
    print(f"Results saved in: {output_csv}")

    # --- CROSS VALIDATION STEP ---
    cv.save_metadata(output_folder, input_folder, filter_type="AI")
    
    cv.run_comparison(output_folder, current_filter_type="AI")