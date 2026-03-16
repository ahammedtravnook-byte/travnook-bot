import json

input_file = r"c:\Users\Tariq\OneDrive\Desktop\Nehar\Korea\New version\travnook-bot\final\TrainingData_Phases1to4_V2.jsonl"
output_file = r"c:\Users\Tariq\OneDrive\Desktop\Nehar\Korea\New version\travnook-bot\final\TrainingData_Final.jsonl"

arabic_triggers = ["أوقات العمل", "راح يتواصل", "سيتواصل معك", "راح يتواصلوا"]

def is_transition_message(text):
    text_lower = text.lower()
    if "working hours" in text_lower:
        return True
    for phrase in arabic_triggers:
        if phrase in text:
            return True
    return False

def is_routing_command(text):
    return text.strip().startswith("/")

valid_count = 0

with open(input_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8") as f_out:
    for line in f_in:
        line = line.strip()
        if not line:
            continue
            
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
            
        messages = data.get("messages", [])
        if not messages:
            continue
            
        cleaned_messages = []
        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            
            if msg.get("role") == "assistant" and is_transition_message(content):
                continue
                
            if msg.get("role") == "assistant" and is_routing_command(content):
                if i != len(messages) - 1:
                    continue
            
            cleaned_messages.append(msg)
            
        clean_item = {"messages": cleaned_messages}
        out_str = json.dumps(clean_item, ensure_ascii=False)
        f_out.write(out_str + "\n")
        valid_count += 1

print(f"Cleaned and saved {valid_count} conversations successfully to TrainingData_Final.jsonl")
