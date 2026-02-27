import os
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Competitor_Posts")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_POSTS_PER_RUN = int(os.getenv("MAX_POSTS_PER_RUN"))

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
DIGEST_RECIPIENTS = os.getenv("DIGEST_RECIPIENTS")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")