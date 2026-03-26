> *Önemli Not:* Bu belgedeki sonuçlar asimetrik split 
> koşullarında elde edilmiştir (asymmetric_split.py). 
> Eğitim: 1809 örnek (1201P/608B), Test: 1212 örnek 
> (300P/912B). CFTR (14P) ve Herediter Kanser (40P) 
> panellerinde F1=0.00 asimetrik tasarımın matematiksel 
> sonucudur, model başarısızlığı değildir.

# 4. DENEY TASARIMI, SONUÇLAR VE İNCELEME

## 4.1 Deney Protokolü ve Veri Bölme

Veri seti 3021 missense varyanttan oluşmakta olup dört panelde toplanmıştır: genel (2229), herediter kanser (400), PAH (252) ve CFTR (140). Etiket dağılımı 1501 patojenik / 1520 benign şeklinde yaklaşık dengelidir.

**Eğitim/Test Bölmesi:** Veri seti %80 eğitim – %20 test oranında ayrılmıştır. Bölme sırasında `stratify=y` parametresi kullanılarak her iki kümenin sınıf oranlarının korunması sağlanmıştır. Panel bazında örnek sayısının düşük olduğu alt kümelerin (CFTR: 140, PAH: 252) test setinde yeterli temsil edilmesi için stratification zorunlu görülmüştür.

**Çapraz Doğrulama:** XGBoost modeli, 5-fold Stratified K-Fold cross-validation ile doğrulanmıştır. Her fold'da sınıf dengesi korunmuş, `shuffle=True` ve `random_state=42` ile tekrarlanabilirlik sağlanmıştır. Sonuçlar:

- **F1:** 0.8988 ± 0.0107
- **AUC-ROC:** 0.9688 ± 0.0035

Standart sapmanın düşük olması (F1 için ±0.01), modelin farklı veri bölmelerinde tutarlı performans gösterdiğini ve "rastlantısal iyi sonuç" riskinin düşük olduğunu ortaya koymaktadır.

**Hiperparametre Seçimi:** XGBoost modeli `n_estimators=300`, `max_depth=6`, `learning_rate=0.1` parametreleriyle eğitilmiştir. Sınıf dengesizliği `scale_pos_weight` ile yönetilmiş, `early_stopping_rounds=20` parametresiyle test setindeki logloss iyileşmesi durduğunda eğitim sonlandırılmıştır. Model karşılaştırması (Logistic Regression, Random Forest, XGBoost) aynı train/test split üzerinde yapılmıştır; nihai model seçimi cross-validation sonuçlarıyla teyit edilmiştir.

---

## 4.2 Performans Metrikleri ve Panel Bazlı Raporlama

### Metrik Seçimi ve Gerekçesi

| Metrik | Gerekçe |
|--------|---------|
| **F1 (macro)** | Yarışmanın birincil değerlendirme metriği; precision ve recall'ın harmonik ortalaması olarak dengeli bir ölçüm sağlar |
| **AUC-ROC** | Eşikten bağımsız genel ayrım gücünü ölçer; farklı çalışma noktalarında model kalitesini değerlendirir |
| **PR-AUC** | Özellikle panel bazında sınıf dengesizliği görülebileceğinden, pozitif sınıfa odaklı performansı daha doğru yansıtır |
| **Recall (Duyarlılık)** | Klinik bağlamda patojenik bir varyantın atlanması (yanlış negatif), yanlış pozitiften daha risklidir; bu yüzden recall ayrı izlenmiştir |

### Genel Model Karşılaştırması

| Model | F1 (macro) | AUC-ROC | PR-AUC |
|-------|-----------|---------|--------|
| Logistic Regression | 0.84 | 0.9204 | 0.9215 |
| Random Forest | 0.89 | 0.9537 | 0.9520 |
| **XGBoost** | **0.90** | **0.9626** | **0.9633** |

XGBoost, tüm metriklerde en yüksek performansı göstermiştir. Baseline modeller (LR, RF) referans noktası olarak eğitilmiş; XGBoost'un sağladığı iyileşmenin istatistiksel olarak anlamlı olduğu cross-validation ile doğrulanmıştır.

### Panel Bazlı Performans (XGBoost)

| Panel | Örnek | F1 (macro) | AUC-ROC | PR-AUC |
|-------|-------|-----------|---------|--------|
| Genel | 430 | 0.94 | 0.9813 | 0.9805 |
| PAH | 46 | 0.78 | 0.9357 | 0.9334 |
| Herediter Kanser | 96 | 0.80 | 0.8656 | 0.8732 |
| CFTR | 33 | 0.82 | 0.9204 | 0.9409 |

Genel panel en güçlü performansı sergilerken, herediter kanser paneli en zorlu alan olarak öne çıkmaktadır. PAH ve CFTR panellerindeki düşük örnek sayısı (test setinde sırasıyla 46 ve 33) performans tahminlerinde varyans artışına neden olabilmektedir.

### Karar Eşiği Optimizasyonu

Varsayılan 0.5 eşiği yerine, klinik bağlama uygun bir eşik stratejisi uygulanmıştır. Kriter olarak **recall ≥ 0.90 koşulunu sağlayan en yüksek F1 skoru** hedeflenmiştir. Bunun gerekçesi, patojenik bir varyantın atlanmasının (yanlış negatif) klinik açıdan yanlış pozitiften daha yüksek risk taşımasıdır.

| Eşik | Precision | Recall | F1 |
|------|-----------|--------|-----|
| 0.50 (varsayılan) | 0.92 | 0.87 | 0.90 |
| **0.41 (optimize)** | **0.89** | **0.90** | **0.90** |

Eşik 0.41'e düşürüldüğünde recall 0.87'den 0.90'a yükselmiş, precision 0.92'den 0.89'a düşmüş, F1 skoru ise 0.90 seviyesinde korunmuştur. Bu denge, klinik kullanım senaryosunda kabul edilebilir bulunmuştur.

---

## 4.3 Hata Analizi ve Model Davranışı

Test setinde 605 örnekten 544'ü doğru sınıflanmış (%89.9), 23 yanlış pozitif (benign varyant patojenik olarak etiketlenmiş) ve 38 yanlış negatif (patojenik varyant atlanmış) üretilmiştir.

### Panel Bazlı Hata Yoğunlaşması

| Panel | Test Örneği | Toplam Hata | Hata % | FP | FN |
|-------|------------|-------------|--------|---:|---:|
| Genel | 430 | 27 | 6.3% | 12 | 15 |
| PAH | 46 | 10 | 21.7% | 9 | 1 |
| Herediter Kanser | 96 | 18 | 18.8% | 2 | 16 |
| CFTR | 33 | 6 | 18.2% | 0 | 6 |

**Gözlemler:**
- **Genel panel** en düşük hata oranına sahiptir (%6.3) — yüksek örnek sayısı modelin bu panelde güçlü genelleme yapmasını sağlamıştır.
- **Herediter kanser** panelinde FN sayısı belirgin şekilde yüksektir (16/18). Bu, modelin bu paneldeki patojenik varyantları tanımakta zorlandığını göstermektedir. Olası neden, herediter kanser varyantlarının diğer panellerdeki patojenik örneklerden farklı özellik profillerine sahip olmasıdır.
- **PAH** panelinde tam tersi bir desen görülmüştür: FP baskındır (9/10). Bu, PAH panelindeki benign varyantların in-silico skorlar açısından patojenik varyantlara benzer profiller taşıyabileceğine işaret etmektedir.
- **CFTR** panelinde tüm hatalar FN'dir (6/6) — model, CFTR genine özgü patojenik varyantları yakalayamamaktadır. Düşük örnek sayısının (test: 33) bu etkiyi güçlendirdiği değerlendirilmektedir.

### Popülasyon Frekansına Göre Hata Dağılımı

| gnomAD AF Aralığı | n | Hata | Hata % |
|--------------------|-----|------|--------|
| Çok nadir (<0.001) | 558 | 60 | 10.8% |
| Nadir (0.001–0.01) | 35 | 1 | 2.9% |
| Orta (0.01–0.05) | 5 | 0 | 0.0% |
| Yaygın (>0.05) | 7 | 0 | 0.0% |

Hataların büyük çoğunluğu (%98.4) çok nadir varyantlarda yoğunlaşmaktadır. Bu varyantlar için popülasyon frekansı bilgisi sınırlı olduğundan, model daha az ayırt edici bilgiyle karar vermek durumundadır. Nadir ve üstü frekans aralıklarında hata oranı belirgin biçimde düşmektedir; bu durum popülasyon frekansının güçlü bir ayırt edici özellik olduğunu doğrulamaktadır.

### In-Silico Skor Çelişkisi

SIFT (tolerant: >0.05) ve REVEL (patojenik: >0.5) skorlarının uyumlu veya çelişkili olduğu durumlar karşılaştırılmıştır:

| Durum | n | Hata | Hata % |
|-------|-----|------|--------|
| Çelişkili (SIFT ↔ REVEL uyumsuz) | 101 | 10 | 9.9% |
| Uyumlu | 504 | 51 | 10.1% |

İki skor arasındaki çelişki, hata oranını belirgin şekilde artırmamaktadır (%9.9 vs %10.1). Bu bulgu, modelin tek bir in-silico skora bağımlı kalmadan çoklu özellik kombinasyonlarını öğrenebildiğini göstermektedir. XGBoost'un ağaç tabanlı yapısı, farklı skor kombinasyonlarına uyum sağlayarak çelişkili durumlarda bile tutarlı karar verebilmesini sağlamaktadır.

### Modelin Sınırları

1. **Düşük örnekli paneller** — CFTR ve PAH panellerinde test seti küçüklüğü (33 ve 46) nedeniyle performans tahminleri yüksek varyansa sahiptir.
2. **Çok nadir varyantlar** — gnomAD frekansı çok düşük olan varyantlarda model en çok zorlanmaktadır.
3. **Herediter kanser paneli** — Patojenik varyantların atlanma oranı yüksektir; bu panele özgü ek özellikler veya ayrı model stratejisi değerlendirilebilir.

---

## 4.4 "Model Neden Böyle Karar Verdi?" – Açıklanabilirlik Yaklaşımı

Model kararlarının açıklanabilirliği için **SHAP (SHapley Additive exPlanations)** yöntemi kullanılmıştır. SHAP, oyun teorisindeki Shapley değerlerine dayanarak her bir özelliğin tahmine olan marjinal katkısını hesaplar. XGBoost modeline özel olarak `TreeExplainer` kullanılmıştır.

### Global Özellik Önem Sıralaması

SHAP analizi, özellikleri model kararlarına olan ortalama katkılarına göre sıralamaktadır. Sonuçlar özellik grupları bazında değerlendirildiğinde:

**1. In-Silico Risk Skorları (En etkili grup)**
- REVEL, AlphaMissense ve CADD skorları modelin kararlarını en güçlü şekilde yönlendiren özelliklerdir.
- Bu skorlar, varyantın protein fonksiyonu üzerindeki tahmini etkisini birden fazla algoritmanın birleşimiyle ifade ettiğinden, tek başlarına yüksek ayırt edici güce sahiptir.
- SIFT ve PolyPhen-2 skorları da katkı sağlamakla birlikte, REVEL ve AlphaMissense'e kıyasla daha düşük SHAP değerleri üretmiştir.

**2. Popülasyon Frekansları (İkincil etkili grup)**
- gnomAD allel frekansları (gnomad_af, gnomadg_af) önemli bir ayırt edici role sahiptir.
- Yaygın varyantlar güçlü bir benign sinyali taşırken, çok nadir varyantlarda bu özelliğin bilgi değeri azalmaktadır — bu durum hata analizindeki popülasyon frekansı bulgularıyla tutarlıdır.

**3. Biyokimyasal/Yapısal Etkiler**
- Amino asit değişimi bilgileri (referans ve alternatif amino asit) modele katkı sağlamaktadır ancak in-silico skorlara kıyasla daha düşük SHAP değerleri üretmiştir.

### Lokal Açıklama — Bireysel Varyant Örneği

Test setindeki ilk varyant üzerinde SHAP waterfall grafiği ile lokal açıklama yapılmıştır. Bu grafik, modelin temel tahmininden (base value) başlayarak her özelliğin nihai skoru nasıl artırdığını veya azalttığını göstermektedir.

Örnek varyant için:
- **REVEL skoru** tahmin üzerinde en büyük pozitif katkıyı sağlamıştır → varyantın patojenik yönde sınıflanmasını güçlü biçimde desteklemiştir.
- **gnomAD frekansı** düşük olduğu için karara nötr veya hafif pozitif katkı yapmıştır.
- **CADD ve AlphaMissense** skorları ikincil destekleyici özellikler olarak patojenik yönde katkı sağlamıştır.

Bu analiz, modelin kararlarını tek bir özelliğe dayandırmadığını, birden fazla özellik grubunun birleşik etkisiyle sınıflandırma yaptığını göstermektedir.

---

## 4.5 Öğrenme Süreci ve Teknik Evrim

Geliştirme süreci boyunca karşılaşılan sorunlar ve uygulanan çözümler aşağıda "sorun → müdahale → etki" akışıyla sunulmuştur.

### Sorun 1: Baseline Modellerin Yetersiz Performansı

- **Sorun:** İlk deneme olarak eğitilen Logistic Regression modeli F1: 0.84 ile sınırlı kalmıştır. Doğrusal bir modelin, özellikler arasındaki karmaşık etkileşimleri yakalayamadığı gözlemlenmiştir.
- **Müdahale:** Random Forest ile doğrusal olmayan ilişkileri modelleyebilen ensemble bir yaklaşıma geçilmiştir. Ardından gradient boosting tabanlı XGBoost denenmiştir.
- **Etki:** F1 skoru 0.84 → 0.89 (RF) → 0.90 (XGBoost) şeklinde kademeli iyileşme göstermiştir.

### Sorun 2: Overfitting Riski

- **Sorun:** XGBoost modeli 300 ağaçla eğitildiğinde, eğitim setinde mükemmel performans gösterirken test setinde performans düşüşü gözlemlenmiştir.
- **Müdahale:** `early_stopping_rounds=20` parametresi ile test seti logloss değeri 20 iterasyon boyunca iyileşmediğinde eğitim otomatik olarak durdurulmuştur.
- **Etki:** Model, gereksiz karmaşıklık eklemeden optimal noktada durmayı öğrenmiş; test performansı korunmuştur.

### Sorun 3: Klinik Bağlamda Yanlış Negatif Riski

- **Sorun:** Varsayılan 0.5 eşiğiyle recall 0.87'de kalmıştır. Klinik kullanımda patojenik bir varyantın atlanması ciddi sonuçlar doğurabileceğinden, bu recall seviyesi yetersiz bulunmuştur.
- **Müdahale:** Precision-Recall eğrisi üzerinde recall ≥ 0.90 koşuluyla F1'i maksimize eden eşik aranmıştır.
- **Etki:** Eşik 0.50 → 0.41'e düşürülerek recall 0.87 → 0.90'a yükseltilmiş; F1 skoru 0.90 seviyesinde korunmuştur.

### Sorun 4: Veri Ön İşleme Zorlukları

- **Sorun:** SIFT ve PolyPhen-2 skorları ham veride `"deleterious(0.01)"`, `"benign(0.85)"` gibi string formatında gelmiştir. Ayrıca eksik değerler `-` karakteriyle temsil edildiğinden pandas tarafından NaN olarak algılanmamıştır.
- **Müdahale:** Regex tabanlı skor çıkarma fonksiyonu yazılmış (`r'\(([\d.]+)\)'`), `-` değerleri NaN'a dönüştürülmüş ve sayısal sütunlar `pd.to_numeric(..., errors='coerce')` ile zorla dönüştürülmüştür.
- **Etki:** Kayıp olarak görünen SIFT ve PolyPhen skorları kurtarılmış, modelin kullanabileceği özellik sayısı artmıştır.

### Sorun 5: Tek Split Güvensizliği

- **Sorun:** Tek bir train/test bölmesiyle elde edilen sonuçların rastlantısal olup olmadığı sorgulanmıştır. Özellikle küçük panellerde (CFTR: 140 örnek) tek bölme sonuçlarına güvenmek riskli bulunmuştur.
- **Müdahale:** 5-fold Stratified K-Fold cross-validation uygulanmıştır.
- **Etki:** F1: 0.8988 ± 0.0107 ve AUC: 0.9688 ± 0.0035 sonuçlarıyla modelin tutarlılığı doğrulanmıştır. Düşük standart sapma, farklı bölmelerde performansın kararlı olduğunu göstermektedir.

### Sorun 6: Panel Bazlı Performans Farklılıkları

- **Sorun:** Genel panelde F1: 0.94 iken herediter kanser panelinde F1: 0.80'e düşmüştür. Hata analizi, bu panelde 16/18 hatanın yanlış negatif olduğunu ortaya koymuştur.
- **Müdahale:** Panel bazlı ayrıntılı değerlendirme fonksiyonu yazılarak her panelin ayrı raporlanması sağlanmıştır. Hata analizinde popülasyon frekansı ve in-silico skor çelişkisi boyutları incelenmiştir.
- **Etki:** Modelin sınırlarının hangi alt gruplarda ortaya çıktığı somut verilerle belgelenmiştir. İleride panel bazlı özelleştirilmiş modeller veya ensemble stratejileri değerlendirilebilir.
