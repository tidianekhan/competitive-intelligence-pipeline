# src/main.py

from airtable_client import fetch_posts_needing_summary, update_post_summary
from llm_client import generate_summary
from config import MAX_POSTS_PER_RUN
from email_client import send_digest_email


if __name__ == "__main__":
    print("🚀 Running Insta Intel Pipeline")

    posts = fetch_posts_needing_summary(limit=MAX_POSTS_PER_RUN)
    processed_records = []

    if not posts:
        print("No posts need processing.")
    else:
        for post in posts:
            record_id = post["id"]

            # Your Airtable field name for caption is lowercase in your current setup
            caption = post["fields"].get("caption", "")

            print(f"\nProcessing: {record_id}")

            summary_text = generate_summary(caption)
            update_post_summary(record_id, summary_text)

            # Keys here should match what email_client.py expects
            processed_records.append(
                {
                    "ownerFullName": post["fields"].get("ownerFullName", ""),
                    "timestamp": post["fields"].get("timestamp", ""),
                    "topicSummary": summary_text,
                    "url": post["fields"].get("url", ""),
                }
            )

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