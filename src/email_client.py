import os
from typing import List, Dict
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def build_digest_html(rows: List[Dict[str, str]]) -> str:
    """Builds the HTML table for the digest email."""

    table_rows = ""

    for row in rows:
        table_rows += f"""
        <tr>
            <td>{row.get("ownerFullName", "")}</td>
            <td>{row.get("timestamp", "")}</td>
            <td>{row.get("topicSummary", "")}</td>
            <td><a href="{row.get("url", "")}">View Post</a></td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>📊 Daily Competitor Instagram Digest</h2>
        <p>The following posts were summarized today:</p>

        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <thead style="background-color:#f2f2f2;">
                <tr>
                    <th>Competitor</th>
                    <th>Timestamp</th>
                    <th>Topic Summary</th>
                    <th>Post Link</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <p style="margin-top:20px; font-size:12px; color:gray;">
            Automated Competitive Intelligence System – v2
        </p>
    </body>
    </html>
    """

    return html


def send_digest_email(rows: List[Dict[str, str]]) -> None:
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL")
    recipients = os.getenv("DIGEST_RECIPIENTS", "")

    if not api_key or not from_email or not recipients:
        raise ValueError("Missing SendGrid environment variables")

    to_emails = [email.strip() for email in recipients.split(",")]

    html_content = build_digest_html(rows)

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject="Daily Competitor Instagram Digest",
        html_content=html_content,
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)

    print(f"Digest sent (status {response.status_code})")