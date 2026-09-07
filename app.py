import os, json
from flask import Flask, request, jsonify, send_from_directory, redirect, session, render_template_string
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY','change-this-secret')
USER = os.environ.get('LUYS_USER','admin')
PASSWORD = os.environ.get('LUYS_PASSWORD','luys-change-me')
VIEWER_USER = os.environ.get('LUYS_VIEWER_USER','metahan')
VIEWER_PASSWORD = os.environ.get('LUYS_VIEWER_PASSWORD','5454')
DB_URL = os.environ.get('DATABASE_URL','sqlite:///luys_cloud.db')
if DB_URL.startswith('postgres://'):
    DB_URL='postgresql+psycopg://'+DB_URL[len('postgres://'):]
elif DB_URL.startswith('postgresql://') and '+psycopg' not in DB_URL:
    DB_URL='postgresql+psycopg://'+DB_URL[len('postgresql://'):]
engine = create_engine(DB_URL, pool_pre_ping=True)
DEFAULT_STATE={"orders":[],"daily":[],"calendar":{"0":{"h":0,"b":0},"1":{"h":10,"b":1},"2":{"h":10,"b":1},"3":{"h":10,"b":1},"4":{"h":10,"b":1},"5":{"h":10,"b":1},"6":{"h":10,"b":1}}}

def init_db():
    with engine.begin() as c:
        c.execute(text('CREATE TABLE IF NOT EXISTS luys_state (id INTEGER PRIMARY KEY, payload TEXT NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'))
        row=c.execute(text('SELECT id FROM luys_state WHERE id=1')).first()
        if not row:
            c.execute(text('INSERT INTO luys_state (id,payload) VALUES (1,:p)'),{'p':json.dumps(DEFAULT_STATE,ensure_ascii=False)})

try:
    init_db()
except OperationalError:
    pass

LOGIN_HTML='''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#06111d">
<title>LÜYS Giriş</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
body{
  min-height:100vh;
  color:#f4f8fc;
  background:
    radial-gradient(circle at 70% 16%,rgba(0,140,255,.18),transparent 26%),
    radial-gradient(circle at 16% 72%,rgba(0,96,180,.14),transparent 30%),
    linear-gradient(145deg,#02070c 0%,#07131f 43%,#0a1d2d 100%);
  overflow-x:hidden;
}
body:before{
  content:"";
  position:fixed;inset:0;
  background:
    linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.018) 1px,transparent 1px);
  background-size:38px 38px;
  pointer-events:none;
}
.page{
  min-height:100vh;
  display:grid;
  grid-template-columns:minmax(320px,1.15fr) minmax(340px,.85fr);
}
.brand{
  position:relative;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
  padding:clamp(34px,5vw,70px);
  overflow:hidden;
  border-right:1px solid rgba(255,255,255,.07);
}
.brand:after{
  content:"";
  position:absolute;inset:auto -12% -26% 18%;
  height:56%;
  background:radial-gradient(ellipse at center,rgba(0,128,255,.22),transparent 58%);
  filter:blur(18px);
}
.eyebrow{font-size:12px;letter-spacing:.34em;color:#9fb6ca;text-transform:uppercase}
.logo-wrap{position:relative;z-index:2;margin-top:7vh}
.mark{
  position:relative;width:132px;height:112px;margin-bottom:28px;
  filter:drop-shadow(0 18px 28px rgba(0,102,255,.24));
}
.mark .silver,.mark .blue{
  position:absolute;bottom:0;border-radius:4px;
  transform:skewY(-31deg);
  transform-origin:bottom;
}
.mark .silver{
  left:11px;width:53px;height:103px;
  background:linear-gradient(90deg,#8f9aa4 0%,#f5f7f8 42%,#77828d 100%);
  clip-path:polygon(0 0,100% 22%,100% 100%,0 79%);
}
.mark .blue{
  left:57px;width:62px;height:78px;
  background:linear-gradient(135deg,#084b98 0%,#0797ff 46%,#3bc5ff 100%);
  clip-path:polygon(0 0,100% 26%,100% 100%,0 76%);
  box-shadow:0 0 26px rgba(0,153,255,.46);
}
.logo-title{
  margin:0;font-size:clamp(58px,7vw,96px);line-height:.9;
  letter-spacing:.08em;font-weight:800;
  background:linear-gradient(180deg,#fff 0%,#d7dce1 42%,#8d98a2 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  text-shadow:0 12px 30px rgba(0,0,0,.28);
}
.logo-sub{margin-top:18px;font-size:15px;letter-spacing:.34em;color:#d4dee6;text-transform:uppercase}
.rule{margin-top:24px;width:min(520px,82%);height:1px;background:linear-gradient(90deg,#139cff,rgba(19,156,255,0))}
.slogan{margin-top:18px;font-size:13px;letter-spacing:.31em;color:#a7bac9;text-transform:uppercase}
.bottom-copy{position:relative;z-index:2}
.bottom-copy b{display:block;font-size:15px;letter-spacing:.42em}
.bottom-copy span{display:block;margin-top:7px;font-size:10px;letter-spacing:.32em;color:#7f97aa}
.login-side{
  display:flex;align-items:center;justify-content:center;
  padding:38px clamp(24px,5vw,70px);
  position:relative;
}
.login-side:before{
  content:"";position:absolute;inset:8% 8%;
  background:radial-gradient(circle,rgba(0,138,255,.10),transparent 61%);
  filter:blur(12px);pointer-events:none;
}
.box{
  position:relative;z-index:2;
  width:min(100%,460px);
  padding:34px;
  border-radius:28px;
  background:linear-gradient(180deg,rgba(13,34,52,.92),rgba(6,20,33,.92));
  border:1px solid rgba(127,183,226,.18);
  box-shadow:0 30px 70px rgba(0,0,0,.44),inset 0 1px rgba(255,255,255,.04);
  backdrop-filter:blur(16px);
}
.mini-logo{display:flex;align-items:center;gap:14px;margin-bottom:30px}
.mini-mark{
  width:48px;height:48px;border-radius:14px;
  background:linear-gradient(145deg,#173148,#07131f);
  border:1px solid rgba(255,255,255,.09);
  display:grid;place-items:center;box-shadow:0 12px 28px rgba(0,0,0,.28)
}
.mini-mark:before{
  content:"L";font-weight:900;font-size:30px;
  background:linear-gradient(135deg,#e7edf2 20%,#169cff 72%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
}
.mini-logo b{font-size:25px;letter-spacing:.11em}
.mini-logo span{display:block;margin-top:3px;font-size:11px;letter-spacing:.16em;color:#8ca3b5}
h1{margin:0;font-size:31px;letter-spacing:-.02em}
.lead{margin:8px 0 26px;color:#8fa5b7;font-size:14px;line-height:1.5}
.field{position:relative;margin:12px 0}
.field input{
  width:100%;height:56px;padding:0 17px 0 49px;
  border-radius:14px;border:1px solid #25445e;
  background:#0d2437;color:#fff;outline:none;
  font-size:16px;transition:.18s ease;
}
.field input::placeholder{color:#8195a5}
.field input:focus{border-color:#149cff;box-shadow:0 0 0 3px rgba(20,156,255,.12)}
.ico{position:absolute;left:17px;top:50%;transform:translateY(-50%);font-size:20px;opacity:.82}
button{
  width:100%;height:56px;margin-top:14px;border:0;border-radius:14px;
  color:#fff;font-weight:800;font-size:16px;letter-spacing:.04em;cursor:pointer;
  background:linear-gradient(90deg,#0875ff,#10b7ff);
  box-shadow:0 12px 28px rgba(0,123,255,.28);
}
button:active{transform:translateY(1px)}
.err{
  margin:0 0 14px;padding:11px 13px;border-radius:12px;
  color:#ffd7d7;background:rgba(198,53,53,.14);border:1px solid rgba(255,92,92,.26);font-size:13px
}
.secure{
  display:flex;align-items:center;gap:8px;justify-content:center;
  margin-top:18px;color:#71899c;font-size:11px;letter-spacing:.08em;text-transform:uppercase
}
.dot{width:7px;height:7px;border-radius:50%;background:#28d17c;box-shadow:0 0 12px rgba(40,209,124,.65)}
@media(max-width:860px){
  .page{display:block;min-height:100vh}
  .brand{
    min-height:38vh;padding:34px 26px 26px;border-right:0;border-bottom:1px solid rgba(255,255,255,.07);
    justify-content:center;
  }
  .eyebrow,.bottom-copy{display:none}
  .logo-wrap{margin:0;text-align:center}
  .mark{width:92px;height:78px;margin:0 auto 18px}
  .mark .silver{left:7px;width:38px;height:72px}
  .mark .blue{left:40px;width:45px;height:55px}
  .logo-title{font-size:56px}
  .logo-sub{font-size:10px;letter-spacing:.24em}
  .rule{margin:16px auto 0}
  .slogan{font-size:9px;letter-spacing:.23em}
  .login-side{padding:24px 18px 34px;align-items:flex-start}
  .box{padding:26px 20px;border-radius:22px;margin-top:-1px}
  .mini-logo{display:none}
  h1{font-size:26px}
}
</style>
</head>
<body>
<div class="page">
  <section class="brand">
    <div class="eyebrow">PLANLA &nbsp; • &nbsp; ÜRET &nbsp; • &nbsp; TAKİP ET &nbsp; • &nbsp; BAŞAR</div>
    <div class="logo-wrap">
      <div class="mark"><div class="silver"></div><div class="blue"></div></div>
      <div class="logo-title">LÜYS</div>
      <div class="logo-sub">Üretim Yönetim Sistemi</div>
      <div class="rule"></div>
      <div class="slogan">İmalatı daha akıllı yönet</div>
    </div>
    <div class="bottom-copy"><b>LUUKMAS</b><span>MAKİNA LTD. ŞTİ.</span></div>
  </section>

  <section class="login-side">
    <form class="box" method="post">
      <div class="mini-logo">
        <div class="mini-mark"></div>
        <div><b>LÜYS</b><span>LUUKMAS ÜRETİM YÖNETİM SİSTEMİ</span></div>
      </div>
      <h1>Hoş geldin</h1>
      <div class="lead">Üretimi planla, operasyonları takip et ve terminleri tek ekrandan yönet.</div>
      {% if err %}<div class="err">Kullanıcı adı veya parola yanlış.</div>{% endif %}
      <div class="field"><span class="ico">◉</span><input name="username" placeholder="Kullanıcı adı" autocomplete="username" required></div>
      <div class="field"><span class="ico">◆</span><input name="password" type="password" placeholder="Parola" autocomplete="current-password" required></div>
      <button>GİRİŞ YAP →</button>
      <div class="secure"><span class="dot"></span> Güvenli bulut bağlantısı</div>
    </form>
  </section>
</div>
</body>
</html>'''

def auth_ok(): return session.get('luys_auth') is True

def can_edit(): return session.get('luys_role') == 'admin'

@app.route('/login',methods=['GET','POST'])
def login():
    err=False
    if request.method=='POST':
        username=request.form.get('username','')
        password=request.form.get('password','')
        if username==USER and password==PASSWORD:
            session.clear()
            session['luys_auth']=True
            session['luys_role']='admin'
            session['luys_username']=username
            return redirect('/')
        if username==VIEWER_USER and password==VIEWER_PASSWORD:
            session.clear()
            session['luys_auth']=True
            session['luys_role']='viewer'
            session['luys_username']='Metahan Mutlu'
            return redirect('/')
        err=True
    return render_template_string(LOGIN_HTML,err=err)

@app.route('/logout')
def logout():
    session.clear(); return redirect('/login')

@app.before_request
def protect():
    if request.path.startswith('/login') or request.path.startswith('/health'):
        return None
    if not auth_ok():
        if request.path.startswith('/api/'):
            return jsonify({'error':'unauthorized'}),401
        return redirect('/login')

@app.route('/')
def home(): return send_from_directory('static','index.html')


@app.route('/api/me',methods=['GET'])
def api_me():
    return jsonify({
        'username': session.get('luys_username', USER),
        'role': session.get('luys_role','viewer'),
        'can_edit': can_edit()
    })

@app.route('/api/state',methods=['GET'])
def get_state():
    init_db()
    with engine.begin() as c:
        row=c.execute(text('SELECT payload FROM luys_state WHERE id=1')).first()
    raw=row[0] if row else json.dumps(DEFAULT_STATE)
    # Görüntüleyici hesap üretim verilerini okuyabilir; finansal alanlar yalnızca yöneticiye gider.
    if not can_edit():
        try:
            data=json.loads(raw)
            data.pop('accounting',None)
            data.pop('laborFinance',None)
            raw=json.dumps(data,ensure_ascii=False)
        except Exception:
            pass
    return app.response_class(raw,mimetype='application/json')

@app.route('/api/state',methods=['PUT'])
def put_state():
    if not can_edit():
        return jsonify({'error':'forbidden'}),403
    payload=request.get_json(force=True,silent=False)
    if not isinstance(payload,dict): return jsonify({'error':'invalid'}),400
    raw=json.dumps(payload,ensure_ascii=False)
    if len(raw)>8_000_000: return jsonify({'error':'too_large'}),413
    init_db()
    with engine.begin() as c:
        c.execute(text('UPDATE luys_state SET payload=:p, updated_at=CURRENT_TIMESTAMP WHERE id=1'),{'p':raw})
    return jsonify({'ok':True})

@app.route('/api/export',methods=['GET'])
def export_state():
    return get_state()

@app.route('/health')
def health(): return jsonify({'ok':True})

if __name__=='__main__':
    init_db(); app.run(host='0.0.0.0',port=int(os.environ.get('PORT','8080')),debug=False)
