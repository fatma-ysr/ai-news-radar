import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("HATA: API anahtari bulunamadi! .env dosyasini kontrol et.")
    exit()

print("Anahtar bulundu, ilk 10 karakter:", api_key[:10] + "...")

client = Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Merhaba Claude! Bana bir şiir yazabilir misin?"
        }
    ]
)

print("Claude'un cevabi:", message.content[0].text)