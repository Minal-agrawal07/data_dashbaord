from llama_cpp import Llama

llm = Llama(
    model_path=r"C:\Users\agraw\OneDrive\Desktop\strtup\models\Qwen3-8B-Q4_K_M.gguf",
    n_ctx=2048,
    chat_format="chatml",
)

response = llm.create_chat_completion(
    messages=[
        {
            "role": "user",
            "content": "Hi"
        }
    ],
    max_tokens=1000,
    temperature=0.1,
    
)

print(response["choices"][0]["message"]["content"])