# Clara Answers - Automation Pipeline

## What This Does
Converts call recordings into configured AI voice agent specs for Clara Answers.

## Architecture

Demo Call -> Whisper Transcription -> Groq LLM Extraction -> Account Memo (v1) -> Agent Spec (v1)
                                                                    |
Onboarding Call -> Extract Changes -> Patch v1 -> Account Memo (v2) -> Agent Spec (v2) + Changelog

## Quick Start

### 1. Install dependencies
pip install groq faster-whisper python-dotenv deepdiff

### 2. Set up environment
Copy .env.example to .env and add your Groq API key
Get free key at: https://console.groq.com

### 3. Add transcripts to data folder
data/demo/001_bens_electric_demo.txt
data/onboarding/001_bens_electric_onboard.txt

### 4. Update manifest
Edit data/manifest.json with your account names and file paths

### 5. Run single account

Demo call - creates v1:
python scripts/ingest.py --file data/demo/001_bens_electric_demo.txt --type demo

Onboarding call - creates v2:
python scripts/ingest.py --file data/onboarding/001_bens_electric_onboard.txt --type onboarding --account_id ben's_electric_solutions_team_20260304

### 6. Run all accounts at once
python scripts/batch_run.py

## Output Structure

outputs/accounts/{account_id}/
    v1/
        account_memo.json        <- extracted from demo call
        retell_agent_spec.json   <- Clara conversation script (v1)
    v2/
        account_memo.json        <- updated from onboarding call
        retell_agent_spec.json   <- Clara conversation script (v2)
        changes.json             <- what changed and why

## n8n Setup

### Run n8n locally with Docker
docker run -it --rm --name n8n -p 5678:5678 -e N8N_ALLOW_EXEC=true docker.n8n.io/n8nio/n8n

Then open http://localhost:5678

### Import workflow
1. Open n8n at http://localhost:5678
2. Click New Workflow
3. Click 3 dots menu top right
4. Click Import from File
5. Select workflows/clara_n8n_workflow.json
6. Click Save

### Run batch via n8n
Trigger the Run Batch All Accounts node manually inside n8n

### Environment Variables
GROQ_API_KEY=your_groq_key_here
OUTPUT_DIR=./outputs/accounts
DATA_DIR=./data

## Retell Setup

### Create Account
Sign up free at https://retell.ai

### Why No Direct API Integration
Retell programmatic agent creation requires a paid plan.
This pipeline outputs a complete Agent Spec JSON for manual import.

### Manual Import Steps (per account)
1. Open outputs/accounts/{account_id}/v2/retell_agent_spec.json
2. Log into Retell dashboard
3. Click Create Agent -> Custom LLM
4. Copy the system_prompt field -> paste into System Prompt box
5. Set voice: female, neutral American accent
6. Set language: en-US
7. Set transfer number from key_variables.emergency_contact
8. Click Save

## Task Tracker
Trello board used to track per-account processing status.
Screenshot: workflows/trello_screenshot.png

## Tech Stack

| Tool              | Purpose              | Cost |
|-------------------|----------------------|------|
| Groq Llama 3.3 70B| LLM extraction       | Free |
| faster-whisper    | Audio transcription  | Free |
| n8n Docker        | Orchestration        | Free |
| Python            | Scripts              | Free |
| GitHub            | Storage              | Free |
| Trello            | Task tracking        | Free |
| Total             |                      | $0   |

## Dataset Status
Currently tested on 1 account: Ben's Electric Solutions.
Remaining 4 accounts will be added upon receiving recordings.
Pipeline is fully batch-capable.
Run python scripts/batch_run.py once all recordings are received.

## Known Limitations
- Retell agent spec is mock JSON - manual import required
- Whisper transcription runs on local CPU (~5 mins per file)
- Groq free tier: 14,400 requests per day
- n8n Execute Command needs N8N_ALLOW_EXEC=true Docker flag

## What I Would Improve with Production Access
- Direct Retell API integration for automated agent creation
- Webhook trigger from call platforms
- Supabase for persistent queryable storage
- Confidence scoring on extracted fields
- Automated Trello card creation via API