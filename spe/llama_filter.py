import os
import csv
import json
import sys
import re
from contextlib import contextmanager
from colorama import Fore, Style, init
from tqdm import tqdm  # <-- MUDANÇA: Importa a biblioteca tqdm

# Initializes colorama for a more visually appealing terminal output.
init(autoreset=True)

# Corrected context manager to suppress stdout and stderr.
@contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    with open(os.devnull, 'w') as f:
        sys.stdout = f
        sys.stderr = f
        try:
            yield
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

# Llama model setup
try:
    from llama_cpp import Llama
    print(f"{Fore.CYAN}Loading Llama model... (Logs are hidden){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}This may take a few minutes. Take a coffee while you wait! ☕{Style.RESET_ALL}")
    with suppress_stdout_stderr():
        llm = Llama.from_pretrained(
            repo_id="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
            filename="Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
        )
except ImportError:
    print(f"{Fore.RED}❌ ERROR: The 'llama-cpp-python' library is not installed.")
    print(f"Please install it using the following command: {Fore.GREEN}pip install llama-cpp-python{Style.RESET_ALL}")
    llm = None
except Exception as e:
    print(f"{Fore.RED}❌ ERROR: Could not load the Llama model.")
    print(f"Error details: {e}")
    llm = None


def get_user_prompt_criteria():
    """
    Prompts the user for information about the prompt, making it editable.
    """
    print(f"\n{Fore.CYAN}--- Llama Filter Customization ---{Style.RESET_ALL}")
    print(f"Please provide the following information for the Llama prompt.")
    print(f"You can customize the expert, topic, and criteria.")
    
    expert_persona = input(f"\n{Fore.YELLOW}What is the Llama's area of expertise?{Style.RESET_ALL} ")
    research_topic = input(f"{Fore.YELLOW}What is the specific research topic?{Style.RESET_ALL} ")
    
    criteria = []
    print(f"\n{Fore.YELLOW}Enter the evaluation criteria (one per line).{Style.DIM}")
    print(f"Press Enter on an empty line to finish.{Style.RESET_ALL}")
    
    while True:
        criterion = input(f"{Fore.GREEN}> {Style.RESET_ALL}")
        if not criterion:
            break
        criteria.append(criterion)

    if not expert_persona:
        expert_persona = "an expert researcher"
    if not research_topic:
        research_topic = "the provided scientific article"
    if not criteria:
        criteria = ["The title and abstract (if provide) are relevant to the area of interest."]
        
    return expert_persona, research_topic, criteria


def build_llama_prompt(expert_persona, research_topic, criteria_list, title, abstract):
    """
    Builds the dynamic prompt for the Llama model.
    """
    abstract_block = f"Abstract: {abstract}" if abstract else ""
    criteria_list_formatted = "\n* ".join(criteria_list)

    prompt = f"""
You are {expert_persona}.

Given the following scientific article, assess whether it is a high-quality and trustworthy reference for {research_topic}. Consider the following criteria:

* {criteria_list_formatted}

Respond only with one word: **True** or **False**.
---

Title: {title}

{abstract_block}
---
Answer:"""
    return prompt.strip()


def get_llama_completion(expert_persona, research_topic, criteria_list, title, abstract, max_retries=5, abstract_decrement=0.1):
    """
    Attempts to get a completion from the Llama model.
    """
    if not llm:
        return "False"

    current_abstract = abstract
    for attempt in range(max_retries):
        prompt = build_llama_prompt(expert_persona, research_topic, criteria_list, title, current_abstract)
        try:
            # Apply the context manager here to hide performance logs
            with suppress_stdout_stderr():
                response = llm.create_chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=5,
                    stop=["\n"]
                )
            
            content = response['choices'][0]['message']['content'].strip()
            return content
        except Exception as e:
            # Se ocorrer um erro, é útil mostrá-lo, mesmo com a barra de progresso
            tqdm.write(f"{Fore.YELLOW}⚠️  Attempt {attempt + 1} for '{title[:30]}...' failed: {e}")
            new_size = int(len(current_abstract) * (1 - abstract_decrement))
            if new_size < 50:
                tqdm.write(f"{Fore.RED}❌ The abstract was reduced to its minimum size and still caused an error. Skipping this article.")
                return "False"
            current_abstract = current_abstract[:new_size]
    tqdm.write(f"{Fore.RED}❌ Could not get a response after {max_retries} attempts for '{title[:30]}...'.")
    return "False"


def filter_with_llama(input_folder):
    """
    Reads CSV files, applies Llama-based filtering, and saves results incrementally.
    """
    if not llm:
        print(f"{Fore.RED}Llama model not loaded. Skipping this step.")
        return

    while True:
        expert_persona, research_topic, criteria_list = get_user_prompt_criteria()
        print(f"\n{Fore.CYAN}--- Prompt Preview ---{Style.RESET_ALL}")
        example_prompt = build_llama_prompt(
            expert_persona, research_topic, criteria_list,
            "[Example Article Title]", "[Example article abstract...]"
        )
        print(f"{Fore.LIGHTBLACK_EX}{example_prompt}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}--------------------{Style.RESET_ALL}")
        print("\nPlease review the generated prompt. What would you like to do?")
        print(f"{Fore.GREEN}(1) Approve and Start Filtering")
        print(f"{Fore.YELLOW}(2) Edit the Prompt Again")
        print(f"{Fore.RED}(3) Exit Program")
        choice = input(f"{Fore.WHITE}> {Style.RESET_ALL}")

        if choice == '1':
            print(f"\n{Fore.GREEN}✅ Prompt approved. Starting file filtering...{Style.RESET_ALL}")
            break
        elif choice == '2':
            print(f"\n{Fore.YELLOW}✏️ Returning to the prompt editor...{Style.RESET_ALL}")
            continue
        elif choice == '3':
            print(f"\n{Fore.RED}🛑 Exiting the program.{Style.RESET_ALL}")
            return
        else:
            print(f"\n{Fore.RED}Invalid option. Please choose 1, 2, or 3.{Style.RESET_ALL}")

    output_folder = "llama_filtered"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "llama_filtered_articles.jsonl")
    print(f"\n{Fore.CYAN}Results will be saved incrementally to: {output_path}{Style.RESET_ALL}")

    if not os.path.exists(input_folder):
        print(f"{Fore.YELLOW}⚠️ Input folder '{input_folder}' not found. Skipping Llama filtering.")
        return

    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    if not csv_files:
        print(f"{Fore.YELLOW}⚠️ No CSV files found in '{input_folder}'. Skipping Llama filtering.")
        return

    # <-- MUDANÇA: Contar o total de artigos antes de começar
    total_articles = 0
    print("Calculating total number of articles...")
    for filename in csv_files:
        filepath = os.path.join(input_folder, filename)
        with open(filepath, mode='r', encoding='utf-8') as f:
            # Soma as linhas e subtrai 1 para o cabeçalho
            total_articles += sum(1 for line in f) - 1
    
    articles_found_count = 0
    
    # <-- MUDANÇA: Abre o arquivo de saída
    with open(output_path, "w", encoding="utf-8") as outfile:
        # <-- MUDANÇA: Inicia a barra de progresso
        with tqdm(total=total_articles, desc="Filtering Articles", unit=" article") as pbar:
            for filename in csv_files:
                # Atualiza a descrição da barra com o arquivo atual
                pbar.set_description(f"Processing {os.path.basename(filename)}")
                filepath = os.path.join(input_folder, filename)
                
                with open(filepath, mode='r', newline='', encoding='utf-8') as infile:
                    reader = csv.DictReader(infile)
                    for row in reader:
                        query = row.get("Query", "")
                        title = row.get("Title", "")
                        abstract = row.get("Abstract", "")
                        url = row.get("URL", "")

                        if not title or not abstract:
                            pbar.update(1) # Pula o artigo, mas atualiza a barra
                            continue
                        
                        llama_response = get_llama_completion(expert_persona, research_topic, criteria_list, title, abstract)
                        normalized_response = llama_response.strip().lower()

                        if re.search(r'\btrue\b', normalized_response) and not re.search(r'\bfalse\b', normalized_response):
                            result_data = {
                                "query": query,
                                "title": title,
                                "abstract": abstract,
                                "url": url,
                                "llama_decision": llama_response
                            }
                            outfile.write(json.dumps(result_data, ensure_ascii=False) + '\n')
                            articles_found_count += 1
                        
                        # <-- MUDANÇA: Atualiza a barra de progresso em 1, independentemente do resultado
                        pbar.update(1)

    print(f"\n{Fore.GREEN}Done. Found and saved {articles_found_count} relevant articles.{Style.RESET_ALL}")

if __name__ == "__main__":
    filter_with_llama("input_data")