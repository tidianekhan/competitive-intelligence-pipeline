# AI Competitor Social Media Monitoring

**Status:** v2 Complete (Core Pipeline)  
**Alert Layer:** Pending Implementation  

An AI-powered competitive intelligence pipeline that monitors competitor Instagram activity, structures raw data in Airtable, and enriches posts with LLM-generated topic summaries using a modular Python workflow.

---

## Overview

This system automates the collection, enrichment, and distribution of competitor social media intelligence.

The pipeline:

1. Scrapes competitor Instagram posts daily via Apify  
2. Stores structured post data in Airtable  
3. Syncs a local URL ledger with Airtable state to identify unprocessed posts  
4. Generates concise AI-powered topic summaries  
5. Updates Airtable records and the local ledger to prevent duplicate processing  
6. Sends a daily automated HTML email digest of newly processed posts  

The result is a fully automated, scalable competitive intelligence system requiring zero manual intervention.

---

## Architecture
```
Apify (Scheduled Scraper)
        │
        ▼
Airtable (Central Intelligence Database)
        │
        ▼
Python Intelligence Layer
   ├─ Ledger Sync (processed_urls.json)
   ├─ Airtable Client
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

Apify uses native Airtable Exporter integration to UPSERT records using URL as the primary key, preventing duplicates automatically.

---

### 2. Central Data Storage

Airtable acts as the structured intelligence database:

- Stores all raw post data
- Holds AI-generated topic summaries once enriched

---

### 3. Ledger-Based Processing State

Processing state is tracked via a local `processed_urls.json` ledger committed to the repository rather than relying on Airtable field state. This makes the pipeline resilient to external overwrites from Apify UPSERT operations.

At the start of every run the pipeline:

- Reads current Airtable state
- Adds URLs that have summaries but are missing from the ledger
- Removes URLs that are in the ledger but have lost their summary
- Saves the corrected ledger before processing begins

This self-healing sync ensures the ledger and Airtable remain consistent across runs without manual intervention.

---

### 4. Python Intelligence Layer

The Python pipeline:

- Syncs the ledger with Airtable state
- Queries Airtable for unprocessed posts (URLs not in ledger)
- Sends captions to an LLM client
- Generates a neutral 15–25 word topic summary
- Updates the Airtable record with the summary
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

- **Apify Scheduler** → Scraping
- **GitHub Actions (cron: 07:30 UTC daily)** → Ledger sync, Python enrichment, digest
- **SendGrid** → Email delivery

The GitHub Actions workflow commits the updated ledger back to the repository after each run.

All secrets are managed securely via:

- `.env` (local development)
- GitHub Actions Secrets (production)

No manual execution is required.

---

## What Changed vs v1

Version 2 introduced significant architectural improvements:

- Removed Make (reduced cost and complexity)
- Implemented native Apify → Airtable integration
- Introduced a dedicated Python intelligence layer
- Added modular LLM abstraction
- Implemented automated daily HTML email digest
- Added GitHub Actions scheduling
- Added secure secret management
- Reduced external orchestration dependencies
- Replaced Airtable field-based processing state with a local URL ledger, making the pipeline resilient to external field overwrites
- Added self-healing ledger sync at the start of every run

---

## Tech Stack

- Python
- OpenAI API (LLM abstraction layer)
- Apify
- Airtable
- SendGrid
- GitHub Actions (scheduler)
- dotenv

---

## Project Structure
```
src/
├── main.py              # Pipeline entry point
├── airtable_client.py   # Airtable integration and ledger management
├── llm_client.py        # LLM abstraction layer
├── email_client.py      # SendGrid HTML digest layer
├── models.py            # Data models
├── prompts.py           # Prompt templates
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
AIRTABLE_API_KEY
AIRTABLE_BASE_ID
AIRTABLE_TABLE_NAME
OPENAI_API_KEY
SENDGRID_API_KEY
SENDGRID_FROM_EMAIL
DIGEST_RECIPIENTS
MAX_POSTS_PER_RUN
```
6. Initialise the ledger: `echo "[]" > processed_urls.json`
7. Run the pipeline: `python src/main.py`

---

## Design Principles

- Modular integrations
- Clear separation of orchestration and API clients
- Idempotent processing (no duplicate summaries)
- Resilient state management via local ledger
- Self-healing sync on every run
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