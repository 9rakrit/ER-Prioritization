from huggingface_hub import InferenceClient
import os

client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=os.getenv("HUGGINGFACE_API_KEY")
)

print(client.text_generation("Hello, what is emergency triage?", max_new_tokens=30))
