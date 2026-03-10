import json
import os

# Paths
JSONL_FILE = r"c:\Users\Tariq\OneDrive\Desktop\Nehar\Korea\New version\travnook-bot\unified bot\UnifiedTrainingData.jsonl"
HTML_OUTPUT = r"c:\Users\Tariq\OneDrive\Desktop\Nehar\Korea\New version\travnook-bot\unified bot\visualized_conversations.html"

def generate_html():
    if not os.path.exists(JSONL_FILE):
        print(f"Error: {JSONL_FILE} not found.")
        return

    conversations = []
    with open(JSONL_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                conversations.append(json.loads(line))

    if not conversations:
        print("Error: No conversations found in JSONL.")
        return

    # Extract system prompt from the first conversation
    system_prompt = ""
    for msg in conversations[0]['messages']:
        if msg['role'] == 'system':
            system_prompt = msg['content']
            break

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travnook Bot - Conversation Visualizer</title>
    <style>
        :root {{
            --wa-bg: #e5ddd5;
            --wa-bubble-user: #ffffff;
            --wa-bubble-bot: #dcf8c6;
            --wa-bubble-cmd: #e1f5fe;
            --wa-text: #000000;
            --wa-time: #999999;
            --wa-header: #075e54;
            --wa-rule-bg: #f0f4f8;
            --wa-rule-border: #bcccdc;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .container {{
            max-width: 800px;
            width: 100%;
        }}
        .header {{
            background: var(--wa-header);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .rules-section {{
            background: var(--wa-rule-bg);
            border: 1px solid var(--wa-rule-border);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            white-space: pre-wrap;
            font-size: 14px;
            color: #334e68;
            line-height: 1.5;
        }}
        .scenario-card {{
            background-color: var(--wa-bg);
            border-radius: 15px;
            margin-bottom: 40px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png');
            background-repeat: repeat;
        }}
        .scenario-header {{
            background: rgba(255,255,255,0.9);
            padding: 10px 20px;
            border-bottom: 1px solid #ddd;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .chat-window {{
            padding: 20px;
            display: flex;
            flex-direction: column;
        }}
        .bubble {{
            max-width: 70%;
            padding: 8px 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            position: relative;
            font-size: 15px;
            line-height: 1.4;
            box-shadow: 0 1px 1px rgba(0,0,0,0.1);
        }}
        .bubble.user {{
            align-self: flex-start;
            background-color: var(--wa-bubble-user);
            border-top-left-radius: 0;
        }}
        .bubble.assistant {{
            align-self: flex-end;
            background-color: var(--wa-bubble-bot);
            border-top-right-radius: 0;
        }}
        .bubble.command {{
            align-self: center;
            background-color: var(--wa-bubble-cmd);
            border-radius: 10px;
            font-family: monospace;
            font-weight: bold;
            color: #0277bd;
            text-align: center;
            border: 1px dashed #0277bd;
        }}
        .role-label {{
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 4px;
            display: block;
        }}
        .user .role-label {{ color: #075e54; }}
        .assistant .role-label {{ color: #25d366; text-align: right; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Travnook Unified Bot Visualizer</h1>
            <p>Training Data Preview (WhatsApp Style)</p>
        </div>

        <h3>Unified System Prompt (The Rules)</h3>
        <div class="rules-section">{system_prompt}</div>

        <div id="conversations">
    """

    for i, conv in enumerate(conversations):
        html_content += f"""
        <div class="scenario-card">
            <div class="scenario-header">
                <span>Conversation #{i+1}</span>
            </div>
            <div class="chat-window">
        """
        
        for msg in conv['messages']:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                continue
            
            # Identify commands
            is_command = content.startswith('/')
            
            bubble_class = "bubble " + ("command" if is_command else role)
            label = "Client" if role == "user" else "Travnook Bot"
            if is_command: label = "System Action"

            html_content += f"""
                <div class="{bubble_class}">
                    <span class="role-label">{label}</span>
                    {content}
                </div>
            """
            
        html_content += """
            </div>
        </div>
        """

    html_content += """
        </div>
    </div>
</body>
</html>
    """

    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Visualization created at: {HTML_OUTPUT}")

if __name__ == "__main__":
    generate_html()
