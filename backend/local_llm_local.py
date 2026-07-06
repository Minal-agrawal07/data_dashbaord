"""
Local LLM loader using llama-cpp-python.

Set GEMMA_MODEL_PATH in backend/.env to the absolute path of your GGUF file.
Example:
    GEMMA_MODEL_PATH=/Users/you/models/gemma-3-4b-it-q4_k_m.gguf

Optional tuning env vars:
    LLM_CONTEXT_SIZE  — context window in tokens (default: 8192)
    LLM_GPU_LAYERS    — layers to offload to GPU; -1 = all (default: -1)
    LLM_THREADS       — CPU threads when GPU is not used (default: 8)
"""
import re



import os
from functools import lru_cache
from llama_cpp import Llama
def remove_thinking(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


import time

@lru_cache(maxsize=1)
def load_model() -> Llama:
    model_path = r"C:\Users\agraw\OneDrive\Desktop\projectsss\models_run\models\gemma-4-E4B-it-IQ4_NL.gguf"
    if not model_path:
        raise RuntimeError(
            "GEMMA_MODEL_PATH is not set. "
            "Add it to backend/.env, e.g.:\n"
            "  GEMMA_MODEL_PATH=/path/to/gemma-3-4b-it-q4_k_m.gguf"
        )

    

    print(f"[local_llm] Loading model from {model_path} ...")

    start = time.perf_counter()

    model = Llama(
    model_path=model_path,
    n_ctx=8192,
    n_threads=8,
    verbose=False,
)

    end = time.perf_counter()

    print(f"[TIME] Model Load: {end-start:.3f} sec")
    print("[local_llm] Model loaded.")
    return model


def generate(
    user_prompt: str,
    system_prompt: str = "",
    max_tokens: int = 1024,
    temperature: float = 0.1,
) -> str:
    """
    Run inference on the loaded Gemma model.

    Gemma 3+ supports a system role natively via its chat template.
    For Gemma 2 the system content is merged into the first user turn
    since the template does not define a system role.
    """
    llm = load_model()
    

    # Detect whether the loaded model's chat template accepts a system role.
    # llama-cpp-python exposes the raw Jinja template string on the metadata dict.
    chat_template: str = (llm.metadata or {}).get("tokenizer.chat_template", "")
    supports_system_role = "system" in chat_template

    if system_prompt and supports_system_role:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    elif system_prompt:
        # Gemma 2: fold system prompt into the first user message
        messages = [{"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}]
    else:
        messages = [{"role": "user", "content": user_prompt}]

    print("MESSAGES:")
    print(messages)
    start = time.perf_counter()
    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
         
    
    )
    end = time.perf_counter()

    print(f"[TIME] LLM Inference: {end-start:.3f} sec")
    text = response["choices"][0]["message"]["content"]

    # print("\n" + "=" * 80)
    # print("RAW MODEL OUTPUT")
    # print(text)
    # print("=" * 80)

    text = remove_thinking(text).strip()

    return text
