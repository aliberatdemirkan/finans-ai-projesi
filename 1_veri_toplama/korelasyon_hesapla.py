import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

print("📂 Fiyat verisi yükleniyor...")
fiyatlar = pd.read_csv(
    r'C:\YazilimProjem\data\fiyat_verileri\kapanis_fiyatlari.csv',
    index_col='Date',
    parse_dates=True
)
print(f"✅ {len(fiyatlar)} günlük veri yüklendi.")

degisimler = fiyatlar.pct_change().dropna()
print(f"✅ Günlük değişimler hesaplandı.")
korelasyon = degisimler.corr()

print("\n🔗 Korelasyon Matrisi:")
print(korelasyon.round(2))
os.makedirs(r'C:\YazilimProjem\data\korelasyon', exist_ok=True)

korelasyon.to_csv(r'C:\YazilimProjem\data\korelasyon\korelasyon_matrisi.csv')
degisimler.to_csv(r'C:\YazilimProjem\data\korelasyon\gunluk_degisimler.csv')
print("✅ CSV dosyaları kaydedildi.")
print("\n📖 Altın ile diğer varlıklar arasındaki ilişki:")
for varlik in korelasyon.columns:
    if varlik == 'Altin':
        continue
    kor = korelasyon['Altin'][varlik]
    if kor > 0.5:
        yorum = "güçlü pozitif → Altın artınca bu da artar"
    elif kor > 0.2:
        yorum = "zayıf pozitif → Altın artınca hafif artar"
    elif kor < -0.5:
        yorum = "güçlü negatif → Altın artınca bu düşer"
    elif kor < -0.2:
        yorum = "zayıf negatif → Altın artınca hafif düşer"
    else:
        yorum = "ilişki yok"
    print(f"  Altın ↔ {varlik:10s}: {kor:+.2f}  ({yorum})")
print("\n🎨 Isı haritası oluşturuluyor...")

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(korelasyon.values, cmap='RdYlGn', vmin=-1, vmax=1)

ax.set_xticks(range(len(korelasyon.columns)))
ax.set_yticks(range(len(korelasyon.index)))
ax.set_xticklabels(korelasyon.columns, rotation=45, ha='right', fontsize=11)
ax.set_yticklabels(korelasyon.index, fontsize=11)

for i in range(len(korelasyon.index)):
    for j in range(len(korelasyon.columns)):
        deger = korelasyon.values[i, j]
        renk = 'white' if abs(deger) > 0.6 else 'black'
        ax.text(j, i, f'{deger:.2f}', ha='center', va='center',
                fontsize=10, color=renk, fontweight='bold')

plt.colorbar(im, ax=ax, label='Korelasyon Katsayısı')
ax.set_title('Varlıklar Arası Korelasyon Matrisi (2019-2024)',
             fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()

plt.savefig(r'C:\YazilimProjem\data\korelasyon\korelasyon_haritasi.png',
            dpi=150, bbox_inches='tight')
plt.show()

print("✅ Isı haritası kaydedildi: korelasyon_haritasi.png")
print("\n🎉 ADIM 3 TAMAMLANDI! Adım 4'e geçebilirsiniz.")
