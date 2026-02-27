from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_summary(caption: str) -> str:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
                You generate structured competitor intelligence summaries.

                Return:

                1. A 15–25 word neutral topic summary.
                2. Then add a short section titled:

                Similar Content Suggestions:
                3. Provide 2 concise post ideas in similar tone and format.

                Keep tone analytical and professional.
                Do not exceed 120 words total.
                """
            },
            {
                "role": "user",
                "content": f"Summarize this Instagram post caption in 15–25 neutral words:\n\n{caption}"
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()