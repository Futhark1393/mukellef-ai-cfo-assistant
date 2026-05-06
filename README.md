# Mükellef - AI CFO Assistant

Mükellef AI CFO Assistant, küçük ve orta ölçekli işletmelerin (KOBİ) tüm finansal operasyonlarını yapay zeka destekli otonom bir asistan ile yönetmelerini sağlayan modern bir finansal teknolojiler (FinTech) projesidir.

Bu proje, "SolveX AI Hackathon 2026" kapsamında **"Mock-First"** (simüle edilmiş veri tabanlı MVP) yaklaşımıyla geliştirilmiştir.

## 🚀 Özellikler

Mükellef AI CFO Assistant, aşağıdaki 12 ana modülü içerisinde barındıran tam teşekküllü bir **SPA (Single Page Application)** paneline sahiptir:

1. 📊 **Dashboard (Genel Bakış):** Nakit akışı, banka durumu ve şirket özetinin anlık takibi.
2. 👥 **Cari Hesap Yönetimi:** Müşterilerin veresiye (cari) işlemlerinin ve alacakların takibi.
3. 📄 **Fatura İşleme & OCR:** Yüklenen faturaların (PDF/Görsel) taranıp otomatik satır kalemlerine (line-item) ayrılması ve stok gruplarına atanması.
4. 💰 **Tedarikçi Ödemeleri (Tediyeler):** Tedarikçi borçları ve ödeme planlamalarının yönetimi.
5. 📦 **Stok & Envanter:** Giren/çıkan stok hareketlerinin izlenmesi ve **FIFO/LIFO** yöntemleriyle envanter değerlemesi.
6. 🏦 **Banka & Finans:** Vadesiz/vadeli banka hesap hareketlerinin günlük olarak sınıflandırılması.
7. 📈 **Nakit Akış Analizi:** Şirketin gelecek 6 aylık baz/iyi/kötü senaryolara göre nakit akış (cashflow) tahminlemesi.
8. 🧾 **Çek & Senet Takibi:** Alınan ve verilen çek/senetlerin, takas ve portföy durumlarının kontrolü.
9. 💵 **Gider Yönetimi (Dönemsellik İlkesi):** Peşin ödenen giderlerin ait oldukları aylara otomatik dağıtılması.
10. 📋 **Vergi & Bordro:** Hesaplanan/İndirilecek KDV, Muhtasar ve Personel Maaş/SGK maliyetlerinin otomatik hesaplanması.
11. 👨‍💼 **Personel Takibi:** Çalışanların günlük check-in/check-out mesai verilerinin analizi.
12. 🚗 **Araç & Sigorta Giderleri:** Şirket araçlarının poliçe süreleri ve bakım/yakıt masraflarının takibi.
13. 💹 **Karlılık Analizi:** Üretim ve ticari ürünlerin maliyet (COGS), Brüt Kar/Net Kar ve Rantabilite (ROE) performanslarının ayrıştırılması.

## 🛠️ Teknolojiler

- **Backend:** Python 3, FastAPI, SQLAlchemy
- **Frontend:** HTML5, Vanilla CSS (Glassmorphism Dark Theme, CSS-only Charts), Vanilla JS
- **Veritabanı:** SQLite (Mock data altyapısı ile bağımsız çalışabilir)
- **Mimari:** Multi-tenant tasarıma uygun, modüler RESTful servis mimarisi.

## 💻 Kurulum ve Çalıştırma

Projenin yerel bilgisayarınızda (local) çalıştırılması için aşağıdaki adımları izleyin:

### 1. Gereksinimleri Yükleyin
Proje dizininde sanal bir ortam (virtual environment) oluşturup bağımlılıkları yükleyin:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Uygulamayı Başlatın
Uvicorn kullanarak FastAPI sunucusunu ayağa kaldırın:
```bash
./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Tarayıcıda Açın
Tarayıcınızdan şu adrese giderek asistan panelini görüntüleyebilirsiniz:
[http://localhost:8000](http://localhost:8000)

## 📁 Proje Yapısı

```
.
├── core/
│   ├── bank_tracker.py       # Banka hareketleri ve finans modülü
│   ├── burn_rate.py          # Runway hesaplama modülü
│   ├── cari.py               # Cari hesap modülü
│   ├── cashflow.py           # Nakit akış projeksiyonu modülü
│   ├── check_manager.py      # Çek ve senet takibi modülü
│   ├── db.py                 # Veritabanı bağlantı yönetimi
│   ├── employee_tracker.py   # Mesai takibi modülü
│   ├── expense_manager.py    # Gider dönemselleştirme modülü
│   ├── models.py             # SQLAlchemy DB Modelleri
│   ├── ocr_engine.py         # Mock OCR ve fatura okuma motoru
│   ├── profitability.py      # Maliyet/Kar analiz modülü
│   ├── stock_grouping.py     # Otomatik stok gruplama mantığı
│   ├── stock_manager.py      # Stok hareket ve FIFO/LIFO değerleme
│   ├── supplier_payments.py  # Tedarikçi ödemeleri modülü
│   ├── tax_payroll.py        # Vergi (KDV/Muhtasar) ve Bordro modülü
│   └── vehicle_insurance.py  # Araç gider takibi modülü
├── static/
│   ├── app.js                # Frontend SPA state yönetimi ve API entegrasyonu
│   ├── index.html            # Ana dashboard arayüzü
│   └── style.css             # Glassmorphism tema
├── main.py                   # FastAPI Controller'ı (Tüm REST uç noktaları)
└── README.md
```

## 🤖 AI Traceability (Yapay Zeka İzlenebilirliği)
Hackathon gereksinimleri doğrultusunda, karmaşık algoritmalar ve muhasebe standartlarına yönelik (örn. dönemsellik ilkesi, KDV hesaplaması, FIFO değerleme) kurulan mantık bloklarının tamamı `# AI Traceability:` etiketleriyle kod içinde İngilizce olarak açıklanmıştır.

## 🤝 Katkıda Bulunma
Geliştirme sürecine dahil olmak için lütfen yeni bir branch oluşturup (örn: `feature/new-module`) Pull Request (PR) açın.
