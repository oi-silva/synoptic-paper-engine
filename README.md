# Synoptic Paper Engine ✨

**Synoptic Paper Engine (SPE)** is a powerful command-line interface (CLI) tool designed to streamline and automate the process of academic literature review. It leverages the Semantic Scholar API to perform large-scale bibliographic searches and uses a local AI model (Llama 3) to perform contextual analysis and filtering of the results.

This tool is perfect for researchers, students, and anyone who needs to quickly gather, filter, and analyze a large volume of academic papers on a specific topic.

---

## 🚀 Key Features

* **Advanced Bibliographic Search**:
    * Connects to the **Semantic Scholar API** for comprehensive searches.
    * Supports complex **Boolean queries** with `AND`, `OR`, `NOT`, and nested parentheses `(...)` for precise searching.
    * Pre-filters results based on **minimum citation count** and **year range**.

* **🤖 AI-Powered Filtering**:
    * Integrates a **local Llama 3 model** to "read" the title and abstract of each paper.
    * Allows users to define a custom **expert persona, research topic, and evaluation criteria** for the AI.
    * Intelligently filters papers based on their contextual relevance, not just keywords.

* **📊 In-depth Analysis**:
    * Analyzes both the initial search results and the AI-filtered results.
    * Generates statistics on the **most productive years**, **most prolific authors**, and **most cited papers**.
    * Exports all analysis data to CSV files in a `log/` directory for further use.

* **⚙️ User-Friendly Interface**:
    * A simple and intuitive menu-driven CLI.
    * Interactive prompts guide the user through every step.
    * Built-in help menus explain all features and associated risks.
    * Safe-guards like a confirmation preview before executing large searches.

---

## 🔧 Installation

The project is designed to be installed directly from its GitHub repository using `pip`.

**Prerequisites:**
* Python 3.8+
* Git

To install the Synoptic Paper Engine, run the following command in your terminal:

```bash
pip install git+[https://github.com/oi-silva/synoptic-paper-engine.git](https://github.com/oi-silva/synoptic-paper-engine.git)
```

This command will download the project and install all the required Python dependencies automatically.

---

## 🔄 Updating the Tool

To update your installation to the latest version from the repository, you need to re-run the installation command with the `--upgrade` and `--no-cache-dir` flags.

```bash
pip install --upgrade --no-cache-dir git+[https://github.com/oi-silva/synoptic-paper-engine.git](https://github.com/oi-silva/synoptic-paper-engine.git)
```

* `--upgrade`: Tells `pip` to update the package to the newest version.
* `--no-cache-dir`: This is crucial. It forces `pip` to fetch the latest code from GitHub instead of using a cached, older version.

---

## Usage

Once installed, you can run the tool as a Python module from your terminal:

```bash
spe
```

This will launch the main menu, where you can choose from the following options:

#### 1. Run Bibliographic Search
This option allows you to perform a large-scale search on Semantic Scholar. You will be prompted to:
- Enter your complex query.
- Set optional filters for minimum citations and publication year.
- Configure batch size and the number of batches to retrieve.
The results are saved as multiple CSV files inside a `results/` folder.

#### 2. Filter Papers with AI (Llama)
After running a search, use this option to apply contextual filtering.
- First, you will choose which `results/` folder to process.
- Then, you will be guided to create a prompt for the AI by defining:
  - An **expert persona** (e.g., "a biochemist").
  - A **research topic** (e.g., "the role of CRISPR in gene therapy").
  - Specific **evaluation criteria**.
- The AI will process each paper and save the relevant ones to a new folder named `llama_filtered/`.

#### 3. Analyze Results
This option generates and displays statistics for the papers you have collected. You can choose to analyze either a `results/` folder from a bibliographic search or a `llama_filtered/` folder from an AI filtering session.

#### 4. Help / Information
Displays a detailed help menu that explains how to construct queries, use the AI filter effectively, and understand the risks and limitations of the AI.

---

## ⚠️ Important Note on the AI Filter

The AI filtering feature uses `llama-cpp-python` to run a 4-bit quantized version of **Meta-Llama-3-8B-Instruct**.

* **Automatic Download**: The first time you run the AI filter, the script will automatically download the model file (~4.7 GB). This may take a few minutes.
* **Resource Usage**: Running the model is CPU-intensive and requires a significant amount of RAM. Performance will vary depending on your hardware.
* **Disclaimer**: The AI is a powerful assistant for initial screening, but it is not a replacement for expert human judgment. Always critically evaluate its outputs.

---

## Dependencies

The installer will handle these automatically, but for reference, the main dependencies are:
* `requests`
* `colorama`
* `tqdm`
* `llama-cpp-python`

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
