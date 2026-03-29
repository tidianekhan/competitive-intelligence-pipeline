# AI Competitor Social Media Monitoring

**Status:** v3 Complete (Google Sheets Migration)  
**Alert Layer:** Implemented

An AI-powered competitive intelligence pipeline that monitors competitor Instagram activity, stores structured post data in Google Sheets, and enriches posts with LLM-generated topic summaries using a modular Python workflow.

---

## Overview

This system automates the collection, enrichment, and distribution of competitor social media intelligence.

The pipeline:

1. Scrapes competitor Instagram posts daily via Apify
2. Writes structured post data directly to Google Sheets via native Apify integration
3. Reads unprocessed posts from Google Sheets using a local URL ledger
4. Generates concise AI-powered topic summaries
5. Writes summaries back to Google Sheets and updates the local ledger
6. Sends a daily automated HTML email digest of newly processed posts

The result is a fully automated, scalable competitive intelligence system requiring zero manual intervention.

---

## Architecture
```
Apify (Scheduled Scraper)
        │
        ▼
Google Sheets (Central Intelligence Database)
        │
        ▼
Python Intelligence Layer
   ├─ Ledger (processed_urls.json)
   ├─ Google Sheets Client
   ├─ OpenAI LLM Client
   └─ Email Digest Builder
        │
        ▼
SendGrid (Daily HTML Digest)
        │
        ▼
Stakeholders
```

The Python layer runs daily via GitHub Actions using secure environment secrets.

---

## Core Workflow

### 1. Data Collection

- Apify runs daily on a schedule
- Scrapes latest Instagram posts for defined competitors
- Extracted fields:
  - Post URL
  - Caption
  - Owner Name
  - Timestamp

Apify uses the `lukaskrivka/google-sheets` integration to append records to Google Sheets, deduplicating by URL as the primary key to prevent duplicates automatically.

---

### 2. Central Data Storage

Google Sheets acts as the structured intelligence database:

- Stores all raw post data
- Holds AI-generated topic summaries once enriched
- Accessible and editable without any API limits or account restrictions

---

### 3. Ledger-Based Processing State

Processing state is tracked via a local `processed_urls.json` ledger committed to the repository. This is the single source of truth — the ledger only ever grows, never shrinks.

At the start of every run the pipeline:

- Loads the ledger as-is
- Fetches all rows from Google Sheets
- Skips any URL already present in the ledger
- Processes only new, unprocessed posts

This simple approach is resilient and predictable — no reconciliation logic, no regressions.

---

### 4. Python Intelligence Layer

The Python pipeline:

- Loads the ledger from `processed_urls.json`
- Queries Google Sheets for unprocessed posts (URLs not in ledger)
- Skips posts with captions too short or emoji-only
- Sends captions to an LLM client
- Generates a neutral 15–25 word topic summary
- Writes the summary back to the `Topic Summary` column in Google Sheets
- Adds the URL to the ledger only on confirmed successful write
- Ensures each post is processed exactly once

---

### 5. Automated Digest Layer

After processing posts, the system:

- Builds a structured HTML table digest
- Includes:
  - Competitor name
  - Timestamp
  - AI-generated topic summary
  - Direct post link
- Sends the digest via SendGrid
- Only sends email if new summaries were generated

This ensures stakeholders receive concise daily competitive intelligence updates without noise.

---

## Scheduling & Automation

The system runs fully automatically via:

- **Apify Scheduler** → Scraping and Google Sheets population
- **GitHub Actions (cron: 07:30 UTC daily)** → Ledger load, Python enrichment, digest
- **SendGrid** → Email delivery

The GitHub Actions workflow commits the updated ledger back to the repository after each run.

All secrets are managed securely via:

- `.env` (local development)
- GitHub Actions Secrets (production)

No manual execution is required.

---

## What Changed vs v2

Version 3 introduced a full data storage migration and pipeline simplification:

- **Replaced Airtable with Google Sheets** — more reliable, no record limits, native Apify integration
- **Removed ledger sync logic entirely** — the ledger is now the single source of truth and only grows
- **Simplified `sheets_client.py`** — clean read/write against Google Sheets with no reconciliation logic
- **Removed self-healing sync** — eliminated the source of recurring ledger regressions
- **Apify now writes directly to Google Sheets** via `lukaskrivka/google-sheets` with URL-based deduplication

---

## Tech Stack

- Python
- OpenAI API (LLM abstraction layer)
- Apify
- Google Sheets (via `gspread` and Google Service Account)
- SendGrid
- GitHub Actions (scheduler)
- dotenv

---

## Project Structure
```
src/
├── main.py              # Pipeline entry point
├── sheets_client.py     # Google Sheets integration and ledger management
├── llm_client.py        # LLM abstraction layer
├── email_client.py      # SendGrid HTML digest layer
└── config.py            # Environment configuration

processed_urls.json      # Processed URL ledger (committed to repo)
```

---

## Setup

1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` file using `.env.example`
5. Configure required environment variables:
```
GOOGLE_SHEETS_CREDENTIALS=<service account JSON as single line>
GOOGLE_SHEET_ID=<your Google Sheet ID>
OPENAI_API_KEY=<your OpenAI key>
SENDGRID_API_KEY=<your SendGrid key>
SENDGRID_FROM_EMAIL=<verified sender email>
DIGEST_RECIPIENTS=<comma separated recipient emails>
MAX_POSTS_PER_RUN=<number of posts to process per run>
```
6. Share your Google Sheet with the service account email (Editor access)
7. Initialise the ledger: `echo "[]" > processed_urls.json`
8. Run the pipeline: `python3 src/main.py`

---

## Design Principles

- Modular integrations
- Clear separation of orchestration and API clients
- Idempotent processing (no duplicate summaries)
- Resilient state management via local ledger
- Single source of truth — ledger only grows
- Deterministic daily digest logic
- Secure secret management
- Minimal infrastructure overhead
- Scalable architecture ready for advanced reporting

---

## Purpose

This project demonstrates:

- Automation architecture design
- API integration workflows
- LLM-powered enrichment pipelines
- Resilient state management patterns
- Automated executive reporting systems
- Structured intelligence system design
- Clean modular Python implementation
