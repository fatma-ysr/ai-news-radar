"""
AI/ML HAFTALIK HABER RADARI - 1. GUN: VERI TOPLAMA MOTORU
=========================================================
Bu script ne yapar?
1. Asagidaki KAYNAKLAR listesindeki RSS adreslerine tek tek gider
2. Son 7 gunde yayinlanmis haberleri toplar
3. Ayni haber birden fazla kaynakta ciktiysa tekrarlari ayiklar
4. Sonucu hem ekrana yazar hem de 'haberler.json' dosyasina kaydeder
   (JSON = verileri duzenli saklamak icin kullanilan basit metin formati.
    2. gun bu dosyayi okuyup ozetletip Notion'a yazacagiz.)

Calistirmak icin terminalde:
    pip install feedparser
    python gun1_haber_toplayici.py
"""

import feedparser          # RSS beslemelerini okuyan kutuphane
import json                # Veriyi dosyaya kaydetmek icin
import time                # Tarih hesaplamalari icin
from datetime import datetime, timedelta
import requests



# ---------------------------------------------------------------
# 1) KAYNAK LISTESI
# Her kaynak: (Gorunen isim, RSS adresi)
# Yeni kaynak eklemek istersen buraya bir satir eklemen yeterli.
# ---------------------------------------------------------------
KAYNAKLAR = [
   
    ("arXiv - Makine Ogrenmesi (cs.LG)",
     "https://rss.arxiv.org/rss/cs.LG"),

    ("arXiv - Dil Isleme (cs.CL)",
     "https://rss.arxiv.org/rss/cs.CL"),

    ("Google AI Blog",
     "https://blog.google/technology/ai/rss/"),

    ("Hugging Face Blog",
     "https://huggingface.co/blog/feed.xml"),

    ("TechCrunch AI",
     "https://techcrunch.com/category/artificial-intelligence/feed/"),

     ("arXiv - Istatistik ML (stat.ML)",
     "https://rss.arxiv.org/rss/stat.ML"),

    ("The Verge AI",
     "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),

    ("MIT Technology Review (AI)",
     "https://www.technologyreview.com/topic/artificial-intelligence/feed"),

    ("Google News (AI)",
     "https://news.google.com/rss/search?q=artificial+intelligence&hl=tr&gl=TR&ceid=TR:tr"),
]

# Kac gunluk haber toplansin?
GUN_SAYISI = 7

# arXiv gunde yuzlerce makale yayinlar; hepsini almak bogar.
# Her kaynaktan en fazla kac haber alinsin?
KAYNAK_BASINA_LIMIT = 15


def tarihi_al(haber):
    """
    RSS'teki her haberin yayin tarihi farkli alanlarda gelebilir.
    Bu fonksiyon hangisi doluysa onu bulup Python tarihine cevirir.
    Tarih hic yoksa None doner.
    """
    for alan in ("published_parsed", "updated_parsed"):
        deger = haber.get(alan)
        if deger:
            return datetime.fromtimestamp(time.mktime(deger))
    return None


def kaynagi_tara(kaynak_adi, rss_adresi, en_eski_tarih):
    """
    Tek bir RSS kaynagina gider, son 7 gunun haberlerini liste olarak doner.
    Her haber bir 'sozluk' (dictionary) olarak tutulur: {"baslik": ..., "link": ...}
    """
    print(f"  Taraniyor: {kaynak_adi} ...", end=" ")

    besleme = feedparser.parse(rss_adresi)   # RSS'i indir ve cozumle

    # bozo=1 -> besleme okunurken sorun cikti demektir (site cokmus olabilir)
    if besleme.bozo and not besleme.entries:
        print("HATA - kaynak okunamadi, atlandi.")
        return []

    haberler = []
    for haber in besleme.entries[:KAYNAK_BASINA_LIMIT]:
        tarih = tarihi_al(haber)

        # Tarihi olmayan ya da 7 gunden eski haberleri atla
        if tarih is None or tarih < en_eski_tarih:
            continue

        haberler.append({
            "baslik":  haber.get("title", "(basliksiz)").strip(),
            "link":    haber.get("link", ""),
            "kaynak":  kaynak_adi,
            "tarih":   tarih.strftime("%Y-%m-%d"),
            # summary alani bazi kaynaklarda HTML icerir; 2. gun
            # Claude'a ozetletirken ham metin olarak isimize yarayacak.
            "aciklama": haber.get("summary", "")[:500],
        })

    print(f"{len(haberler)} haber bulundu.")
    return haberler


def tekrarlari_ayikla(haberler):
    """
    Ayni link iki kaynakta ciktiysa birini at.
    Ayrica birebir ayni basligi da tekrar sayariz.
    """
    gorulen_linkler = set()   # set = "daha once gordum mu?" kontrolu icin hizli liste
    gorulen_basliklar = set()
    temiz = []

    for h in haberler:
        anahtar_link = h["link"].rstrip("/")
        anahtar_baslik = h["baslik"].lower()

        if anahtar_link in gorulen_linkler or anahtar_baslik in gorulen_basliklar:
            continue  # tekrar -> atla

        gorulen_linkler.add(anahtar_link)
        gorulen_basliklar.add(anahtar_baslik)
        temiz.append(h)

    return temiz

def hacker_news_tara(en_eski_tarih):
    """
    Hacker News'i resmi Algolia API'sinden ceker (RSS degil, JSON API).
    Son 7 gunde 100+ puan almis, AI/LLM/GPT gecen hikayeler.
    """
    print("  Taraniyor: Hacker News (Algolia API) ...", end=" ")

    epoch = int(en_eski_tarih.timestamp())  # API tarihi sayi olarak ister
    adres = "https://hn.algolia.com/api/v1/search"
    parametreler = {
        "query": "AI OR LLM OR GPT",
        "tags": "story",
        "numericFilters": f"created_at_i>{epoch}",
        "hitsPerPage": 50,
    }

    try:
        cevap = requests.get(adres, params=parametreler, timeout=15)
        cevap.raise_for_status()          # 200 degilse hata firlat
        sonuc = cevap.json()              # JSON cevabi Python sozlugune cevir
    except Exception as hata:
        print(f"HATA - {hata}")
        return []

    haberler = []
    for hikaye in sonuc.get("hits", []):
        if hikaye.get("points", 0) < 100:
            continue  # dusuk puanli hikayeleri biz eliyoruz (API filtrelemiyor)
        haberler.append({
            "baslik":   hikaye.get("title", "(basliksiz)").strip(),
            "link":     hikaye.get("url") or f"https://news.ycombinator.com/item?id={hikaye.get('objectID')}",
            "kaynak":   "Hacker News",
            "tarih":    hikaye.get("created_at", "")[:10],
            "aciklama": f"HN puani: {hikaye.get('points', 0)}",
        })
    haberler = haberler[:KAYNAK_BASINA_LIMIT]    
    print(f"{len(haberler)} haber bulundu.")
    return haberler

def main():
    print("=" * 60)
    print("AI/ML HABER RADARI - Veri Toplama Basliyor")
    print("=" * 60)

    en_eski_tarih = datetime.now() - timedelta(days=GUN_SAYISI)
    tum_haberler = []
    tum_haberler.extend(hacker_news_tara(en_eski_tarih))

    for kaynak_adi, rss_adresi in KAYNAKLAR:
        tum_haberler.extend(kaynagi_tara(kaynak_adi, rss_adresi, en_eski_tarih))

    print(f"\nToplam ham haber: {len(tum_haberler)}")

    tum_haberler = tekrarlari_ayikla(tum_haberler)
    print(f"Tekrarlar ayiklandiktan sonra: {len(tum_haberler)}")

    # Yeniden eskiye sirala
    tum_haberler.sort(key=lambda h: h["tarih"], reverse=True)

    # JSON dosyasina kaydet (2. gunun girdisi bu dosya olacak)
    with open("haberler.json", "w", encoding="utf-8") as dosya:
        json.dump(tum_haberler, dosya, ensure_ascii=False, indent=2)

    print("\n'haberler.json' dosyasina kaydedildi. Ilk 5 haber:\n")
    for h in tum_haberler[:5]:
        print(f"  [{h['tarih']}] {h['kaynak']}")
        print(f"    {h['baslik']}")
        print(f"    {h['link']}\n")


if __name__ == "__main__":
    main()
