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
<meta name="theme-color" content="#04111f">
<title>LÜYS • Giriş</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;font-family:Inter,Arial,sans-serif;background:#030b14;color:#eef7ff}
body{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:22px;background:radial-gradient(circle at 75% 20%,rgba(0,145,255,.20),transparent 28%),radial-gradient(circle at 18% 80%,rgba(0,92,170,.15),transparent 30%),linear-gradient(145deg,#02070d 0%,#071522 52%,#020810 100%);overflow:auto}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.18;background-image:linear-gradient(rgba(77,177,255,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(77,177,255,.08) 1px,transparent 1px);background-size:42px 42px;transform:perspective(500px) rotateX(58deg) scale(1.5);transform-origin:center bottom}
.shell{width:min(94vw,430px);position:relative;z-index:1}
.brand{text-align:center;margin-bottom:22px}
.mark{width:88px;height:88px;margin:0 auto 14px;border-radius:25px;position:relative;background:linear-gradient(145deg,#0d263b,#06101c);border:1px solid rgba(115,198,255,.28);box-shadow:0 0 45px rgba(0,139,255,.22),inset 0 0 25px rgba(255,255,255,.035)}
.mark:before,.mark:after{content:"";position:absolute;background:linear-gradient(135deg,#f4fbff 0%,#83bddd 38%,#168ee0 62%,#eaf7ff 100%);filter:drop-shadow(0 0 8px rgba(37,164,255,.65))}
.mark:before{width:16px;height:54px;left:27px;top:16px;transform:skewY(-28deg);border-radius:3px}
.mark:after{width:42px;height:16px;left:29px;top:53px;transform:skewX(-28deg);border-radius:3px}
h1{font-size:42px;letter-spacing:5px;margin:0;font-weight:850;background:linear-gradient(180deg,#fff,#a8c7dc);-webkit-background-clip:text;color:transparent}
.tag{font-size:12px;letter-spacing:2.2px;color:#77bce9;margin-top:8px;font-weight:700}
.line{width:58px;height:3px;border-radius:3px;background:#138fd8;margin:17px auto 0;box-shadow:0 0 13px #138fd8}
.card{padding:27px 24px 24px;border-radius:25px;background:linear-gradient(155deg,rgba(13,35,53,.93),rgba(4,15,26,.96));border:1px solid rgba(119,198,255,.22);box-shadow:0 24px 70px rgba(0,0,0,.55),inset 0 1px rgba(255,255,255,.04);backdrop-filter:blur(16px)}
.title{font-size:21px;font-weight:800;margin-bottom:5px}.sub{font-size:13px;color:#839bae;margin-bottom:21px}
.field{position:relative;margin:11px 0}
input[type=text],input[type=password]{width:100%;height:55px;border:1px solid #29475d;border-radius:14px;background:#071522;color:#fff;padding:0 16px;font-size:16px;outline:none;transition:.2s}
input:focus{border-color:#168fe0;box-shadow:0 0 0 3px rgba(22,143,224,.14)}input::placeholder{color:#71899b}
.options{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:12px 2px 4px;font-size:13px;color:#b8cddd}
.remember{display:flex;align-items:center;gap:8px;cursor:pointer}.remember input{width:18px;height:18px;accent-color:#159fea}
.linkBtn{border:0;background:none;color:#48bfff;padding:0;font:inherit;cursor:pointer}
button.submit{width:100%;height:55px;margin-top:14px;border:0;border-radius:14px;cursor:pointer;color:white;font-size:15px;font-weight:900;letter-spacing:1.2px;background:linear-gradient(100deg,#0876bd,#15a7ef);box-shadow:0 12px 30px rgba(0,132,215,.28)}
button.submit:active{transform:translateY(1px)}
.err{background:rgba(255,69,69,.1);border:1px solid rgba(255,92,92,.28);color:#ff9d9d;padding:10px 12px;border-radius:11px;font-size:13px;margin-bottom:13px}
.bioBox{margin-top:18px;padding-top:17px;border-top:1px solid #244359;text-align:center}
.bioBtn{width:64px;height:64px;border-radius:18px;border:1px solid #2c658a;background:#092033;color:#71c9ff;font-size:27px;cursor:pointer;box-shadow:inset 0 0 20px rgba(18,143,224,.08)}
.bioText{margin-top:7px;color:#9fb7c8;font-size:12px}
.secure{text-align:center;color:#55758b;font-size:10px;letter-spacing:1.4px;margin-top:16px}
.hint{display:none;margin-top:10px;padding:10px 12px;border-radius:11px;background:#0a2233;border:1px solid #204b67;color:#b9d5e8;font-size:12px;line-height:1.45}
@media(max-height:760px){body{padding:12px}.brand{margin-bottom:12px}.mark{width:68px;height:68px}.mark:before{transform:scale(.8) skewY(-28deg);transform-origin:top left}.mark:after{transform:scale(.8) skewX(-28deg);transform-origin:top left}h1{font-size:34px}.card{padding:20px}.bioBox{margin-top:12px;padding-top:12px}}
</style>
</head>
<body>
<div class="shell">
 <div class="brand">
  <div class="mark"></div>
  <h1>LÜYS</h1>
  <div class="tag">LUUKMAS • ÜRETİM YÖNETİM SİSTEMİ</div>
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
  <div id="forgotHint" class="hint">Şifre, LÜYS yöneticisi tarafından değiştirilir. Yönetici hesabı için Render'daki <b>LUYS_PASSWORD</b> değerini güncelleyebilirsin.</div>
  <button class="submit" type="submit">SİSTEME GİRİŞ →</button>
  <div class="bioBox">
    <button class="bioBtn" type="button" onclick="bioInfo()" aria-label="Biyometrik giriş">◉</button>
    <div class="bioText">Biyometrik Giriş</div>
    <div id="bioHint" class="hint">Biyometrik giriş, PWA kurulumu ve cihaz doğrulama adımında etkinleştirilecek.</div>
  </div>
  <div class="secure">LÜYS • SECURE CLOUD ACCESS</div>
 </form>
</div>
<script>
const u=document.getElementById('username'),r=document.getElementById('remember');
try{
 const saved=localStorage.getItem('luys_username');
 if(saved){u.value=saved;r.checked=true}
}catch(e){}
document.querySelector('form').addEventListener('submit',()=>{
 try{
  if(r.checked)localStorage.setItem('luys_username',u.value.trim());
  else localStorage.removeItem('luys_username');
 }catch(e){}
});
function toggleForgot(){
 const x=document.getElementById('forgotHint');
 x.style.display=x.style.display==='block'?'none':'block';
}
function bioInfo(){
 const x=document.getElementById('bioHint');
 x.style.display=x.style.display==='block'?'none':'block';
}
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
