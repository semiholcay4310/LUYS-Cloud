LÜYS CLOUD v0.1

Bu paket buluta deploy edilmek üzere hazırlanmıştır.
- Telefon / iş yeri PC / ev PC farklı internetlerden aynı URL ile erişebilir.
- Kullanıcı girişi vardır.
- Veriler PostgreSQL DATABASE_URL verilirse bulut veritabanında saklanır.
- DATABASE_URL yoksa yerel SQLite ile test edilebilir.

Gerekli ortam değişkenleri:
LUYS_USER
LUYS_PASSWORD
SECRET_KEY
DATABASE_URL (bulutta PostgreSQL önerilir)

Yerel test:
python -m pip install -r requirements.txt
set LUYS_USER=admin
set LUYS_PASSWORD=guclu-parola
python app.py
Tarayıcı: http://127.0.0.1:8080

Buluta alırken Render/Railway/Fly.io benzeri bir servis kullanılabilir. Kalıcı URL için hosting hesabı gerekir.
