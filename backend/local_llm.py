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
    # Remove thinking blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # Remove Gemma tokenizer artifacts
    text = re.sub(r"</?pad>", "", text)
    text = re.sub(r"</?bos>", "", text)
    text = re.sub(r"</?eos>", "", text)
    text = re.sub(r"<start_of_turn>", "", text)
    text = re.sub(r"<end_of_turn>", "", text)

    return text.strip()


# Create OpenRouter client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def generate(
    user_prompt: str,
    system_prompt: str = "",
    max_tokens: int = 500,
    temperature: float = 0.1,
    model: str = "openai/gpt-oss-20b:free",
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
    model=model,
    messages=messages,
    temperature=temperature,
    max_tokens=max_tokens,
)
    print("\n========== FULL RESPONSE ==========")
    print(response.model_dump_json(indent=2))
    print("===================================\n")

    text = response.choices[0].message.content or ""

    print("\n" + "=" * 80)
    print("RAW MODEL OUTPUT")
    print(text)
    print("=" * 80)

# Only clean Gemma outputs
    if "gemma" in model.lower():
     text = remove_thinking(text)

    return text