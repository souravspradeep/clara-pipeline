import os
import json
from datetime import datetime

def build_agent_prompt(memo):
    """Fill the prompt template with real values from the memo"""
    
    with open("scripts/prompts/agent_prompt_template.txt", "r", encoding="utf-8") as f:
        template = f.read()
    
    bh = memo.get("business_hours", {})
    er = memo.get("emergency_routing_rules", {})
    ner = memo.get("non_emergency_routing_rules", {})
    tr = memo.get("call_transfer_rules", {})
    
    # Build readable lists
    em_list = "\n".join(
        f"- {e}" for e in memo.get("emergency_definition", ["Not yet defined"])
    )
    constraints = "\n".join(
        f"- {c}" for c in memo.get("integration_constraints", ["None specified"])
    )
    
    # Replace all placeholders
    replacements = {
    "{company_name}":            memo.get("company_name") or "the company",
    "{business_hours_days}":     bh.get("days") or "Monday-Friday",
    "{business_hours_start}":    bh.get("start") or "8:00 AM",
    "{business_hours_end}":      bh.get("end") or "5:00 PM",
    "{timezone}":                bh.get("timezone") or "local time",
    "{emergency_triggers}":      ", ".join(memo.get("emergency_definition") or ["emergency"]),
    "{emergency_contact}":       er.get("primary_contact") or "on-call technician",
    "{transfer_timeout}":        str(tr.get("timeout_seconds") or 30),
    "{emergency_definitions}":   em_list or "Not yet defined",
    "{integration_constraints}": constraints or "None specified",
}

    
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    
    return template


def generate_agent_spec(memo, version="v1"):
    """Creates the full Retell Agent Spec JSON"""
    
    prompt = build_agent_prompt(memo)
    bh = memo.get("business_hours", {})
    er = memo.get("emergency_routing_rules", {})
    tr = memo.get("call_transfer_rules", {})
    
    spec = {
        "agent_name": f"Clara - {memo.get('company_name', 'Client')}",
        "version": version,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "voice_style": {
            "tone": "professional, warm, concise",
            "language": "en-US"
        },
        "system_prompt": prompt,
        "key_variables": {
            "timezone":          bh.get("timezone"),
            "business_hours":    bh,
            "office_address":    memo.get("office_address"),
            "emergency_contact": er.get("primary_contact"),
            "fallback":          er.get("fallback")
        },
        "call_transfer_protocol": {
            "timeout_seconds": tr.get("timeout_seconds", 30),
            "retries":         tr.get("retries", 1),
            "fail_message":    tr.get("fail_action",
                "I wasn't able to connect you right now. Your details have been noted.")
        },
        "fallback_protocol": {
            "transfer_fails": "Collect name, number, issue. Assure callback.",
            "unknown_request": "Take name and number. Route to office."
        }
    }
    
    return spec


def save_agent_spec(spec, account_id, version="v1"):
    """Saves agent spec to outputs folder"""
    out_dir = os.path.join(
        os.environ.get("OUTPUT_DIR", "./outputs/accounts"),
        account_id, version
    )
    os.makedirs(out_dir, exist_ok=True)
    
    path = os.path.join(out_dir, "retell_agent_spec.json")
    with open(path, "w") as f:
        json.dump(spec, f, indent=2)
    
    print(f"[SAVE] Agent spec saved to: {path}")
    return path