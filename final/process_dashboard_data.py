import json
import os

def process_data():
    base_dir = r"c:\Users\Tariq\OneDrive\Desktop\Nehar\Korea\New version\travnook-bot\final"
    
    # 1. Process the 606 conversations
    jsonl_path = os.path.join(base_dir, "TrainingData_Final.jsonl")
    conversations = []
    
    if os.path.exists(jsonl_path):
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f):
                if line.strip():
                    try:
                        data = json.loads(line)
                        messages = data.get("messages", [])
                        
                        # Filter: Remove only the specific scenarios user requested
                        # We look for the assistant commands /payment and /payment-doc-correction
                        has_blacklisted_cmd = any(
                            m.get("role") == "assistant" and 
                            (m.get("content", "").strip() == "/payment" or m.get("content", "").strip() == "/payment-doc-correction")
                            for m in messages
                        )
                        if has_blacklisted_cmd:
                            continue

                        # Add an ID and Name for the sidebar
                        convo = {
                            "id": len(conversations) + 1,
                            "title": f"Conversation {len(conversations) + 1}",
                            "messages": messages
                        }
                        conversations.append(convo)
                    except Exception as e:
                        print(f"Error parsing line {idx}: {e}")
    else:
        print("TrainingData_Final.jsonl not found.")

    # 2. Process text files
    files_to_read = {
        "behavior": "All_Phases_Behavior.txt",
        "goals": "All_Phases_Generation_Goal.txt",
        "prompts": "All_Phases_System_Prompt.txt"
    }
    
    docs = {}
    for key, filename in files_to_read.items():
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                docs[key] = f.read()
        else:
            docs[key] = f"File {filename} not found."
            print(f"{filename} not found.")

    # Combine all into one JSON
    output_data = {
        "conversations": conversations,
        "docs": docs
    }
    
    output_path = os.path.join(base_dir, "dashboard_data.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    js_output_path = os.path.join(base_dir, "dashboard_data.js")
    with open(js_output_path, 'w', encoding='utf-8') as f:
        f.write("const dashboardData = ")
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        f.write(";")
        
    print(f"Successfully processed {len(conversations)} conversations and saved to data files.")

if __name__ == "__main__":
    process_data()
