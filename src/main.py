# main.py - Boru hattinin giris noktasi: topla -> ozetle -> kaydet

from kaynaklar import haberleri_topla
from ozetleyici import ozetle
from kayit import raporu_birlestir, radar_json_yaz, arsive_ekle


def main():
    # 1) Haberleri topla
    haberler = haberleri_topla()
    if not haberler:
        print("HATA: Hic haber toplanamadi, akis durduruldu.")
        return

    # 2) Claude ile ozetle
    rapor = ozetle(haberler)
    if rapor is None:
        print("HATA: Ozetleme basarisiz, radar.json korundu.")
        return

    # 3) Kaydet
    tam_rapor = raporu_birlestir(rapor, haberler)
    radar_json_yaz(tam_rapor)
    arsive_ekle(tam_rapor)

    print("\nTAMAM: docs/radar.json ve data/arsiv.csv guncellendi.")
    print(f"Rapor tarihi: {tam_rapor['rapor_tarihi']}, haber sayisi: {len(tam_rapor['haberler'])}")


if __name__ == "__main__":
    main()