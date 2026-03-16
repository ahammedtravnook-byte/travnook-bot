import os
import json
import logging
from typing import List, Dict, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from openai import OpenAI
from dotenv import load_dotenv

# Setup Logging
logging.basicConfig(
    filename='bot_diagnostic.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Rich Console
console = Console()

# File Paths
BASE_DIR = r"c:\Users\Tariq\OneDrive\Desktop\Nehar\Korea\New version\travnook-bot\final"
PROMPT_FILES = {
    "System Prompt": os.path.join(BASE_DIR, "All_Phases_System_Prompt.txt"),
    "Behavior Rules": os.path.join(BASE_DIR, "All_Phases_Behavior.txt"),
    "Generation Goals": os.path.join(BASE_DIR, "All_Phases_Generation_Goal.txt")
}
TRAINING_DATA_FILE = os.path.join(BASE_DIR, "TrainingData_Final.jsonl")

# Load OpenAI Key
load_dotenv()
# Fallback to the known key if not in env
api_key = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=api_key)

def show_header():
    console.clear()
    title = Text("Travnook Bot Performance Analyzer", style="bold cyan")
    subtitle = Text("AI Diagnostic & Precision Tuning Tool", style="dim italic")
    console.print(Panel.fit(
        f"{title}\n{subtitle}",
        border_style="cyan",
        title="[bold yellow]v1.0[/bold yellow]"
    ))

def read_file_with_lines(filepath: str) -> str:
    """Read a file and return its content with line numbers for exact referencing."""
    if not os.path.exists(filepath):
        logging.error(f"File not found: {filepath}")
        return f"[Error: File {os.path.basename(filepath)} not found]"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    numbered_content = ""
    for i, line in enumerate(lines, 1):
        numbered_content += f"L{i}: {line}"
    return numbered_content

def search_training_data_local(keywords: List[str], max_results: int = 3) -> str:
    """
    RAG approach: Search the JSONL locally for lines containing any of the keywords.
    Returns a condensed string of matching JSON objects with their source line numbers,
    saving massive amounts of API tokens.
    """
    if not os.path.exists(TRAINING_DATA_FILE):
        return "No training data found."

    results = []
    with open(TRAINING_DATA_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line_lower = line.lower()
            if any(kw.lower() in line_lower for kw in keywords):
                # Try to format it slightly nicer, or just return the raw line with L#
                results.append(f"TrainingData_Final.jsonl - Line {i}:\n{line.strip()}")
                if len(results) >= max_results:
                    break
    
    if not results:
        return "No strictly matching training data lines found for keywords."
    
    return "\n\n".join(results)

def get_keywords_from_input(feedback: str, transcript: str) -> List[str]:
    """Extract simple search keywords using OpenAI to guide the local RAG."""
    prompt = f"""
    Extract 2-3 key unique, specific travel or issue-related terms from this feedback and transcript.
    Return ONLY a comma-separated list of words (e.g., "UK visa, price, blurry").
    
    Feedback: {feedback}
    Transcript summary: {transcript[:200]}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        words = response.choices[0].message.content.split(',')
        return [w.strip() for w in words if w.strip()]
    except Exception as e:
        logging.error(f"Failed keyword extraction: {e}")
        return ["visa", "price"] # safe fallback

def analyze_performance(transcript: str, feedback: str):
    logging.info("Starting performance analysis...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        
        # 1. Gather Context
        task_gather = progress.add_task("[cyan]Gathering Context & Identifying RAG Keywords...", total=None)
        
        prompts_context = ""
        for name, path in PROMPT_FILES.items():
            content = read_file_with_lines(path)
            prompts_context += f"\n--- {name} ({os.path.basename(path)}) ---\n{content}\n"
        
        keywords = get_keywords_from_input(feedback, transcript)
        logging.info(f"Local RAG Keywords determined: {keywords}")
        
        training_context = search_training_data_local(keywords)
        progress.update(task_gather, completed=True)
        
        # 2. Querying OpenAI
        task_analyze = progress.add_task("[yellow]Sending targeted context to AI for deep analysis...", total=None)
        
        system_instructions = """
        You are an expert Dialogflow Bot Debugger. Your job is to analyze a failed bot conversation.
        You have been provided with:
        1. The Master System Prompts (with Line Numbers).
        2. Relevant snippets of the existing bot Training Data (with Line Numbers).
        3. The user's flawed transcript.
        4. The user's feedback on what the bot did wrong.
        
        Your ONLY job is to tell the user EXACTLY how to fix the files.
        Output your response using the following markdown structure:
        
        ### 🔍 Root Cause Analysis
        (Explain briefly why the bot messed up based on the provided Master rules or missing training data)
        
        ### 🛠️ Required Prompt Fixes
        (Tell the user EXACTLY which file and which Line Number needs to be added/modified to fix this)
        Example: `In All_Phases_System_Prompt.txt, insert at Line 45:`
        
        ### 📝 Required Training Data Fixes (Optional)
        (If the training data caused the hallucination, mention the exact Line Numbers in TrainingData_Final.jsonl that need review).
        
        ### 🧠 Data Augmentation
        (Generate 2 new high-quality JSONL examples specifically handling this edge case correctly, so the user can paste them into their training file).
        """
        
        user_prompt = f"""
        MASTER RULES CONTEXT:
        {prompts_context}
        
        RELEVANT TRAINING DATA (Snippets):
        {training_context}
        
        ====== FAILED BOT DATA ======
        USER FEEDBACK ON FAILURE: {feedback}
        
        FLAWED TRANSCRIPT:
        {transcript}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o", # Using full 4o for maximum reasoning precision on line numbers
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            analysis_result = response.choices[0].message.content
            logging.info("Analysis completed successfully.")
            progress.update(task_analyze, completed=True)
            return analysis_result
            
        except Exception as e:
            logging.error(f"OpenAI API Error: {e}")
            progress.update(task_analyze, completed=True)
            return f"[red]Error contacting AI Analyzer: {e}[/red]"

def main():
    show_header()
    console.print("\n[bold green]Welcome![/bold green] Paste the failed transcript from your live bot below.")
    console.print("[dim]When you are done pasting the transcript, type 'DONE' on a new line.[/dim]\n")
    
    transcript_lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'DONE':
                break
            transcript_lines.append(line)
        except EOFError:
            break
            
    transcript = "\n".join(transcript_lines)
    
    if not transcript.strip():
        console.print("[red]Transcript cannot be empty.[/red]")
        return
        
    console.print("\n[bold green]Feedback[/bold green]")
    feedback = Prompt.ask("What exactly did the bot do wrong here? (e.g., 'Offered discount on UK visa')")
    
    console.print("\n[bold cyan]Initiating Diagnostics...[/bold cyan]")
    
    result_markdown = analyze_performance(transcript, feedback)
    
    console.print(Panel(Markdown(result_markdown), title="[bold green]Diagnostic Report[/bold green]", border_style="green"))
    console.print("\n[dim]Analysis saved to bot_diagnostic.log[/dim]")

if __name__ == "__main__":
    main()
