import json
import os
from pyairtable import Api
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, MAX_POSTS_PER_RUN

LEDGER_PATH = "processed_urls.json"


def get_table():
    api = Api(AIRTABLE_API_KEY)
    return api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)


def load_processed_urls() -> set:
    if not os.path.exists(LEDGER_PATH):
        return set()
    with open(LEDGER_PATH, "r") as f:
        return set(json.load(f))


def save_processed_urls(urls: set):
    with open(LEDGER_PATH, "w") as f:
        json.dump(sorted(list(urls)), f, indent=2)


def sync_ledger_with_airtable() -> set:
    current_ledger = load_processed_urls()
    print(f"Ledger loaded: {len(current_ledger)} URLs")
    return current_ledger


def fetch_posts_needing_summary(limit=None, existing_urls=None) -> tuple[list, set]:
    limit = limit or MAX_POSTS_PER_RUN
    table = get_table()
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
    table = get_table()

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
