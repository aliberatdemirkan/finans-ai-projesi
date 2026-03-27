# Yapay Zeka Tabanlı Finansal Duygu Analizi

**Öğrenci:** Ali Berat Demirkan  
**No:** 23100011018  
**Ders:** Uygulama Tasarımı 1

## Proje Hakkında
Finansal haberleri analiz ederek hangi yatırım araçlarının 
nasıl etkileneceğini tahmin eden yapay zeka sistemi.

## Kurulum
pip install transformers torch pandas yfinance deep-translator langdetect matplotlib

## Klasör Yapısı
- 1_veri_toplama   → Fiyat verisi çekme ve korelasyon hesabı
- 2_ner_modulu     → Metinden varlık tespiti  
- 3_finbert_modulu → Duygu analizi (FinBERT)
- 4_analiz_modulu  → Tüm modülleri birleştiren motor

## Kullanılan Teknolojiler
- ProsusAI/FinBERT
- yfinance
- deep-translator
- langdetect
- matplotlib
