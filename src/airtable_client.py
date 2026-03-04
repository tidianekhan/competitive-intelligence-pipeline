from pyairtable import Table
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, MAX_POSTS_PER_RUN


def fetch_posts_needing_summary(limit=None):
    limit = limit or MAX_POSTS_PER_RUN

    table = Table(
        AIRTABLE_API_KEY,
        AIRTABLE_BASE_ID,
        AIRTABLE_TABLE_NAME,
    )

    print("Fetching posts where Processed is unchecked...")

    records = table.all(
        formula="{Processed} = 0",
        max_records=limit
    )

    print(f"Found {len(records)} posts needing summary")
    
    return records

if __name__ == "__main__":
    posts = fetch_posts_needing_summary(limit=5)

    for post in posts:
        print("------")
        print(post["fields"])

def update_post_summary(record_id: str, summary_text: str):
    table = Table(
        AIRTABLE_API_KEY,
        AIRTABLE_BASE_ID,
        AIRTABLE_TABLE_NAME,
    )

    table.update(record_id, {
        "Topic Summary": summary_text,
        "Processed": True
    })

    print(f"Updated record {record_id}")

