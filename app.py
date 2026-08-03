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

LOGIN_HTML='''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LÜYS Giriş</title><style>body{font-family:Arial;background:#eef3f8;margin:0;display:grid;place-items:center;min-height:100vh;color:#16324a}.box{background:white;padding:28px;border-radius:18px;box-shadow:0 8px 30px #0002;width:min(92vw,390px)}h1{margin:0 0 4px}.sub{font-size:13px;color:#687b89;margin-bottom:22px}input{width:100%;padding:12px;margin:7px 0;border:1px solid #aab9c6;border-radius:10px;box-sizing:border-box}button{width:100%;padding:12px;margin-top:10px;background:#0b67a3;color:white;border:0;border-radius:10px;font-weight:800}.err{color:#b42318;font-size:13px}</style></head><body><form class="box" method="post"><h1>LÜYS</h1><div class="sub">LUUKMAS Üretim Yönetim Sistemi</div>{% if err %}<div class="err">Kullanıcı adı veya parola yanlış.</div>{% endif %}<input name="username" placeholder="Kullanıcı adı" autocomplete="username" required><input name="password" type="password" placeholder="Parola" autocomplete="current-password" required><button>GİRİŞ YAP</button></form></body></html>'''

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
    return app.response_class(row[0] if row else json.dumps(DEFAULT_STATE),mimetype='application/json')

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
