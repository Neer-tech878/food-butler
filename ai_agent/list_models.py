# list_models.py - NVIDIA NIM version
import os
from dotenv import load_dotenv
from openai import OpenAI

try:
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY not found in .env file or environment variables.")

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
    )

    print("--- Successfully configured NVIDIA NIM API Key ---")
    print("--- Fetching available models... ---")

    models = client.models.list()
    print(f"\nAvailable NVIDIA NIM Models ({len(models.data)} found):")
    for m in sorted(models.data, key=lambda x: x.id):
        print(f"  -> {m.id}")

except Exception as e:
    print(f"\n--- An error occurred ---")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    print("\n--- Please check your NVIDIA_API_KEY in the .env file. ---")