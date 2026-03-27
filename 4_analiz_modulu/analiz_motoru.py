import pandas as pd
import sys
import os

sys.path.append(r'C:\YazilimProjem\2_ner_modulu')
sys.path.append(r'C:\YazilimProjem\3_finbert_modulu')

from varlik_tespit import varlik_tespit_et
from duygu_analiz import metin_analiz_et
print("📂 Korelasyon matrisi yükleniyor...")
try:
    KORELASYON = pd.read_csv(
        r'C:\YazilimProjem\data\korelasyon\korelasyon_matrisi.csv',
        index_col=0
    )
    print(f"✅ Korelasyon matrisi yüklendi. ({len(KORELASYON)} varlık)\n")
except Exception as e:
    print(f"❌ Korelasyon matrisi yüklenemedi: {e}")
    sys.exit(1)

DUYGU_YON = {
    "positive": +1.0,
    "negative": -1.0,
    "neutral":   0.0
}
TUM_VARLIKLAR = ["Altin", "Bitcoin", "Dolar_TL", "THYAO", "BIST100", "Tesla", "Petrol", "Gumus"]

ETKI_ESIKLERI = {
    "guclu":  0.15, 
    "orta":   0.07,   
    "zayif":  0.02,   
}

ETKI_EMOJI = {
    "guclu_pos":  "🟢⬆️",
    "orta_pos":   "🟢",
    "zayif_pos":  "🔼",
    "ihmal":      "⚪",
    "zayif_neg":  "🔽",
    "orta_neg":   "🔴",
    "guclu_neg":  "🔴⬇️"
}
def etki_hesapla(duygu_sonucu: dict, tespit_edilen_varliklar: list) -> dict:
    """
    NER ve FinBERT sonuçlarını korelasyon matrisiyle birleştirerek
    tüm varlıklar için etki tahmini hesaplar.

    Mantık:
    1. Haberde geçen varlıklar için FinBERT skoru → yönlü etki
    2. Bu etkiyi korelasyon matrisi ile diğer varlıklara yay
    3. Her varlık için toplam etki skoru hesapla

    Örnek:
    - Haber: "Fed faiz artırdı, altın düştü" → %93 negatif
    - Altın için direkt etki: -0.93
    - Gümüş için dolaylı etki: -0.93 × 0.78 (korelasyon) = -0.73
    - Bitcoin için dolaylı etki: -0.93 × 0.12 = -0.11
    """

    ana_duygu = duygu_sonucu["ana_duygu"]
    guven = duygu_sonucu["guven"]
    yon = DUYGU_YON[ana_duygu]
    duygu_skoru = yon * guven
    MATRIS_VARLIKLARI = set(KORELASYON.columns)
    direkt_varliklar = [v for v in tespit_edilen_varliklar if v in MATRIS_VARLIKLARI]
    if not direkt_varliklar:
        direkt_varliklar = ["BIST100"] 
    etki_sonuclari = {}

    for hedef in TUM_VARLIKLAR:
        toplam_etki = 0.0
        katki_detaylari = []

        for kaynak in direkt_varliklar:
            if kaynak in KORELASYON.columns and hedef in KORELASYON.index:
                korelasyon_katsayisi = KORELASYON[kaynak][hedef]
                katki = duygu_skoru * korelasyon_katsayisi
                if kaynak == hedef:
                    katki = duygu_skoru * 1.0 
                toplam_etki += katki
                katki_detaylari.append({
                    "kaynak": kaynak,
                    "korelasyon": round(korelasyon_katsayisi, 3),
                    "katki": round(katki, 4)
                })
        if len(direkt_varliklar) > 1:
            toplam_etki /= len(direkt_varliklar)

        etki_sonuclari[hedef] = {
            "etki_skoru": round(toplam_etki, 4),
            "katki_detaylari": katki_detaylari
        }

    return etki_sonuclari


def etki_siniflandir(etki_skoru: float) -> str:
    """Etki skorunu sınıflandırır ve emoji döndürür."""
    abs_etki = abs(etki_skoru)
    pozitif = etki_skoru > 0

    if abs_etki > ETKI_ESIKLERI["guclu"]:
        return ETKI_EMOJI["guclu_pos"] if pozitif else ETKI_EMOJI["guclu_neg"]
    elif abs_etki > ETKI_ESIKLERI["orta"]:
        return ETKI_EMOJI["orta_pos"] if pozitif else ETKI_EMOJI["orta_neg"]
    elif abs_etki > ETKI_ESIKLERI["zayif"]:
        return ETKI_EMOJI["zayif_pos"] if pozitif else ETKI_EMOJI["zayif_neg"]
    else:
        return ETKI_EMOJI["ihmal"]
def makale_analiz_et(metin: str) -> dict:
    """
    Tek giriş noktası. Bir makale/haber verilince tam analiz yapar.

    Döndürdüğü şey:
    {
        "duygu": { ana_duygu, skorlar, guven, ... },
        "tespit_edilen_varliklar": [...],
        "tespit_edilen_olaylar": [...],
        "etki_analizi": {
            "Altin": { etki_skoru, katki_detaylari },
            "Bitcoin": { ... },
            ...
        }
    }
    """

    print("\n" + "="*65)
    print("🔍 ANALİZ BAŞLIYOR...")
    print("="*65)
    print("\n[1/3] 🏷️  Varlık tespiti yapılıyor (NER)...")
    ner_sonucu = varlik_tespit_et(metin)
    tespit_edilen = ner_sonucu["bulunan_varliklar"]
    tespit_edilen_olaylar = ner_sonucu["bulunan_olaylar"]
    print(f"      Tespit edilen varlıklar: {tespit_edilen if tespit_edilen else 'Genel piyasa haberi'}")
    print(f"      Olay kategorisi: {tespit_edilen_olaylar if tespit_edilen_olaylar else 'Belirlenemedi'}")
    print("\n[2/3] 🧠  Duygu analizi yapılıyor (FinBERT)...")
    duygu_sonucu = metin_analiz_et(metin)

    if not duygu_sonucu:
        print("❌ Duygu analizi başarısız.")
        return None

    ana = duygu_sonucu["ana_duygu"]
    guven = duygu_sonucu["guven"]
    emoji_map = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}
    tr_map = {"positive": "POZİTİF", "negative": "NEGATİF", "neutral": "NÖTR"}
    print(f"      Sonuç: {emoji_map[ana]} {tr_map[ana]} — Güven: %{guven*100:.1f}")
    print("\n[3/3] 📊  Korelasyon ile etki hesaplanıyor...")
    etki_analizi = etki_hesapla(duygu_sonucu, tespit_edilen)
    print("      Tüm varlıklar için etki hesaplandı.")

    return {
        "duygu": duygu_sonucu,
        "tespit_edilen_varliklar": tespit_edilen,
        "tespit_edilen_olaylar": tespit_edilen_olaylar,
        "etki_analizi": etki_analizi
    }
def rapor_yazdir(metin: str, sonuc: dict):
    """Analiz sonucunu detaylı rapor olarak ekrana yazdırır."""

    if not sonuc:
        print("❌ Rapor oluşturulamadı.")
        return

    duygu = sonuc["duygu"]
    ana = duygu["ana_duygu"]
    emoji_map = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}
    tr_map = {"positive": "POZİTİF", "negative": "NEGATİF", "neutral": "NÖTR"}

    print("\n" + "╔" + "═"*63 + "╗")
    print("║" + "  📊 FİNANSAL ETKİ ANALİZ RAPORU".center(63) + "║")
    print("╚" + "═"*63 + "╝")

    print(f"\n📰 HABER: {metin.strip()[:150]}{'...' if len(metin.strip()) > 150 else ''}")

    print(f"\n🎯 GENEL DUYGU: {emoji_map[ana]} {tr_map[ana]}  (Güven: %{duygu['guven']*100:.1f})")

    skorlar = duygu["skorlar"]
    sirali = sorted(skorlar.items(), key=lambda x: x[1], reverse=True)
    for etiket, skor in sirali:
        bar = "█" * int(skor * 15)
        print(f"   {emoji_map[etiket]} {etiket:8s}: {bar:15s} %{skor*100:.1f}")

    if sonuc["tespit_edilen_varliklar"]:
        print(f"\n🏷️  HABERDEN ETKİLENEN ANA VARLIKLAR: {', '.join(sonuc['tespit_edilen_varliklar'])}")

    if sonuc["tespit_edilen_olaylar"]:
        print(f"📌 OLAY KATEGORİSİ: {', '.join(sonuc['tespit_edilen_olaylar'])}")

    print("\n" + "─"*65)
    print(f"{'VARLIK':<12} {'ETKİ SKORU':>12} {'DURUM':<20} {'AÇIKLAMA'}")
    print("─"*65)
    etki = sonuc["etki_analizi"]
    sirali_etki = sorted(etki.items(), key=lambda x: abs(x[1]["etki_skoru"]), reverse=True)

    for varlik, detay in sirali_etki:
        skor = detay["etki_skoru"]
        sinif_emoji = etki_siniflandir(skor)
        yon = "↑ Artış" if skor > 0.02 else ("↓ Düşüş" if skor < -0.02 else "→ Nötr")
        aciklama = f"Etki: {skor:+.3f}"
        print(f"{varlik:<12} {skor:>+12.4f} {sinif_emoji + ' ' + yon:<20} {aciklama}")
    print("─"*65)
    print("\n📖 DETAYLI ETKİ AÇIKLAMASI:")

    for varlik, detay in sirali_etki:
        skor = detay["etki_skoru"]
        if abs(skor) > ETKI_ESIKLERI["zayif"]:
            yon_tr = "artış" if skor > 0 else "düşüş"
            print(f"\n   {varlik}:")
            for katki in detay["katki_detaylari"]:
                print(f"      ← {katki['kaynak']} ile korelasyon {katki['korelasyon']:+.2f} "
                      f"→ katkı {katki['katki']:+.4f}")
            print(f"      → Toplam tahmini {yon_tr} baskısı: {abs(skor):.3f}")

    print("\n⚠️  NOT: Bu analiz istatistiksel korelasyona dayanır.")
    print("   Gerçek piyasa hareketleri farklılık gösterebilir.")
    print("═"*65)
if __name__ == "__main__":

    test_haberleri = [
        "Federal Reserve raises interest rates by 75 basis points. Gold and silver prices drop sharply. Bitcoin crashes below 40,000 dollars as investors flee risk assets.",

        "Rusya-Ukrayna savaşı şiddetleniyor, petrol fiyatları varil başına 110 dolara fırladı. Altın güvenli liman olarak rekor kırdı, borsa istanbul sert düştü.",

        "Tesla reports record quarterly earnings beating all analyst expectations. Stock surges 12 percent in after-hours trading."
    ]

    for i, haber in enumerate(test_haberleri, 1):
        print(f"\n\n{'█'*65}")
        print(f"  TEST {i}")
        print(f"{'█'*65}")
        sonuc = makale_analiz_et(haber)
        rapor_yazdir(haber, sonuc)

    print("\n\n✅ ANALİZ MOTORU HAZIR!")
    print("   Kullanım: from analiz_motoru import makale_analiz_et")
