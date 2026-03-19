Makine Öğrenmesi Aşaması — Rehber

Başlamadan Önce Bilinmesi Gerekenler
Elimizde demo_final_dataset.csv dosyası var. Bu dosya şu kolonları içeriyor:
unique_id          → varyant kimliği
label              → 1 = Patojenik, 0 = Benign
panel              → genel / herediter_kanser / pah / cftr
sift_score         → 0-1 arası (düşük = zararlı)
polyphen_score     → 0-1 arası (yüksek = zararlı)
cadd_phred         → yüksek = zararlı
revel              → 0-1 arası missense skoru
gnomad_af          → popülasyon frekansı
gnomadg_af         → gnomAD genome frekansı
am_pathogenicity   → AlphaMissense skoru
am_class           → AlphaMissense sınıfı
amino_acids        → amino asit değişimi (A/V gibi)
codons             → kodon değişimi
consequence        → fonksiyonel etki
GeneSymbol         → gen adı
Hedef kolon label — bunu tahmin edecek model kurulacak.

Adım 1 — Veriyi Anla
İlk yapılacak şey veriyi keşfetmek. Claude'a şunu söyle:

"demo_final_dataset.csv dosyam var. Bunu yükleyip şunları yap: sınıf dağılımını göster, her feature için eksik değer oranını hesapla, sayısal kolonların dağılımını çiz, patojenik ve benign gruplar arasındaki feature farklarını boxplot ile göster."


Adım 2 — Ön İşleme
Claude'a şunu söyle:

"Şu adımları uygula: SIFT ve PolyPhen string olabilir, sayıya çevir. Eksik değerleri median ile doldur. amino_acids kolonundan ref ve alt amino asiti ayır. am_class gibi kategorik kolonları one-hot encode yap. Label kolonunu hedef değişken olarak ayır, geri kalanları feature olarak kullan. Train/test split yap, %80 train %20 test, stratify=label."


Adım 3 — Baseline Model
Claude'a şunu söyle:

"Önce basit bir baseline kur. Logistic Regression ve Random Forest dene. Her ikisi için F1 skoru, ROC-AUC, confusion matrix göster. Panel bazında da ayrı ayrı sonuçları raporla: genel, herediter_kanser, pah, cftr."

Şartname F1 skorunu temel metrik olarak kullanıyor, bunu Claude'a belirt.

Adım 4 — Asıl Model
Claude'a şunu söyle:

"XGBoost veya LightGBM ile model kur. Şunları yap: cross-validation ile hiperparametre optimizasyonu, erken durdurma (early stopping), sınıf dengesizliği için scale_pos_weight ayarı, her panel için ayrı F1 ve ROC-AUC hesapla."


Adım 5 — Açıklanabilirlik
Bu kısım PSR'de 5 puan değerinde ve jüri için önemli. Claude'a şunu söyle:

"SHAP analizi yap. Hangi feature'lar modelin kararını en çok etkiliyor göster. Global feature importance grafiği çiz. En az bir örnek üzerinde lokal açıklama yap: bu varyant neden patojenik tahmin edildi?"


Adım 6 — Kalibrasyon ve Eşik Seçimi
Claude'a şunu söyle:

"Modelin olasılık çıktılarını kalibre et. Precision-Recall eğrisini çiz. Klinik bağlamda yanlış negatif daha risklidir (hasta atlanıyor), bu yüzden yüksek recall öncelikli bir eşik seç ve bunu gerekçelendir."


PSR İçin Önemli Notlar
Raporlarken şunları mutlaka yaz:
Veri bölme: Test seti eğitimde hiç kullanılmadı, etiketler sadece değerlendirmede görüldü.
Metrik seçimi: Şartname F1 skorunu temel metrik olarak belirtiyor. Sınıf dengesizliği olduğunda accuracy yanıltıcı olabileceği için F1 daha güvenilir.
Panel bazlı raporlama: Sadece genel sonuç değil, her panel için ayrı sonuç ver. PAH ve CFTR küçük veri setleri olduğundan yüksek varyans beklenir, bunu raporla.
Eksik değer stratejisi: Median imputation kullandıysan neden kullandığını açıkla. SIFT ve PolyPhen'in %8'lik eksikliği veri bütünlüğünü bozmaz.
Kolon isimleri yoktu: Şartname kolon isimlerinin gizleneceğini söylüyor. Raporunda "özellik grupları" üzerinden konuş: evrimsel korunmuşluk skorları, popülasyon frekansları, in silico tahmin skorları, biyokimyasal değişim bilgisi gibi.

Claude'a Veriyi Nasıl Verecek
Dosyayı Claude'a yükleyip şöyle başlayabilir:

"TEKNOFEST Sağlıkta Yapay Zeka yarışması için veri hazırladım. Elimde demo_final_dataset.csv var, kolonlar şunlar: [kolonları listele]. Hedef değişken label (1=Patojenik, 0=Benign). Şartname F1 skorunu temel metrik olarak kullanıyor. Bana adım adım model geliştirmeme yardım et."

Bu şekilde başlarsa Claude bağlamı anlayarak doğru yönlendirme yapacaktır.