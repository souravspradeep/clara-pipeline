from flask import Flask, request, jsonify
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Paste your generated system_prompt from retell_agent_spec.json here
SYSTEM_PROMPT = """
YOUR SYSTEM PROMPT FROM retell_agent_spec.json GOES HERE
"""

@app.route("/llm", methods=["POST"])
def llm():
    data = request.json
    messages = data.get("transcript", [])
    
    # Convert Retell transcript format to Groq format
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        role = "user" if msg["role"] == "user" else "assistant"
        groq_messages.append({"role": role, "content": msg["content"]})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        max_tokens=200
    )
    
    return jsonify({
        "content": response.choices[0].message.content
    })

if __name__ == "__main__":
    app.run(port=5000)