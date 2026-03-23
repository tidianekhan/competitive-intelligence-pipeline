# src/main.py

import re
from airtable_client import fetch_posts_needing_summary, update_post_summary, save_processed_urls, sync_ledger_with_airtable
from llm_client import generate_summary
from config import MAX_POSTS_PER_RUN
from email_client import send_digest_email


def is_meaningful_caption(caption: str) -> bool:
    # Strip emojis, punctuation and whitespace, check if anything meaningful remains
    cleaned = re.sub(r'[^\w\s]', '', caption, flags=re.UNICODE).strip()
    return len(cleaned) > 20


if __name__ == "__main__":
    print("🚀 Running Insta Intel Pipeline")

    # Sync ledger with Airtable state before processing
    synced_urls = sync_ledger_with_airtable()

    posts, processed_urls = fetch_posts_needing_summary(
        limit=MAX_POSTS_PER_RUN,
        existing_urls=synced_urls
    )

    processed_records = []

    if not posts:
        print("No posts need processing.")
    else:
        for post in posts:
            record_id = post["id"]
            url = post["fields"].get("url", "")
            caption = post["fields"].get("caption", "")

            print(f"\nProcessing: {record_id}")

            if not is_meaningful_caption(caption):
                print(f"⚠️ Skipping {record_id} — caption too short or emoji only")
                processed_urls.add(url)  # add to ledger so it isn't retried daily
                continue

            summary_text = generate_summary(caption)
            success = update_post_summary(record_id, summary_text)

            if success:
                processed_urls.add(url)
                processed_records.append(
                    {
                        "ownerFullName": post["fields"].get("ownerFullName", ""),
                        "timestamp": post["fields"].get("timestamp", ""),
                        "topicSummary": summary_text,
                        "url": url,
                    }
                )

    # Save ledger regardless of whether anything was processed
    save_processed_urls(processed_urls)
    print(f"💾 Ledger saved with {len(processed_urls)} total URLs.")

    # Send digest email if we processed anything
    if processed_records:
        try:
            send_digest_email(processed_records)
            print("📧 Daily digest sent.")
        except Exception as e:
            print(f"❌ Digest email failed: {e}")
    else:
        print("No new summaries generated. Email not sent.")

    print("\n✅ Pipeline complete.")