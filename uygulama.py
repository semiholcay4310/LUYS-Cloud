import os, json
from datetime import timedelta
from flask import Flask, request, jsonify, send_from_directory, redirect, session, render_template_string
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret')
app.permanent_session_lifetime = timedelta(days=30)

# Admin: verileri görür ve düzenler.
ADMIN_USER = os.environ.get('LUYS_USER', 'admin')
ADMIN_PASSWORD = os.environ.get('LUYS_PASSWORD', 'luys-change-me')

# Viewer: sistemi yalnızca görüntüler, veri ekleyemez/değiştiremez.
VIEWER_USER = os.environ.get('LUYS_VIEWER_USER', 'kullanici')
VIEWER_PASSWORD = os.environ.get('LUYS_VIEWER_PASSWORD', 'luys-viewer-change-me')

DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///luys_cloud.db')
if DB_URL.startswith('postgres://'):
    DB_URL = 'postgresql+psycopg://' + DB_URL[len('postgres://'):]
elif DB_URL.startswith('postgresql://') and '+psycopg' not in DB_URL:
    DB_URL = 'postgresql+psycopg://' + DB_URL[len('postgresql://'):]

engine = create_engine(DB_URL, pool_pre_ping=True)
DEFAULT_STATE = {
    "orders": [],
    "daily": [],
    "calendar": {
        "0": {"h": 0, "b": 0},
        "1": {"h": 10, "b": 1},
        "2": {"h": 10, "b": 1},
        "3": {"h": 10, "b": 1},
        "4": {"h": 10, "b": 1},
        "5": {"h": 10, "b": 1},
        "6": {"h": 10, "b": 1}
    }
}


def init_db():
    with engine.begin() as c:
        c.execute(text(
            'CREATE TABLE IF NOT EXISTS luys_state '
            '(id INTEGER PRIMARY KEY, payload TEXT NOT NULL, '
            'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'
        ))
        row = c.execute(text('SELECT id FROM luys_state WHERE id=1')).first()
        if not row:
            c.execute(
                text('INSERT INTO luys_state (id,payload) VALUES (1,:p)'),
                {'p': json.dumps(DEFAULT_STATE, ensure_ascii=False)}
            )


try:
    init_db()
except OperationalError:
    pass


LOGIN_HTML = r"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#03101b">
<title>LÜYS • Giriş</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;font-family:Inter,Arial,sans-serif;background:#020810;color:#eef8ff}
body{min-height:100vh;display:flex;justify-content:center;padding:20px 18px 28px;overflow:auto;background:
radial-gradient(circle at 75% 14%,rgba(0,150,255,.22),transparent 25%),
radial-gradient(circle at 15% 70%,rgba(0,91,165,.16),transparent 30%),
linear-gradient(155deg,#01060b,#061725 52%,#020810)}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.16;background-image:
linear-gradient(rgba(75,180,255,.08) 1px,transparent 1px),
linear-gradient(90deg,rgba(75,180,255,.08) 1px,transparent 1px);
background-size:44px 44px;mask-image:linear-gradient(to bottom,transparent,#000 25%,#000 85%,transparent)}
.shell{width:min(94vw,440px);position:relative;z-index:1}
.topwords{display:flex;justify-content:space-between;color:#80bce5;font-size:9px;font-weight:800;letter-spacing:2px;text-transform:uppercase;margin:4px 5px 12px}
.brand{text-align:center;margin-bottom:18px}
.mark{width:86px;height:86px;margin:0 auto 12px;border-radius:25px;position:relative;background:linear-gradient(145deg,#0d263b,#06101c);border:1px solid rgba(115,198,255,.28);box-shadow:0 0 45px rgba(0,139,255,.25),inset 0 0 25px rgba(255,255,255,.035)}
.mark:before,.mark:after{content:"";position:absolute;background:linear-gradient(135deg,#f4fbff 0%,#83bddd 38%,#168ee0 62%,#eaf7ff 100%);filter:drop-shadow(0 0 8px rgba(37,164,255,.65))}
.mark:before{width:16px;height:54px;left:27px;top:16px;transform:skewY(-28deg);border-radius:3px}
.mark:after{width:42px;height:16px;left:29px;top:53px;transform:skewX(-28deg);border-radius:3px}
h1{font-size:43px;letter-spacing:6px;margin:0;font-weight:900;background:linear-gradient(180deg,#fff,#a8c7dc);-webkit-background-clip:text;color:transparent}
.tag{font-size:11px;letter-spacing:2.1px;color:#78bce8;margin-top:7px;font-weight:800}
.hero{font-size:13px;color:#c2d7e5;margin-top:13px}.hero b{color:#fff}
.line{width:62px;height:3px;border-radius:3px;background:#159fe8;margin:14px auto 0;box-shadow:0 0 13px #159fe8}
.card{padding:25px 23px 21px;border-radius:25px;background:linear-gradient(155deg,rgba(13,35,53,.94),rgba(4,15,26,.97));border:1px solid rgba(119,198,255,.25);box-shadow:0 24px 70px rgba(0,0,0,.58),inset 0 1px rgba(255,255,255,.04);backdrop-filter:blur(16px)}
.title{font-size:21px;font-weight:900;margin-bottom:5px}.sub{font-size:13px;color:#839bae;margin-bottom:19px}
.field{position:relative;margin:10px 0}
input[type=text],input[type=password]{width:100%;height:54px;border:1px solid #29475d;border-radius:14px;background:#071522;color:#fff;padding:0 16px;font-size:16px;outline:none;transition:.2s}
input:focus{border-color:#168fe0;box-shadow:0 0 0 3px rgba(22,143,224,.14)}input::placeholder{color:#71899b}
.options{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:12px 2px 4px;font-size:13px;color:#b8cddd}
.remember{display:flex;align-items:center;gap:8px;cursor:pointer}.remember input{width:18px;height:18px;accent-color:#159fea}
.linkBtn{border:0;background:none;color:#48bfff;padding:0;font:inherit;cursor:pointer}
.submit{width:100%;height:55px;margin-top:14px;border:0;border-radius:14px;cursor:pointer;color:white;font-size:15px;font-weight:900;letter-spacing:1.2px;background:linear-gradient(100deg,#0876bd,#15a7ef);box-shadow:0 12px 30px rgba(0,132,215,.28)}
.sep{display:flex;align-items:center;gap:12px;color:#6f8ba0;font-size:11px;margin:17px 0 11px}.sep:before,.sep:after{content:"";height:1px;flex:1;background:#24475f}
.bioBox{text-align:center}.bioBtn{width:58px;height:58px;border-radius:17px;border:1px solid #2c658a;background:#092033;color:#71c9ff;font-size:25px;cursor:pointer;box-shadow:inset 0 0 20px rgba(18,143,224,.08)}.bioText{margin-top:6px;color:#9fb7c8;font-size:11px}
.err{background:rgba(255,69,69,.1);border:1px solid rgba(255,92,92,.28);color:#ff9d9d;padding:10px 12px;border-radius:11px;font-size:13px;margin-bottom:13px}
.hint{display:none;margin-top:10px;padding:10px 12px;border-radius:11px;background:#0a2233;border:1px solid #204b67;color:#b9d5e8;font-size:12px;line-height:1.45}
.quote{text-align:center;font-size:14px;font-style:italic;color:#9fbfd5;line-height:1.45;margin:18px 0 13px}.quote strong{color:#e8f7ff;font-weight:700}
.status{display:flex;align-items:center;justify-content:center;gap:9px;flex-wrap:wrap;padding:10px 12px;border:1px solid #22506e;border-radius:999px;background:rgba(5,24,38,.78);font-size:9px;letter-spacing:1.25px;color:#8fc5e9;font-weight:800}
.dot{width:8px;height:8px;border-radius:50%;background:#20e58a;box-shadow:0 0 10px #20e58a}
.features{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:17px 0 9px;text-align:center}.feat{color:#77bce9}.ico{font-size:18px;margin-bottom:5px}.lbl{font-size:8px;letter-spacing:1.1px;color:#9fc3dc;font-weight:800}
.bottom{text-align:center;color:#57768b;font-size:8px;letter-spacing:1.4px;margin-top:13px}.bottom strong{color:#8bb9d6}
@media(max-width:600px){
 body{height:100svh;min-height:100svh;overflow:hidden;padding:8px 12px 10px;align-items:stretch}
 .shell{height:100%;width:min(96vw,430px);display:flex;flex-direction:column;justify-content:center}
 .topwords{display:none}
 .brand{margin:0 0 8px}
 .mark{width:52px;height:52px;margin-bottom:6px;border-radius:17px}
 .mark:before{width:11px;height:37px;left:18px;top:9px}
 .mark:after{width:29px;height:11px;left:19px;top:35px}
 h1{font-size:31px;letter-spacing:4px}
 .tag{font-size:8px;letter-spacing:1.55px;margin-top:4px}
 .hero{font-size:10px;margin-top:6px}
 .line{width:48px;height:2px;margin-top:7px}
 .card{padding:14px 16px 12px;border-radius:20px}
 .title{font-size:18px;margin-bottom:2px}
 .sub{font-size:10px;margin-bottom:9px}
 .field{margin:7px 0}
 input[type=text],input[type=password]{height:43px;border-radius:12px;font-size:14px;padding:0 13px}
 .options{font-size:11px;margin:8px 1px 2px}
 .remember{gap:6px}.remember input{width:16px;height:16px}
 .submit{height:45px;margin-top:9px;border-radius:12px;font-size:13px}
 .sep{margin:10px 0 7px;font-size:9px}
 .bioBtn{width:44px;height:44px;border-radius:14px;font-size:20px}
 .bioText{font-size:9px;margin-top:4px}
 .quote{font-size:10px;line-height:1.3;margin:8px 0 7px}
 .status{padding:7px 8px;font-size:7px;letter-spacing:.9px;gap:6px}
 .dot{width:6px;height:6px}
 .features{margin:8px 0 4px;gap:3px}
 .ico{font-size:15px;margin-bottom:3px}.lbl{font-size:6.8px;letter-spacing:.8px}
 .bottom{font-size:6.8px;line-height:1.35;margin-top:5px}
}
@media(max-width:600px) and (max-height:760px){
 .mark{width:46px;height:46px}
 .mark:before{transform:scale(.88) skewY(-28deg);transform-origin:top left}
 .mark:after{transform:scale(.88) skewX(-28deg);transform-origin:top left}
 h1{font-size:28px}
 .hero{display:none}
 .card{padding:12px 14px 10px}
 .quote{margin:6px 0 5px}
 .features{margin-top:6px}
}

</style>
</head>
<body>
<div class="shell">
 <div class="topwords"><span>PLANLA • ÜRET • TAKİP ET • BAŞAR</span><span>DAHA AKILLI • DAHA GÜÇLÜ</span></div>
 <div class="brand">
  <div class="mark"></div>
  <h1>LÜYS</h1>
  <div class="tag">LUUKMAS • ÜRETİM YÖNETİM SİSTEMİ</div>
  <div class="hero"><b>Hassas üretim.</b> Akıllı planlama. Tam kontrol.</div>
  <div class="line"></div>
 </div>
 <form class="card" method="post">
  <div class="title">Sisteme Giriş</div>
  <div class="sub">Üretimi planla, takip et ve yönet.</div>
  {% if err %}<div class="err">Kullanıcı adı veya parola yanlış.</div>{% endif %}
  <div class="field"><input id="username" name="username" type="text" placeholder="Kullanıcı adı" autocomplete="username" required></div>
  <div class="field"><input name="password" type="password" placeholder="Parola" autocomplete="current-password" required></div>
  <div class="options">
   <label class="remember"><input id="remember" name="remember" value="1" type="checkbox"> Beni Hatırla</label>
   <button type="button" class="linkBtn" onclick="toggleForgot()">Şifremi Unuttum?</button>
  </div>
  <div id="forgotHint" class="hint">Şifre LÜYS yöneticisi tarafından değiştirilir.</div>
  <button class="submit" type="submit">SİSTEME GİRİŞ →</button>
  <div class="sep"><span>GÜVENLİ ERİŞİM</span></div>
  <div class="bioBox"><button class="bioBtn" type="button" onclick="bioInfo()">◎</button><div class="bioText">Biyometrik Giriş</div><div id="bioHint" class="hint">Biyometrik giriş PWA cihaz doğrulama adımında etkinleştirilecek.</div></div>
 </form>
 <div class="quote"><strong>“Küçük detaylar, büyük işler başarır.”</strong><br>Üretimi şansa bırakma. Kontrolü elinde tut.</div>
 <div class="status"><span class="dot"></span><span>SYSTEM ONLINE</span><span>•</span><span>CLOUD CONNECTED</span><span>•</span><span>SECURE ACCESS</span></div>
 <div class="features">
  <div class="feat"><div class="ico">⚙</div><div class="lbl">PLANLA</div></div>
  <div class="feat"><div class="ico">▥</div><div class="lbl">ÜRET</div></div>
  <div class="feat"><div class="ico">☷</div><div class="lbl">TAKİP ET</div></div>
  <div class="feat"><div class="ico">◎</div><div class="lbl">BAŞAR</div></div>
 </div>
 <div class="bottom"><strong>LUUKMAS MAKİNA LTD. ŞTİ.</strong><br>LÜYS • ÜRETİM YÖNETİM SİSTEMİ</div>
</div>
<script>
const u=document.getElementById('username'),r=document.getElementById('remember');
try{const saved=localStorage.getItem('luys_username');if(saved){u.value=saved;r.checked=true}}catch(e){}
document.querySelector('form').addEventListener('submit',()=>{try{if(r.checked)localStorage.setItem('luys_username',u.value.trim());else localStorage.removeItem('luys_username')}catch(e){}});
function toggleForgot(){const x=document.getElementById('forgotHint');x.style.display=x.style.display==='block'?'none':'block'}
function bioInfo(){const x=document.getElementById('bioHint');x.style.display=x.style.display==='block'?'none':'block'}
</script>
</body>
</html>"""


def auth_ok():
    return session.get('luys_auth') is True


def current_role():
    return session.get('luys_role')


def can_edit():
    return current_role() == 'admin'


@app.route('/login', methods=['GET', 'POST'])
def login():
    err = False
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            remember = request.form.get('remember') == '1'
            session.clear()
            session.permanent = remember
            session['luys_auth'] = True
            session['luys_role'] = 'admin'
            session['luys_username'] = username
            return redirect('/')

        if username == VIEWER_USER and password == VIEWER_PASSWORD:
            remember = request.form.get('remember') == '1'
            session.clear()
            session.permanent = remember
            session['luys_auth'] = True
            session['luys_role'] = 'viewer'
            session['luys_username'] = username
            return redirect('/')

        err = True
    return render_template_string(LOGIN_HTML, err=err)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.before_request
def protect():
    if request.path.startswith('/login') or request.path.startswith('/health'):
        return None
    if not auth_ok():
        if request.path.startswith('/api/'):
            return jsonify({'error': 'unauthorized'}), 401
        return redirect('/login')


@app.route('/')
def home():
    return send_from_directory('static', 'index.html')


@app.route('/api/me', methods=['GET'])
def me():
    """Ön yüz, kullanıcının düzenleme yetkisini buradan öğrenebilir."""
    return jsonify({
        'username': session.get('luys_username'),
        'role': current_role(),
        'can_edit': can_edit()
    })


@app.route('/api/state', methods=['GET'])
def get_state():
    init_db()
    with engine.begin() as c:
        row = c.execute(text('SELECT payload FROM luys_state WHERE id=1')).first()
    return app.response_class(
        row[0] if row else json.dumps(DEFAULT_STATE, ensure_ascii=False),
        mimetype='application/json'
    )


@app.route('/api/state', methods=['PUT'])
def put_state():
    # Viewer hesabı hiçbir üretim verisini değiştiremez.
    if not can_edit():
        return jsonify({'error': 'read_only', 'message': 'Bu kullanıcı yalnızca görüntüleme yetkisine sahip.'}), 403

    payload = request.get_json(force=True, silent=False)
    if not isinstance(payload, dict):
        return jsonify({'error': 'invalid'}), 400

    raw = json.dumps(payload, ensure_ascii=False)
    if len(raw) > 8_000_000:
        return jsonify({'error': 'too_large'}), 413

    init_db()
    with engine.begin() as c:
        c.execute(
            text('UPDATE luys_state SET payload=:p, updated_at=CURRENT_TIMESTAMP WHERE id=1'),
            {'p': raw}
        )
    return jsonify({'ok': True})


@app.route('/api/export', methods=['GET'])
def export_state():
    return get_state()


@app.route('/health')
def health():
    return jsonify({'ok': True})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8080')), debug=False)
