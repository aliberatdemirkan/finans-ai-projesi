import yfinance as yf
import pandas as pd
import os

os.makedirs(r'C:\YazilimProjem\data\fiyat_verileri', exist_ok=True)

varliklar = {
    "Altin": "GC=F",
    "Bitcoin": "BTC-USD",
    "Dolar_TL": "USDTRY=X",
    "THYAO": "THYAO.IS",
    "BIST100": "XU100.IS",
    "Tesla": "TSLA",
    "Petrol": "CL=F",
    "Gumus": "SI=F"
}

veri = {}

for isim, sembol in varliklar.items():
    try:
        df = yf.download(sembol, start="2019-01-01", end="2024-12-31", auto_adjust=True)
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        kapanis = df['Close'].squeeze()
        veri[isim] = kapanis
        print(f"✅ {isim} verisi çekildi: {len(df)} gün")
        
    except Exception as e:
        print(f"❌ {isim} verisi çekilemedi: {e}")

fiyatlar = pd.DataFrame(veri)

fiyatlar = fiyatlar.ffill()

fiyatlar = fiyatlar.dropna()

print(f"\n📊 Toplam veri: {len(fiyatlar)} gün, {len(fiyatlar.columns)} varlık")
print(f"📅 Tarih aralığı: {fiyatlar.index[0]} → {fiyatlar.index[-1]}")
print(f"\n🔍 İlk 3 satır:\n{fiyatlar.head(3)}")

fiyatlar.to_csv(r'C:\YazilimProjem\data\fiyat_verileri\kapanis_fiyatlari.csv')
print("\n✅ Veriler 'C:\\YazilimProjem\\data\\fiyat_verileri\\kapanis_fiyatlari.csv' dosyasına kaydedildi!")
