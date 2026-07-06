"""
LLM loader using OpenRouter API.

Set OPENROUTER_API_KEY in backend/.env

Example:
    OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxxxxxx
"""

import os
import re
from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI


def remove_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


# Create OpenRouter client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def generate(
    user_prompt: str,
    system_prompt: str = "",
    max_tokens: int = 1024,
    temperature: float = 0.1,
) -> str:
    """
    Run inference using an OpenRouter-hosted model.
    """

    messages = []

    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    print("MESSAGES:")
    print(messages)

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    text = response.choices[0].message.content or ""

    print("\n" + "=" * 80)
    print("RAW MODEL OUTPUT")
    print(text)
    print("=" * 80)

    text = remove_thinking(text)

    return text