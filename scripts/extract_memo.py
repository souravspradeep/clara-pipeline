import os
import json
import re
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # reads your .env file

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def extract_memo(transcript, call_type="demo"):
    """
    Sends transcript to Groq AI → gets back Account Memo JSON
    call_type is either "demo" or "onboarding"
    """
    
    # Load the right prompt template
    prompt_file = f"scripts/prompts/{call_type}_extraction.txt"
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # Insert the transcript into the prompt
    prompt = prompt.replace("{transcript}", transcript)
    
    print(f"[EXTRACT] Sending {call_type} transcript to AI...")
    
    # Call Groq AI
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,   # Low = more consistent, less creative
        max_tokens=2000,
    )
    
    # Get the text response
    raw = response.choices[0].message.content.strip()
    
    # Sometimes AI wraps JSON in ```json ... ``` — remove that
    raw = re.sub(r"```json|```", "", raw).strip()
    
    # Parse JSON
    try:
        memo = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[ERROR] AI returned invalid JSON: {e}")
        print(f"[RAW]: {raw}")
        raise
    
    # Auto-create account_id from company name + today's date
    if not memo.get("account_id") and memo.get("company_name"):
        slug = memo["company_name"].lower().replace(" ", "_")
        date = datetime.now().strftime("%Y%m%d")
        memo["account_id"] = f"{slug}_{date}"
    
    print(f"[EXTRACT] Done. Account: {memo.get('account_id')}")
    return memo


def save_memo(memo, version="v1"):
    """Saves the memo JSON to the outputs folder"""
    account_id = memo["account_id"]
    out_dir = os.path.join(
        os.environ.get("OUTPUT_DIR", "./outputs/accounts"),
        account_id, version
    )
    os.makedirs(out_dir, exist_ok=True)  # creates folder if it doesn't exist
    
    path = os.path.join(out_dir, "account_memo.json")
    with open(path, "w") as f:
        json.dump(memo, f, indent=2)
    
    print(f"[SAVE] Memo saved to: {path}")
    return path