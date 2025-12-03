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

A instalação é feita diretamente do repositório GitHub usando `pip`. Abaixo estão as instruções para Windows e Linux/macOS.

### For Windows Users

**Step 1: Install Prerequisites (Python and Git)**

1.  **Install Python**:
    * Go to the official Python website: [python.org/downloads/](https://www.python.org/downloads/)
    * Download the latest installer.
    * Run the installer and **make sure to check the box that says "Add Python to PATH"** before you click "Install Now". This is a very important step.

2.  **Install Git**:
    * Go to the official Git website: [git-scm.com/download/win](https://git-scm.com/download/win)
    * Download and run the installer. You can safely use the default options for all installation steps.

**Step 2: Install Synoptic Paper Engine**

1.  Open the **Command Prompt** or **PowerShell** (you can find it in the Start Menu).
2.  Copy and paste the following command and press Enter:

```bash
pip install git+https://github.com/oi-silva/synoptic-paper-engine.git
```

### For Linux / macOS Users

**Step 1: Install Prerequisites (Python and Git)**

Python and Git are often pre-installed on Linux and macOS. You can check by opening your terminal and typing `python3 --version` and `git --version`. If they are not installed, follow these steps.

1.  **Install Python & Git (for Debian/Ubuntu)**:
    * Open your terminal and run the following command:

    ```bash
    sudo apt update && sudo apt install python3 python3-pip git -y
    ```
    * For other Linux distributions or macOS (using Homebrew), use the appropriate package manager commands.

**Step 2: Install Synoptic Paper Engine**

1.  Open your terminal.
2.  Run the following command:

```bash
pip install git+https://github.com/oi-silva/synoptic-paper-engine.git
```

---

## 🔄 Updating the Tool

To update your installation to the latest version from the repository, you need to re-run the installation command with the `--upgrade` and `--no-cache-dir` flags.

```bash
pip uninstall synoptic-paper-engine
pip install --upgrade --no-cache-dir git+https://github.com/oi-silva/synoptic-paper-engine.git
```

* `--upgrade`: Tells `pip` to update the package to the newest version.
* `--no-cache-dir`: This is crucial. It forces `pip` to fetch the latest code from GitHub instead of using a cached, older version.

---

## Usage

After a successful installation, you can run the tool directly from your terminal.

### On Windows

1.  Open **Command Prompt** or **PowerShell**.
2.  Type the following command to start the application:

```bash
python -m spe.main
```

### On Linux / macOS

1.  Open your terminal.
2.  Thanks to the setup process, you can use a shorter, direct command:

```bash
spe
```

This will launch the main menu, where you can choose from the following options:

1.  **Run Bibliographic Search**: Perform a large-scale search on Semantic Scholar with custom queries and filters.
2.  **Filter Papers with AI (Llama)**: Use a local AI model to perform contextual filtering on your search results.
3.  **Analyze Results**: Generate statistics on the papers you've collected.
4.  **Help / Information**: View the detailed help menu.
5.  **Exit**: Close the application.

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
