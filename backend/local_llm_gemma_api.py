"""
LLM loader using OpenRouter REST API.

Set OPENROUTER_API_KEY in backend/.env

Example:
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxxxxxx
"""

import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()


def remove_thinking(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # Remove tokenizer artifacts
    text = re.sub(r"</?pad>", "", text)
    text = re.sub(r"</?bos>", "", text)
    text = re.sub(r"</?eos>", "", text)
    text = re.sub(r"<start_of_turn>", "", text)
    text = re.sub(r"<end_of_turn>", "", text)

    return text.strip()



def generate(
    user_prompt: str,
    system_prompt: str = "",
    max_tokens: int = 500,
    temperature: float = 0.1,
) -> str:
    """
    Run inference using OpenRouter REST API.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in .env")

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

    print("\nMESSAGES:")
    print(messages)

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "model": "google/gemma-4-26b-a4b-it:free",
                # "model": "openai/gpt-oss-20b:free",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "reasoning": {
                    "enabled": True
                },
            }
        ),
    )

    response.raise_for_status()

    result = response.json()

    print("\n" + "=" * 80)
    print("RAW RESPONSE")
    print(json.dumps(result, indent=2))
    print("=" * 80)

    text = result["choices"][0]["message"]["content"]

    text = remove_thinking(text)

    print(text)

    text = remove_thinking(text)

    return text