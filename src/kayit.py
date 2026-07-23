# kayit.py - Kayit katmani: birlestirme, radar.json ve arsiv.csv

import json
from datetime import date
import os
import csv

def raporu_birlestir(rapor, haberler):
    # Claude raporundaki kaynak_no'lari gercek haber bilgileriyle birlestirir
    tam_haberler = []
    for h in rapor["haberler"]:
        kaynak = haberler[h["kaynak_no"] - 1]
        tam_haber = {
             "sira": h["sira"],
            "baslik": kaynak["baslik"],
            "url": kaynak["link"],
            "kaynak": kaynak["kaynak"],
            "tarih": kaynak["tarih"],
            "ne_oldu": h["ne_oldu"],
            "ne_oldu_en": h["ne_oldu_en"],
            "senin_icin_neden_onemli": h["senin_icin_neden_onemli"],
            "senin_icin_neden_onemli_en": h["senin_icin_neden_onemli_en"],
            "ne_takip_edilmeli": h["ne_takip_edilmeli"],
            "ne_takip_edilmeli_en": h["ne_takip_edilmeli_en"],
            "onem_puani": h["onem_puani"]



        }
        tam_haberler.append(tam_haber)
    return {
        "rapor_tarihi": str(date.today()),
        "haberler": tam_haberler
    }

def radar_json_yaz(tam_rapor):
    # Tam raporu docs/radar.json'a yazar (GitHub Pages bunu yayinlayacak)
    os.makedirs("docs", exist_ok=True)
    with open("docs/radar.json", "w", encoding="utf-8") as f:
        json.dump(tam_rapor, f, ensure_ascii=False, indent=2) 


def arsive_ekle(tam_rapor):
    # Haberleri data/arsiv.csv'ye ekler (append) - gecmis birikir
    os.makedirs("data", exist_ok=True)
    dosya_var = os.path.exists("data/arsiv.csv")
    sutunlar = ["rapor_tarihi", "sira", "baslik", "url", "kaynak", "tarih",
                "ne_oldu", "ne_oldu_en", "senin_icin_neden_onemli",
                "senin_icin_neden_onemli_en", "ne_takip_edilmeli",
                "ne_takip_edilmeli_en", "onem_puani"]
    with open("data/arsiv.csv", "a", encoding="utf-8", newline="") as f:
        yazici = csv.DictWriter(f, fieldnames=sutunlar)
        if not dosya_var:
            yazici.writeheader()
        for h in tam_rapor["haberler"]:
            satir = dict(h)
            satir["rapor_tarihi"] = tam_rapor["rapor_tarihi"]
            yazici.writerow(satir)


if __name__ == "__main__":
    # Test: sahte mini rapor ile birlestirmeyi dene
    with open("haberler.json", "r", encoding="utf-8") as f:
        haberler = json.load(f)

    sahte_rapor = {
        "haberler": [
            {"sira": 1, "kaynak_no": 1, "ne_oldu": "test", "ne_oldu_en": "test",
             "senin_icin_neden_onemli": "test", "senin_icin_neden_onemli_en": "test",
             "ne_takip_edilmeli": "test", "ne_takip_edilmeli_en": "test", "onem_puani": 9},
            {"sira": 2, "kaynak_no": 5, "ne_oldu": "test", "ne_oldu_en": "test",
             "senin_icin_neden_onemli": "test", "senin_icin_neden_onemli_en": "test",
             "ne_takip_edilmeli": "test", "ne_takip_edilmeli_en": "test", "onem_puani": 8}
        ]
    }

    sonuc = raporu_birlestir(sahte_rapor, haberler)
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    radar_json_yaz(sonuc)
    print("docs/radar.json yazildi.")
    arsive_ekle(sonuc)
    print("data/arsiv.csv guncellendi.")