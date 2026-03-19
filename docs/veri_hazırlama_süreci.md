Veri Hazırlama Süreci — PSR Raporu İçin Detaylı Açıklama

1. Veri Kaynakları ve Gerekçeleri
ClinVar
ClinVar, NCBI tarafından yönetilen ve dünya genelinde 2.800'den fazla kurumun katkıda bulunduğu kamuya açık bir genetik varyant veritabanıdır. Her varyant için klinik önemi (patojenik, benign vb.) ve bu değerlendirmenin güvenilirlik seviyesi yıldız sistemiyle gösterilmektedir.
Biz bu çalışmada yalnızca 3 ve 4 yıldız güvenilirlik seviyesindeki varyantları kullandık. Bu iki kategori şu şekilde tanımlanmaktadır:

3 yıldız (reviewed by expert panel): Alanında uzman bir kurul tarafından incelenmiş varyantlar.
4 yıldız (practice guideline): Klinik uygulama kılavuzlarına dahil edilmiş, en güvenilir varyantlar.

Bu filtrenin seçilme nedeni doğrudan şartnameden kaynaklanmaktadır. Şartname patojenik sınıf için ClinVar ve ClinGen veri tabanlarından "Expert Panel" ve güvenilir "Practice Guideline" inceleme statüsüne sahip, 3 ve 4 yıldız güvenilirlik seviyesindeki missense varyantların seçildiğini belirtmektedir. Dolayısıyla demo veri setimizi yarışma verisinin kaynağıyla birebir uyumlu tuttuk.
gnomAD
gnomAD (Genome Aggregation Database), 807.162 bireyden toplanan genomik veriyi içeren kamuya açık bir popülasyon veritabanıdır. Bu veri tabanındaki varyantlar hastalıksız bireylerden toplandığından, sağlıklı popülasyonda görülen varyantlar benign proxy olarak kabul edilmektedir.
Biz gnomAD'ı yalnızca PAH ve CFTR panellerinde benign sınıfını dengelemek için kullandık. Bu yaklaşım doğrudan şartnameden alınmıştır: "Sınıf dengesizliğini gidermek amacıyla ClinVar verilerine ek olarak gnomAD veri tabanından sık görülen sağlıklı popülasyon varyantları eklenecektir."

2. Varyant Filtreleme Kriterleri
Ham ClinVar verisine aşağıdaki filtreler sırayla uygulandı:
2.1 Genom Versiyonu
Yalnızca GRCh38 (hg38) assembly'sine ait varyantlar alındı. GRCh38, güncel referans genom versiyonu olup biyoinformatik araçların büyük çoğunluğu bu versiyonu desteklemektedir.
2.2 Varyant Tipi
Yalnızca tek nükleotid değişimleri (single nucleotide variant) alındı. İnsersiyon, delesyon veya yapısal varyantlar kapsam dışında tutuldu. Bunun nedeni şartnamedeki problemin yalnızca missense varyantları kapsamasıdır.
2.3 Missense Filtresi
Protein düzeyinde amino asit değişimine yol açan varyantları seçmek için HGVS protein notasyonu kullanıldı. p.Ala123Val gibi iki farklı amino asit içeren notasyon regex ile filtrelendi:
p\.[A-Z][a-z]{2}\d+[A-Z][a-z]{2}
Bu regex yalnızca bir amino asidin başka bir amino aside dönüştüğü missense varyantları yakalar. Stop kazanımı (p.Arg123*), frameshift veya synonymous varyantları bu filtreyle elenir. Bu adım kritik öneme sahiptir çünkü ilk denemelerimizde bu filtreyi uygulamadığımızda ClinVar'dan gelen varyantların önemli bir kısmının stop_gained veya synonymous olduğunu gördük.
2.4 Klinik Yorumun Kesinliği
Birden fazla laboratuvarın çelişkili yorum sunduğu (conflicting interpretations), klinik önemi belirsiz (uncertain significance) veya VUS (variant of uncertain significance) olarak sınıflandırılan varyantlar çıkarıldı. Bu varyantların modele dahil edilmesi, öğrenme sürecinde gürültü oluşturacak ve model performansını olumsuz etkileyecektir.
2.5 Sınıf Birleştirme
Şartname ile uyumlu olarak:

Patojenik sınıf: "Pathogenic", "Likely pathogenic", "Pathogenic/Likely pathogenic" etiketleri tek sınıf altında birleştirildi.
Benign sınıf: "Benign", "Likely benign", "Benign/Likely benign" etiketleri tek sınıf altında birleştirildi.


3. Panel Oluşturma
Şartname dört ayrı veri seti tanımlamaktadır. Her panel için gen listesi şu şekilde belirlendi:
Genel Veri Seti: Panel genlerinin dışında kalan tüm genlerden gelen varyantlar. Geniş bir gen yelpazesini kapsar, modelin genel genelleme yeteneğini test etmek için kullanılır.
Kalıtsal Kanser Paneli: BRCA1, BRCA2, ATM, PALB2, CHEK2, BRIP1, RAD51C, RAD51D, BARD1, MLH1, MSH2, MSH6, PMS2, TP53 ve PTEN genleri. Bu genler herediter meme-over kanseri ve Lynch sendromu gibi kalıtsal kanser sendromlarıyla ilişkilidir. ClinGen HBOC ve Lynch Sendromu Variant Curation Expert Panel'leri tarafından kurala bağlanmış genlerdir.
PAH Paneli: Yalnızca PAH geni. Fenilalanin hidroksilaz enzimini kodlayan bu gen, fenilketonüri hastalığından sorumludur.
CFTR Paneli: Yalnızca CFTR geni. Kistik fibrozis transmembran iletkenlik düzenleyicisini kodlar, kistik fibrozis hastalığından sorumludur.

4. Sınıf Dengesi Sorunu ve Çözümü
Filtreleme sonrası şu tablo ortaya çıktı:
PanelPatojenikBenign (ClinVar)DurumGenel3363879Benign azHerediter1764544Benign azPAH4051Benign çok azCFTR1810Benign yok
Benign varyant azlığının nedeni yapısal bir veritabanı sorunudur: ClinVar ağırlıklı olarak hastalık varyantlarının raporlandığı bir veritabanıdır. Sağlıklı bireylerdeki benign varyantlar klinik ortamda genellikle raporlanmaz.
Bu sorunu çözmek için şartnamenin de öngördüğü yaklaşım uygulandı: PAH ve CFTR panelleri için gnomAD'dan sağlıklı popülasyon varyantları eklendi. AF ≥ 0.00001 eşiği kullanıldı. Bu eşiğin seçilme nedeni daha düşük eşiklerin çok az varyant getirmesi, daha yüksek eşiklerin ise nadir patojenik varyantları da kapsama alabilme riskidir.

5. Feature Zenginleştirme
Ham ClinVar verisi yalnızca genomik konum ve klinik sınıf bilgisi içermektedir. Makine öğrenmesi modeli için sayısal özellikler gerekmektedir. Bu amaçla Ensembl VEP (Variant Effect Predictor) REST API kullanıldı.
Her varyant için şu özellikler elde edildi:
Fonksiyonel tahmin skorları:

SIFT skoru ve tahmini (0-1 arası, düşük = zararlı)
PolyPhen-2 skoru ve tahmini (0-1 arası, yüksek = zararlı)
CADD phred skoru (yüksek = zararlı)
REVEL skoru (missense varyantlara özel, 0-1 arası)
AlphaMissense skoru ve sınıfı (Google DeepMind'ın protein dil modeli)

Popülasyon frekansı:

gnomAD exome allel frekansı
gnomAD genome allel frekansı

Protein bağlamı:

Amino asit değişimi (örn. A/V = Alanin'den Valin'e)
Kodon değişimi
Varyantın fonksiyonel etkisi (consequence)

API kullanımında MANE Select transcript tercih edildi. MANE Select, her gen için klinik olarak en anlamlı ve referans alınan transkripti temsil etmektedir. Bu sayede aynı varyant için farklı transkriptlerden gelen çelişkili skorlar yerine tek ve tutarlı bir değer kullanıldı.

6. Çakışma Kontrolü
gnomAD'dan alınan benign varyantların ClinVar'da patojenik olarak kayıtlı olup olmadığı kontrol edildi. Çakışma tespit edilmesi durumunda gnomAD varyantı veri setinden çıkarılacaktı. Bu kontrol veri kalitesi açısından kritiktir: teorik olarak bir varyant gnomAD'da görülmüş olabilir ama klinik olarak patojenik kabul edilebilir (düşük penetranslı varyantlar bunun bir örneğidir).

7. Genomik Adres Gizleme
Şartname, yarışmacıların dış veri kaynaklarına başvurarak etiketi doğrudan bulmalarını engellemek amacıyla genomik adres bilgilerinin (kromozom ve pozisyon) gizleneceğini belirtmektedir. Demo veri setimizde de aynı prensibi uyguladık: final veri setine kromozom ve pozisyon bilgisi dahil edilmedi, yalnızca biyolojik özellikler ve skorlar bırakıldı.

8. Final Veri Seti Özeti
PanelPatojenikBenignToplamGenel109511342229Herediter Kanser200200400PAH136116252CFTR7070140Toplam150115203021
Feature doluluk oranları: SIFT %92.4, PolyPhen %92.0, gnomAD AF %82.1, amino asit değişimi %97.4.
Eksik değerler için model geliştirme aşamasında uygun imputation stratejileri uygulanacaktır.