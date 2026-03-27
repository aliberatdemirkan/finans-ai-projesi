from transformers import AutoTokenizer, AutoModelForSequenceClassification
from deep_translator import GoogleTranslator
import torch
import torch.nn.functional as F
import sys
import langdetect

print("🧠 FinBERT modeli yükleniyor...")

MODEL_ADI = "ProsusAI/finbert"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ADI)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ADI)
    model.eval()  
    print("✅ FinBERT hazır!\n")

except Exception as e:
    print(f"❌ Model yüklenemedi: {e}")
    sys.exit(1)
ETIKET_SIRASI = {0: "positive", 1: "negative", 2: "neutral"}
ETIKET_TR = {
    "positive": "POZİTİF",
    "negative": "NEGATİF",
    "neutral":  "NÖTR"
}

ETIKET_EMOJI = {
    "positive": "🟢",
    "negative": "🔴",
    "neutral":  "⚪"
}

def dil_tespit_et(metin: str) -> str:
    try:
        return langdetect.detect(metin)
    except:
        return "en"


def ingilizceye_cevir(metin: str) -> str:
    try:
        if len(metin) > 4500:
            parcalar = [metin[i:i+4500] for i in range(0, len(metin), 4500)]
            return " ".join([GoogleTranslator(source='tr', target='en').translate(p) for p in parcalar])
        return GoogleTranslator(source='tr', target='en').translate(metin)
    except Exception as e:
        print(f"⚠️ Çeviri başarısız, orijinal kullanılıyor: {e}")
        return metin
def metni_parcala(metin: str, max_karakter: int = 400) -> list:
    parcalar = []
    satirlar = metin.split('\n')
    mevcut_parca = ""

    for satir in satirlar:
        if len(mevcut_parca) + len(satir) > max_karakter and mevcut_parca:
            parcalar.append(mevcut_parca.strip())
            mevcut_parca = satir
        else:
            mevcut_parca += " " + satir

    if mevcut_parca.strip():
        parcalar.append(mevcut_parca.strip())

    sonuc = []
    for parca in parcalar:
        if len(parca) > max_karakter:
            cumleler = parca.split('. ')
            gecici = ""
            for cumle in cumleler:
                if len(gecici) + len(cumle) > max_karakter and gecici:
                    sonuc.append(gecici.strip())
                    gecici = cumle
                else:
                    gecici += ". " + cumle
            if gecici.strip():
                sonuc.append(gecici.strip())
        else:
            sonuc.append(parca)

    return [p for p in sonuc if len(p) > 10]
def parca_analiz_et(metin: str) -> dict:
    """
    Tek parçayı doğrudan model ile analiz eder.
    Softmax uygulayarak 3 sınıf için gerçek olasılık dağılımı üretir.
    Toplamı her zaman 1.0 (yani %100) olur.
    """
    inputs = tokenizer(
        metin[:512],
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model(**inputs)
    olasiliklar = F.softmax(outputs.logits, dim=1)[0]
    skorlar = {}
    for idx, etiket in ETIKET_SIRASI.items():
        skorlar[etiket] = round(olasiliklar[idx].item(), 4)

    return skorlar

def metin_analiz_et(metin: str) -> dict:
    """
    Makale/haber analiz eder. Şunları yapar:
    1. Dili tespit eder, Türkçe ise çevirir
    2. Uzun metni parçalara böler
    3. Her parçayı analiz eder
    4. Parça uzunluğuna göre ağırlıklı ortalama alır
    """
    dil = dil_tespit_et(metin)
    cevrildi = False
    analiz_metni = metin

    if dil == 'tr':
        print("   🌐 Türkçe tespit edildi, çevriliyor...")
        analiz_metni = ingilizceye_cevir(metin)
        cevrildi = True
        print("   ✅ Çeviri tamamlandı.")
    parcalar = metni_parcala(analiz_metni)
    if not parcalar:
        return None
    toplam_agirlik = 0
    agirlikli_skorlar = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

    for parca in parcalar:
        try:
            parca_skorlari = parca_analiz_et(parca)
            agirlik = len(parca)

            for etiket, skor in parca_skorlari.items():
                agirlikli_skorlar[etiket] += skor * agirlik

            toplam_agirlik += agirlik

        except Exception as e:
            print(f"   ⚠️ Parça atlandı: {e}")
            continue

    if toplam_agirlik == 0:
        return None
    ortalama_skorlar = {
        etiket: round(skor / toplam_agirlik, 4)
        for etiket, skor in agirlikli_skorlar.items()
    }

    ana_duygu = max(ortalama_skorlar, key=ortalama_skorlar.get)

    return {
        "ana_duygu":    ana_duygu,
        "skorlar":      ortalama_skorlar,
        "guven":        ortalama_skorlar[ana_duygu],
        "parca_sayisi": len(parcalar),
        "orijinal_dil": dil,
        "cevrildi":     cevrildi
    }
def sonuc_yazdir(metin: str, sonuc: dict):
    if not sonuc:
        print("❌ Analiz yapılamadı.")
        return

    ana = sonuc["ana_duygu"]

    print("\n" + "="*60)
    print(f"📰 METİN: {metin.strip()[:120]}{'...' if len(metin.strip()) > 120 else ''}")
    print("─"*60)

    if sonuc["cevrildi"]:
        print("🌐 Türkçe → İngilizceye çevrildi")

    print(f"🎯 SONUÇ: {ETIKET_EMOJI[ana]} {ETIKET_TR[ana]}  (Güven: %{sonuc['guven']*100:.1f})")
    print("📊 Detaylı Skorlar:")

    sirali = sorted(sonuc["skorlar"].items(), key=lambda x: x[1], reverse=True)
    for etiket, skor in sirali:
        bar = "█" * int(skor * 20)
        print(f"   {ETIKET_EMOJI[etiket]} {ETIKET_TR[etiket]:8s}: {bar:20s} %{skor*100:.1f}")

    toplam = sum(sonuc["skorlar"].values()) * 100
    print(f"   {'─'*45}")
    print(f"   Toplam: %{toplam:.1f}")

    if sonuc["parca_sayisi"] > 1:
        print(f"📄 {sonuc['parca_sayisi']} parçaya bölündü, ağırlıklı ortalama alındı.")

    print("="*60)

if __name__ == "__main__":

    print(f"📋 Model etiket sırası: {model.config.id2label}\n")

    test_haberleri = [
        "Federal Reserve raises interest rates by 75 basis points, gold and silver drop sharply while Bitcoin crashes below 40k.",
        "Apple reports record quarterly earnings, beating analyst expectations. Stock surges 8% in after-hours trading.",
        "The Federal Reserve will meet next week to discuss monetary policy.",
        "Rusya-Ukrayna savaşı nedeniyle petrol fiyatları fırladı, enflasyon beklentilerin çok üzerinde geldi.",
        """The global economy faces significant headwinds as central banks worldwide continue 
        their aggressive rate hiking cycles. The Federal Reserve raised rates by 75 basis points. 
        Gold prices fell sharply as the dollar strengthened. Bitcoin dropped below 20,000 dollars.
        Analysts warn that a recession is increasingly likely as consumer spending weakens."""
    ]

    print("🚀 FİNBERT MODÜLÜ TEST EDİLİYOR...\n")

    for i, haber in enumerate(test_haberleri, 1):
        print(f"\n{'─'*60}")
        print(f"TEST {i}:")
        sonuc = metin_analiz_et(haber)
        sonuc_yazdir(haber, sonuc)

    print("\n✅ FİNBERT MODÜLÜ HAZIR!")
    print("   Kullanım: from duygu_analiz import metin_analiz_et")
