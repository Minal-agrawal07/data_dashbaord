"""
LLM loader using Hugging Face Space API.

Set these in backend/.env

HF_API_URL=https://yashagrawal19-gemmamodelapi.hf.space/generate
HF_API_KEY=your_api_key
"""

import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()


def remove_thinking(text: str) -> str:
    """
    Removes <think>...</think> blocks if the model returns them.
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


API_URL = os.getenv("HF_API_URL")
API_KEY = os.getenv("HF_API_KEY")


def generate(
    user_prompt: str,
    system_prompt: str = "",
    max_tokens: int = 256,
    temperature: float = 0.1,
) -> str:
    """
    Run inference using the Hugging Face Space API.
    """

    payload = {
  "prompt": user_prompt,
  "system_prompt": system_prompt,
  "max_tokens": max_tokens,
  "temperature": temperature,
  "top_p": 1,
  "stream": False
}
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-api-key": API_KEY,
    }

    print("\n" + "=" * 80)
    print("REQUEST PAYLOAD")
    print(payload)
    print("=" * 80)

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=1800,
    )

    response.raise_for_status()

    result = response.json()

    print("\n" + "=" * 80)
    print("RAW API RESPONSE")
    print(result)
    print("=" * 80)

    text = result.get("response", "")

    text = remove_thinking(text)

    return text