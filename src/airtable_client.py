import json
import os
from pyairtable import Table
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, MAX_POSTS_PER_RUN

LEDGER_PATH = "processed_urls.json"


def load_processed_urls() -> set:
    if not os.path.exists(LEDGER_PATH):
        return set()
    with open(LEDGER_PATH, "r") as f:
        return set(json.load(f))


def save_processed_urls(urls: set):
    with open(LEDGER_PATH, "w") as f:
        json.dump(sorted(list(urls)), f, indent=2)


def sync_ledger_with_airtable() -> set:
    table = Table(
        AIRTABLE_API_KEY,
        AIRTABLE_BASE_ID,
        AIRTABLE_TABLE_NAME,
    )

    print("Syncing ledger with Airtable...")
    all_records = table.all()

    has_summary = {
        r["fields"].get("url")
        for r in all_records
        if r["fields"].get("Topic Summary")
        and r["fields"].get("url")
    }

    no_summary = {
        r["fields"].get("url")
        for r in all_records
        if not r["fields"].get("Topic Summary")
        and r["fields"].get("url")
    }

    current_ledger = load_processed_urls()

    # Only remove URLs that were previously processed but have lost their summary
    # NOT all unprocessed records (which would shrink the ledger incorrectly)
    ledger_with_no_summary = current_ledger & no_summary

    synced = (current_ledger | has_summary) - ledger_with_no_summary
    save_processed_urls(synced)

    print(f"Ledger synced: {len(current_ledger)} → {len(synced)}")
    return synced


def fetch_posts_needing_summary(limit=None, existing_urls=None) -> tuple[list, set]:
    limit = limit or MAX_POSTS_PER_RUN

    table = Table(
        AIRTABLE_API_KEY,
        AIRTABLE_BASE_ID,
        AIRTABLE_TABLE_NAME,
    )

    processed_urls = existing_urls if existing_urls is not None else load_processed_urls()

    print("Fetching all records from Airtable...")
    all_records = table.all()
    print(f"Total records in Airtable: {len(all_records)}")
    print(f"Total URLs in ledger: {len(processed_urls)}")

    remaining_total = len([
        r for r in all_records
        if r["fields"].get("url") not in processed_urls
    ])

    unprocessed = [
        r for r in all_records
        if r["fields"].get("url") not in processed_urls
    ][:limit]

    print(f"Found {len(unprocessed)} posts to process this run")
    print(f"Total still unprocessed in Airtable: {remaining_total}")
    print(f"Remaining after this run: {remaining_total - len(unprocessed)}")

    return unprocessed, processed_urls


def update_post_summary(record_id: str, summary_text: str) -> bool:
    table = Table(
        AIRTABLE_API_KEY,
        AIRTABLE_BASE_ID,
        AIRTABLE_TABLE_NAME,
    )

    if not summary_text or not summary_text.strip():
        print(f"Skipping record {record_id} — empty summary, not marking as processed")
        return False

    try:
        table.update(record_id, {
            "Topic Summary": summary_text,
        })
        print(f"Updated record {record_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to update record {record_id}: {e}")
        return False


if __name__ == "__main__":
    posts, processed_urls = fetch_posts_needing_summary(limit=5)

    for post in posts:
        print("------")
        print(post["fields"])