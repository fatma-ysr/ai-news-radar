

from http import client
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import json


SISTEM_PROMPTU = """
You are a personal news analyst and curator for a weekly AI and data news radar.

READER PROFILE:
- 4th-year Statistics student at Marmara University, aiming for AI-focused and data-related roles.
- Knows: Python (pandas, sklearn), statistics, Power BI, Excel.
- Also interested in design and data visualization.
- The field "senin_icin_neden_onemli" must be written from this reader's perspective:
  why does this news matter for her skills, studies, or career goals?

TASK:
- The user message contains a numbered list of news items, each starting with [N].
- Select EXACTLY 10 items: the most important and most relevant for this reader.
- Diversity rule: mix research papers, industry/product news, and open-source news.
  Do not select more than 4 items from the same source.
- Give each selected item an "onem_puani" (importance score) from 1 to 10.
- Sort the report by "onem_puani" in DESCENDING order and number "sira" from 1 to 10.

OUTPUT FORMAT:
Respond with ONLY a valid JSON object. No explanation before or after.
No markdown, no code fences. Use exactly this structure:

{
  "haberler": [
    {
      "sira": 1,
      "kaynak_no": 17,
      "ne_oldu": "...",
      "ne_oldu_en": "...",
      "senin_icin_neden_onemli": "...",
      "senin_icin_neden_onemli_en": "...",
      "ne_takip_edilmeli": "...",
      "ne_takip_edilmeli_en": "...",
      "onem_puani": 9
    }
  ]
}

FIELD RULES:
- "kaynak_no": the [N] number of the item in the input list. Never invent a number.
- "ne_oldu": 1-2 sentences in TURKISH describing what happened.
- "senin_icin_neden_onemli": 1-2 sentences in TURKISH, personalized to the reader profile.
- "ne_takip_edilmeli": 1 sentence in TURKISH about what to watch next.
- Fields ending with "_en": the same content in ENGLISH.
"""

def ozetle(haberler):
    # Haber listesini Claude'a gonderir, JSON rapor dondurur.
    # Basarisiz olursa None doner.
    haber_metni = ""
    for i, haber in enumerate(haberler, start=1):
        aciklama = haber["aciklama"][:200]
        haber_metni += f"[{i}] {haber['baslik']}\n"
        haber_metni += f"Kaynak: {haber['kaynak']}, Tarih: {haber['tarih']}\n"
        haber_metni += f"Ozet: {aciklama}\n\n"

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("HATA: API anahtari bulunamadi! .env dosyasini kontrol et.")
        return None

    client = Anthropic(api_key=api_key)
    print("Claude'a gonderiliyor, bekle... (30-60 saniye surebilir)")

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        system=SISTEM_PROMPTU,
        messages=[
            {"role": "user", "content": haber_metni}
        ]
    )

    cevap = message.content[0].text

    if message.stop_reason == "max_tokens":
        print("UYARI: Cevap token limitine takildi, JSON kesik olabilir!")

    temiz = cevap.strip()
    if temiz.startswith("```"):
        temiz = temiz.split("\n", 1)[1]
        temiz = temiz.rsplit("```", 1)[0]

    try:
        rapor = json.loads(temiz)
    except json.JSONDecodeError as e:
        print("JSON decode hatasi:", e)
        return None

    print("JSON gecerli! Secilen haber sayisi:", len(rapor["haberler"]))
    return rapor