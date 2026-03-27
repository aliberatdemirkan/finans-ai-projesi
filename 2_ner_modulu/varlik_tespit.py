import re

VARLIK_SOZLUGU = {
    "Altin": [
        "gold", "altın", "altin", "xau", "ons", "ounce"
    ],
    "Gumus": [
        "silver", "gümüş", "gumus", "xag"
    ],
    "Bitcoin": [
        "bitcoin", "btc", "kripto", "crypto", "cryptocurrency",
        "kripto para", "dijital para"
    ],
    "Petrol": [
        "oil", "petrol", "crude", "brent", "opec", "enerji", "energy",
        "barrel", "varil"
    ],
    "Dolar": [
        "dollar", "usd", "dolar", "fed", "federal reserve",
        "amerikan merkez", "usdtry"
    ],
    "THYAO": [
        "turkish airlines", "türk hava", "turk hava", "thyao", "thy",
        "havacılık", "havacilik", "airline"
    ],
    "BIST100": [
        "bist", "borsa istanbul", "türk borsası", "turk borsasi",
        "xu100", "istanbul stock"
    ],
    "Tesla": [
        "tesla", "tsla", "elon musk", "elektrikli araç", "elektrikli arac",
        "electric vehicle", "ev stock"
    ],
    "Faiz": [
        "interest rate", "faiz", "rate hike", "rate cut", "baz puan",
        "basis point", "merkez bankası", "merkez bankasi", "central bank",
        "tcmb", "fed rate", "monetary policy", "para politikası"
    ],
    "Enflasyon": [
        "inflation", "enflasyon", "cpi", "tüfe", "tufe", "fiyat artışı",
        "fiyat artisi", "purchasing power", "satın alma gücü"
    ],
    "Savas": [
        "war", "savaş", "savas", "conflict", "çatışma", "catisma",
        "military", "askeri", "ordu", "troops", "missile", "füze", "attack",
        "saldırı", "saldiri", "gerilim", "tension", "nato", "nükleer", "nukleer"
    ],
    "Ekonomik_Kriz": [
        "recession", "kriz", "crisis", "crash", "çöküş", "cokus",
        "bear market", "market crash", "depression", "durgunluk",
        "iflас", "iflas", "bankruptcy", "default"
    ]
}

OLAY_KATEGORILERI = {
    "merkez_bankasi_karari": [
        "fed", "federal reserve", "tcmb", "merkez bankası", "central bank",
        "rate decision", "faiz kararı", "monetary policy"
    ],
    "jeopolitik_gerilim": [
        "war", "savaş", "conflict", "sanctions", "yaptırım", "gerilim",
        "tension", "military", "nato", "invasion", "işgal"
    ],
    "ekonomik_veri": [
        "gdp", "gsyh", "inflation", "enflasyon", "unemployment", "işsizlik",
        "cpi", "pmi", "trade balance", "dış ticaret"
    ],
    "sirket_haberi": [
        "earnings", "kar", "revenue", "gelir", "quarterly", "çeyrek",
        "merger", "birleşme", "acquisition", "satın alma", "ipo"
    ],
    "kripto_ozel": [
        "bitcoin halving", "sec", "regulation", "düzenleme", "blockchain",
        "defi", "nft", "crypto ban", "kripto yasak"
    ]
}

def varlik_tespit_et(metin: str) -> dict:
    """
    Verilen metni okur ve içinde hangi finansal varlıkların
    geçtiğini tespit eder.

    Döndürdüğü şey:
    {
        "bulunan_varliklar": ["Altin", "Faiz", "Dolar"],
        "bulunan_olaylar": ["merkez_bankasi_karari"],
        "eslesme_detaylari": {"Altin": ["gold", "xau"], ...}
    }
    """

    metin_lower = metin.lower()

    bulunan_varliklar = []
    eslesme_detaylari = {}

    for varlik, kelimeler in VARLIK_SOZLUGU.items():
        eslesen_kelimeler = []
        for kelime in kelimeler:
            pattern = r'\b' + re.escape(kelime) + r'\b'
            if re.search(pattern, metin_lower):
                eslesen_kelimeler.append(kelime)

        if eslesen_kelimeler:
            bulunan_varliklar.append(varlik)
            eslesme_detaylari[varlik] = eslesen_kelimeler

    bulunan_olaylar = []
    for kategori, kelimeler in OLAY_KATEGORILERI.items():
        for kelime in kelimeler:
            pattern = r'\b' + re.escape(kelime) + r'\b'
            if re.search(pattern, metin_lower):
                bulunan_olaylar.append(kategori)
                break 
    return {
        "bulunan_varliklar": bulunan_varliklar,
        "bulunan_olaylar": list(set(bulunan_olaylar)),
        "eslesme_detaylari": eslesme_detaylari
    }


def sonuc_yazdir(metin: str, sonuc: dict):
    """Tespit sonuçlarını ekrana düzgün yazdırır."""

    print("\n" + "="*60)
    print("📰 ANALİZ EDİLEN METİN:")
    print(f"   {metin[:200]}{'...' if len(metin) > 200 else ''}")
    print("="*60)

    if sonuc["bulunan_varliklar"]:
        print(f"\n✅ Tespit Edilen Varlıklar ({len(sonuc['bulunan_varliklar'])} adet):")
        for varlik in sonuc["bulunan_varliklar"]:
            kelimeler = sonuc["eslesme_detaylari"][varlik]
            print(f"   📌 {varlik:15s} ← '{', '.join(kelimeler)}' kelimesinden bulundu")
    else:
        print("\n❌ Hiçbir finansal varlık tespit edilemedi.")

    if sonuc["bulunan_olaylar"]:
        print(f"\n🏷️  Olay Kategorisi:")
        for olay in sonuc["bulunan_olaylar"]:
            print(f"   🔖 {olay}")

    print("="*60)

if __name__ == "__main__":

    test_haberleri = [
        "Federal Reserve raises interest rates by 75 basis points, gold and silver drop sharply while Bitcoin crashes below 40k.",

        "Rusya-Ukrayna savaşı nedeniyle petrol fiyatları fırladı, altın rekor kırdı ve borsa istanbul sert düştü.",

        "OPEC cuts oil production, causing energy prices to surge. Meanwhile, Tesla reports record quarterly earnings.",

        "Türk Hava Yolları yolcu sayısında rekor kırdı, THYAO hisseleri BIST100'ü geride bıraktı.",

        "Enflasyon beklentilerin üzerinde geldi, TCMB faiz kararı için olağanüstü toplantı çağrısı yapıldı."
    ]

    print("🚀 NER MODÜLÜ TEST EDİLİYOR...\n")

    for i, haber in enumerate(test_haberleri, 1):
        print(f"\n{'─'*60}")
        print(f"TEST {i}:")
        sonuc = varlik_tespit_et(haber)
        sonuc_yazdir(haber, sonuc)

    print("\n\n✅ NER MODÜLÜ HAZIR! Bu dosyayı diğer modüller import edecek.")
    print("   Kullanım: from varlik_tespit import varlik_tespit_et")
