"""
Run this to process one file at a time.

For a demo call:
  python scripts/ingest.py --file data/demo/company1.txt --type demo

For an onboarding call:
  python scripts/ingest.py --file data/onboarding/company1.txt --type onboarding --account_id company1_fire_20250601
"""
import argparse
import os
import sys

# Add scripts folder to path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from transcribe import load_transcript
from extract_memo import extract_memo, save_memo
from generate_agent_spec import generate_agent_spec, save_agent_spec
from apply_onboarding import load_v1_memo, get_patch_from_onboarding, apply_patch
from generate_changelog import generate_changelog


def run_demo(file_path):
    print(f"\n{'='*50}")
    print(f"[PIPELINE A] Demo call: {file_path}")
    
    # Step 1: Read/transcribe the file
    transcript = load_transcript(file_path)
    
    # Step 2: Extract structured data from transcript
    memo = extract_memo(transcript, call_type="demo")
    
    # Step 3: Save memo JSON
    save_memo(memo, version="v1")
    
    # Step 4: Generate agent spec
    spec = generate_agent_spec(memo, version="v1")
    save_agent_spec(spec, memo["account_id"], version="v1")
    
    print(f"\n[DONE] v1 created for: {memo['account_id']}")
    print(f"       Saved to: outputs/accounts/{memo['account_id']}/v1/")
    return memo["account_id"]


def run_onboarding(file_path, account_id):
    print(f"\n{'='*50}")
    print(f"[PIPELINE B] Onboarding call: {file_path}")
    
    # Step 1: Read/transcribe the file
    transcript = load_transcript(file_path)
    
    # Step 2: Load existing v1 memo
    v1_memo = load_v1_memo(account_id)
    
    # Step 3: Extract what changed from onboarding
    patch_data = get_patch_from_onboarding(v1_memo, transcript)
    
    # Step 4: Apply patch to create v2 memo
    v2_memo = apply_patch(v1_memo, patch_data)
    save_memo(v2_memo, version="v2")
    
    # Step 5: Regenerate agent spec with v2 data
    spec_v2 = generate_agent_spec(v2_memo, version="v2")
    save_agent_spec(spec_v2, account_id, version="v2")
    
    # Step 6: Generate changelog
    generate_changelog(v1_memo, v2_memo, account_id)
    
    print(f"\n[DONE] v2 created for: {account_id}")
    print(f"       Saved to: outputs/accounts/{account_id}/v2/")


# Entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to transcript file")
    parser.add_argument("--type", required=True, choices=["demo", "onboarding"])
    parser.add_argument("--account_id", help="Required for onboarding type")
    args = parser.parse_args()
    
    if args.type == "demo":
        run_demo(args.file)
    else:
        if not args.account_id:
            print("[ERROR] You must provide --account_id for onboarding runs")
            sys.exit(1)
        run_onboarding(args.file, args.account_id)