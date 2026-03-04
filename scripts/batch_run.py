"""
Runs all 5 demo calls then all 5 onboarding calls.
Reads the list from data/manifest.json
"""
import json
import subprocess
import sys

def run_batch():
    # Load the manifest
    with open("data/manifest.json") as f:
        manifest = json.load(f)
    
    print("\n" + "="*60)
    print("PHASE 1: Processing all 5 demo calls...")
    print("="*60)
    
    for entry in manifest:
        demo_file = entry["demo_file"]
        print(f"\n→ {demo_file}")
        
        result = subprocess.run(
            [sys.executable, "scripts/ingest.py",
             "--file", demo_file,
             "--type", "demo"],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"[ERROR]: {result.stderr}")
    
    print("\n" + "="*60)
    print("PHASE 2: Processing all 5 onboarding calls...")
    print("="*60)
    
    for entry in manifest:
        onboard_file = entry["onboarding_file"]
        account_id = entry["account_id"]
        print(f"\n→ {onboard_file} (account: {account_id})")
        
        result = subprocess.run(
            [sys.executable, "scripts/ingest.py",
             "--file", onboard_file,
             "--type", "onboarding",
             "--account_id", account_id],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"[ERROR]: {result.stderr}")
    
    print("\n✅ BATCH COMPLETE")

if __name__ == "__main__":
    run_batch()