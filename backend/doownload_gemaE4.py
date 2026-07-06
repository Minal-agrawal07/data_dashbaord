from huggingface_hub import hf_hub_download

hf_hub_download(
    repo_id="unsloth/gemma-4-E4B-it-GGUF",
    filename="gemma-4-E4B-it-IQ4_NL.gguf",
    local_dir=r"C:\Users\agraw\OneDrive\Desktop\strtup\models",
    local_dir_use_symlinks=False,
)

print("Download complete!")