import os
import csv
import sys
from colorama import Fore, Style, init

# Tenta importar as bibliotecas necessárias
try:
    from llama_cpp import Llama
except ImportError:
    print(f"{Fore.RED}❌ Error: 'llama-cpp-python' is not installed.")
    print("Please select Option 6 in the main menu to install it.")
    sys.exit(1)

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    # Fallback silencioso ou instalação automática se desejar, 
    # mas aqui vamos apenas pedir para instalar se falhar
    pass

init(autoreset=True)

# --- CONFIGURAÇÃO DO MODELO ---
# Usaremos um modelo leve e muito capaz (Qwen 2.5 1.5B ou TinyLlama) para rodar rápido em CPU
REPO_ID = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
FILENAME = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_DIR = "models"

def download_model_if_needed():
    """Baixa o modelo GGUF automaticamente do HuggingFace se não existir."""
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
    """Coleta os critérios do usuário via terminal."""
    print(f"\n{Fore.CYAN}--- AI Filter Configuration ---{Style.RESET_ALL}")
    
    print(f"{Fore.WHITE}Define the persona for the AI (e.g., 'Senior Material Scientist'):")
    persona = input(f"{Fore.GREEN}> {Style.RESET_ALL}") or "Researcher"
    
    print(f"\n{Fore.WHITE}What is the specific Research Topic? (e.g., 'Graphene production'):")
    topic = input(f"{Fore.GREEN}> {Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}List inclusion criteria (e.g., 'Must focus on experimental results, not theory'):")
    criteria = input(f"{Fore.GREEN}> {Style.RESET_ALL}")
    
    return persona, topic, criteria

def construct_prompt(persona, topic, criteria, title, abstract):
    """Monta o prompt para o Llama."""
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
    Função principal chamada pelo main.py.
    Lê CSVs, roda o Llama e salva os aprovados.
    """
    # 1. Preparar Modelo
    model_path = download_model_if_needed()
    
    print(f"\n{Fore.CYAN}🚀 Loading AI Model... (This may take a moment){Style.RESET_ALL}")
    # n_ctx=2048 é suficiente para abstract + prompt. verbose=False limpa o terminal.
    llm = Llama(model_path=model_path, n_ctx=4096, verbose=False, n_gpu_layers=-1) 
    
    # 2. Coletar Inputs
    persona, topic, criteria = get_user_criteria()
    
    # 3. Preparar Arquivos
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    output_csv = os.path.join(output_folder, "llama_filtered_articles.csv")
    
    total_processed = 0
    approved_count = 0
    
    print(f"\n{Fore.GREEN}⚡ Starting Inference on {len(csv_files)} files...{Style.RESET_ALL}")
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        # Inicializa o Writer
        fieldnames = ["Title", "Year", "Citations", "Authors", "URL", "Abstract", "AI_Decision"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for filename in csv_files:
            file_path = os.path.join(input_folder, filename)
            
            with open(file_path, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                
                for row in reader:
                    # --- NORMALIZAÇÃO (ArXiv vs Semantic Scholar) ---
                    # Tenta pegar Capitalizado (Semantic) ou minúsculo (Arxiv)
                    title = row.get("Title") or row.get("title")
                    abstract = row.get("Abstract") or row.get("summary") or row.get("abstract")
                    
                    # Se não tem resumo, não dá pra avaliar bem
                    if not title or not abstract:
                        continue
                        
                    # Prepara dados para salvar (Unifica formato)
                    save_row = {
                        "Title": title,
                        "Year": row.get("Year") or row.get("year"),
                        "Citations": row.get("Citations") or row.get("citationCount") or 0,
                        "Authors": row.get("Authors") or row.get("authors"),
                        "URL": row.get("URL") or row.get("pdf_url") or row.get("url"),
                        "Abstract": abstract
                    }

                    # --- INFERÊNCIA ---
                    prompt = construct_prompt(persona, topic, criteria, title, abstract)
                    
                    # Roda o modelo
                    output = llm(prompt, max_tokens=5, stop=["<|im_end|>", "\n"], echo=False)
                    decision = output['choices'][0]['text'].strip().upper()
                    
                    # Limpeza simples da resposta (caso venha "YES." ou "YES - ...")
                    clean_decision = "YES" if "YES" in decision else "NO"
                    
                    print(f"Analyzing: {title[:50]}... -> {Fore.CYAN}{clean_decision}{Style.RESET_ALL}")
                    
                    if clean_decision == "YES":
                        save_row["AI_Decision"] = "YES"
                        writer.writerow(save_row)
                        outfile.flush() # Garante que salve a cada linha
                        approved_count += 1
                        
                    total_processed += 1

    print(f"\n{Fore.GREEN}🏁 Filtering Complete!{Style.RESET_ALL}")
    print(f"Processed: {total_processed}")
    print(f"Approved: {approved_count}")
    print(f"Results saved in: {output_csv}")