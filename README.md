\# Clara Answers — Automation Pipeline



\## What This Does

Converts call recordings into configured AI voice agent specs for Clara Answers.



\## Architecture

```

Demo Call → Whisper Transcription → Groq LLM Extraction → Account Memo (v1) → Agent Spec (v1)

&nbsp;                                                                 ↓

Onboarding Call → Extract Changes → Patch v1 → Account Memo (v2) → Agent Spec (v2) + Changelog

```



\## Quick Start



\### 1. Install dependencies

```bash

pip install groq faster-whisper python-dotenv deepdiff

```



\### 2. Set up environment

```bash

cp .env.example .env

\# Add your Groq API key to .env

```



\### 3. Add transcripts to data/ folder

```

data/demo/001\_bens\_electric\_demo.txt

data/onboarding/001\_bens\_electric\_onboard.txt

```



\### 4. Update manifest

Edit `data/manifest.json` with your account names and file paths.



\### 5. Run single account

```bash

\# Demo call (creates v1)

python scripts/ingest.py --file data/demo/001\_bens\_electric\_demo.txt --type demo



\# Onboarding call (creates v2)

python scripts/ingest.py --file data/onboarding/001\_bens\_electric\_onboard.txt --type onboarding --account\_id ben's\_electric\_solutions\_team\_20260304

```



\### 6. Run all accounts at once

```bash

python scripts/batch\_run.py

```



\## Output Structure

```

outputs/accounts/{account\_id}/

&nbsp;   v1/

&nbsp;       account\_memo.json        ← extracted from demo call

&nbsp;       retell\_agent\_spec.json   ← Clara's conversation script

&nbsp;   v2/

&nbsp;       account\_memo.json        ← updated from onboarding call

&nbsp;       retell\_agent\_spec.json   ← updated Clara script

&nbsp;       changes.json             ← what changed and why

```



\## Tech Stack

| Tool | Purpose | Cost |

|------|---------|------|

| Groq (Llama 3.3 70B) | LLM extraction | Free |

| faster-whisper | Audio transcription | Free |

| Python | Scripts | Free |

| GitHub | Storage | Free |



\## Known Limitations

\- Retell agent spec is mock JSON (manual import step required)

\- Whisper transcription requires local CPU (~5 mins per file)

\- Groq free tier: 14,400 requests/day (more than enough)



\## What I Would Improve with Production Access

\- Direct Retell API integration for automated agent creation

\- Webhook trigger from call platforms

\- Supabase for persistent queryable storage

\- Confidence scoring on extracted fields

```



---



\### Step 6.3 — Create `.env.example`



Create `.env.example` (this is safe to upload — no real keys):

```

GROQ\_API\_KEY=your\_groq\_key\_here

OUTPUT\_DIR=./outputs/accounts

DATA\_DIR=./data

