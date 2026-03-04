import os
import json
import re
from copy import deepcopy
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])


def load_v1_memo(account_id):
    """Loads the existing v1 memo from disk"""
    path = os.path.join(
        os.environ.get("OUTPUT_DIR", "./outputs/accounts"),
        account_id, "v1", "account_memo.json"
    )
    with open(path, "r") as f:
        return json.load(f)


def get_patch_from_onboarding(v1_memo, transcript):
    """
    Sends v1 memo + onboarding transcript to AI.
    AI returns ONLY what changed.
    """
    with open("scripts/prompts/onboarding_extraction.txt", "r") as f:
        template = f.read()
    
    prompt = template.replace("{v1_memo}", json.dumps(v1_memo, indent=2))
    prompt = prompt.replace("{transcript}", transcript)
    
    print("[PATCH] Extracting onboarding changes from AI...")
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2000,
    )
    
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


def apply_patch(v1_memo, patch_data):
    """
    Takes v1 memo and applies only the changed fields.
    Does NOT touch unchanged fields.
    """
    v2 = deepcopy(v1_memo)   # start with a full copy of v1
    v2["version"] = "v2"
    v2["source"] = "onboarding_call"
    
    # Apply changed fields
    for field, change in patch_data.get("patch", {}).items():
        new_value = change.get("new")
        if new_value is not None:
            v2[field] = new_value
            print(f"[PATCH] Updated: {field}")
    
    # Add brand new fields
    for field, value in patch_data.get("new_fields", {}).items():
        v2[field] = value
        print(f"[PATCH] Added: {field}")
    
    # Merge unresolved questions
    old_q = v2.get("questions_or_unknowns", [])
    new_q = patch_data.get("questions_or_unknowns", [])
    v2["questions_or_unknowns"] = list(set(old_q + new_q))
    
    # Log conflicts in notes
    conflicts = patch_data.get("conflicts", [])
    if conflicts:
        v2["notes"] = (v2.get("notes") or "") + " | CONFLICTS: " + "; ".join(conflicts)
        print(f"[WARNING] Conflicts found: {conflicts}")
    
    return v2