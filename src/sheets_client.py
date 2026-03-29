import json
import os
import gspread
from google.oauth2.service_account import Credentials
from config import MAX_POSTS_PER_RUN

LEDGER_PATH = "processed_urls.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_sheet():
    credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    if not credentials_json:
        # Fall back to local JSON file for local development
        credentials_json = open("google_credentials.json").read()

    credentials_dict = json.loads(credentials_json)
    creds = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).sheet1


def load_processed_urls() -> set:
    if not os.path.exists(LEDGER_PATH):
        return set()
    with open(LEDGER_PATH, "r") as f:
        return set(json.load(f))


def save_processed_urls(urls: set):
    with open(LEDGER_PATH, "w") as f:
        json.dump(sorted(list(urls)), f, indent=2)


def fetch_posts_needing_summary(limit=None) -> tuple[list, set]:
    limit = limit or MAX_POSTS_PER_RUN
    sheet = get_sheet()
    processed_urls = load_processed_urls()

    print("Fetching all records from Google Sheets...")
    rows = sheet.get_all_records()
    print(f"Total records in sheet: {len(rows)}")
    print(f"Total URLs in ledger: {len(processed_urls)}")

    unprocessed = [
        r for r in rows
        if r.get("url") and r.get("url") not in processed_urls
    ]

    remaining_total = len(unprocessed)
    unprocessed = unprocessed[:limit]

    print(f"Found {len(unprocessed)} posts to process this run")
    print(f"Total still unprocessed in sheet: {remaining_total}")
    print(f"Remaining after this run: {remaining_total - len(unprocessed)}")

    return unprocessed, processed_urls


def update_post_summary(url: str, summary_text: str) -> bool:
    if not summary_text or not summary_text.strip():
        print(f"Skipping {url} — empty summary")
        return False

    try:
        sheet = get_sheet()
        rows = sheet.get_all_records()
        headers = sheet.row_values(1)

        # Find the Topic Summary column index
        if "Topic Summary" not in headers:
            print("❌ 'Topic Summary' column not found in sheet")
            return False

        summary_col = headers.index("Topic Summary") + 1  # gspread is 1-indexed

        # Find the row with matching URL
        url_col = headers.index("url") + 1
        for i, row in enumerate(rows, start=2):  # start=2 because row 1 is headers
            if row.get("url") == url:
                sheet.update_cell(i, summary_col, summary_text)
                print(f"Updated row {i} for {url}")
                return True

        print(f"❌ URL not found in sheet: {url}")
        return False

    except Exception as e:
        print(f"❌ Failed to update summary for {url}: {e}")
        return False