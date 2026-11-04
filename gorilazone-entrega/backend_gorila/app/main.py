"""Reconstrução local GorilaZone. Dados persistidos em SQLite, sem dados fictícios."""
import base64, hashlib, hmac, io, json, os, secrets, sqlite3, time
from datetime import date, datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
import qrcode

ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.getenv('GORILA_DB', str(ROOT / 'data' / 'gorila.db')))
DB.parent.mkdir(parents=True, exist_ok=True)
app = FastAPI(title='GorilaZone • API local', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173','http://127.0.0.1:5173'], allow_methods=['*'], allow_headers=['*'])

def connection():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c

with connection() as c:
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, academy_id TEXT NOT NULL, role TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), expires INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, academy_id TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL, created TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS records_scope ON records(academy_id,kind);
    CREATE TABLE IF NOT EXISTS leads(id TEXT PRIMARY KEY, data TEXT NOT NULL, created TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS audit(id TEXT PRIMARY KEY, academy_id TEXT NOT NULL, user_id TEXT NOT NULL, action TEXT NOT NULL, created TEXT NOT NULL);
    ''')

def now(): return datetime.now(timezone.utc).isoformat()
def fail(message, status=400): raise HTTPException(status, message)
def password_hash(password):
    salt = secrets.token_hex(16)
    key = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1).hex()
    return salt + ':' + key

def verify(password, stored):
    salt, key = stored.split(':')
    return hmac.compare_digest(hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1).hex(), key)

def current(request: Request):
    token = request.headers.get('authorization','').removeprefix('Bearer ')
    digest = hashlib.sha256(token.encode()).hexdigest()
    with connection() as c:
        row = c.execute('SELECT users.* FROM sessions JOIN users ON users.id=sessions.user_id WHERE token=? AND expires>?',(digest,int(time.time()))).fetchone()
    if not row: fail('Entre novamente para continuar.',401)
    return dict(row)

def public(user): return {k:v for k,v in user.items() if k!='password'}
def audit(c,user,action): c.execute('INSERT INTO audit VALUES(?,?,?,?,?)',(secrets.token_hex(16),user['academy_id'],user['id'],action,now()))

class Registration(BaseModel):
    name: str = Field(min_length=2,max_length=100)
    email: str = Field(min_length=5,max_length=180)
    password: str = Field(min_length=10,max_length=128)
    academy_name: str = Field(min_length=2,max_length=120)

class Login(BaseModel):
    email: str
    password: str

class Contact(BaseModel):
    name: str = Field(min_length=2,max_length=100)
    email: str = Field(min_length=5,max_length=180)
    academy: str = Field(default='',max_length=120)
    message: str = Field(min_length=5,max_length=2000)
    consent: bool
    website: str = ''

@app.get('/api/health')
def health(): return {'status':'ok','storage':'sqlite','version':'1.0.0'}

@app.post('/api/contact',status_code=201)
def contact(data: Contact):
    if data.website: return {'message':'Solicitação recebida.'}
    if not data.consent: fail('Autorize o uso dos dados para responder ao contato.')
    if '@' not in data.email: fail('Informe um e-mail válido.')
    lead_id=secrets.token_hex(16)
    with connection() as c:
        # Limita repetição do mesmo e-mail; não envia mensagens externas.
        recent=c.execute('SELECT data,created FROM leads ORDER BY created DESC LIMIT 100').fetchall()
        if any(json.loads(r['data'])['email'].lower()==data.email.lower() and (datetime.now(timezone.utc)-datetime.fromisoformat(r['created'])).total_seconds()<60 for r in recent): fail('Solicitação já recebida. Aguarde um minuto.',429)
        c.execute('INSERT INTO leads VALUES(?,?,?)',(lead_id,data.model_dump_json(exclude={'website'}),now()))
    return {'id':lead_id,'message':'Solicitação salva. A equipe pode consultá-la no computador que hospeda esta API.'}

@app.post('/api/auth/register',status_code=201)
def register(data: Registration):
    if '@' not in data.email: fail('Informe um e-mail válido.')
    user_id,academy_id=secrets.token_hex(16),secrets.token_hex(16)
    with connection() as c:
        try: c.execute('INSERT INTO users VALUES(?,?,?,?,?,?)',(user_id,data.name.strip(),data.email.strip().lower(),password_hash(data.password),academy_id,'admin'))
        except sqlite3.IntegrityError: fail('Este e-mail já está cadastrado.',409)
        c.execute('INSERT INTO records VALUES(?,?,?,?,?)',(academy_id,academy_id,'academies',json.dumps({'name':data.academy_name}),now()))
    return {'id':user_id,'message':'Academia criada. Entre para continuar.'}

@app.post('/api/auth/login')
def login(data: Login):
    with connection() as c:
        row=c.execute('SELECT * FROM users WHERE email=?',(data.email.strip().lower(),)).fetchone()
        if not row or not verify(data.password,row['password']): fail('E-mail ou senha incorretos.',401)
        token=secrets.token_urlsafe(48)
        c.execute('DELETE FROM sessions WHERE expires<=?',(int(time.time()),))
        c.execute('INSERT INTO sessions VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),row['id'],int(time.time())+28800))
    return {'access_token':token,'token_type':'bearer','expires_in':28800,'user':public(dict(row))}

@app.get('/api/auth/me')
def me(user=Depends(current)): return public(user)

@app.post('/api/auth/logout')
def logout(request: Request,user=Depends(current)):
    token=request.headers.get('authorization','').removeprefix('Bearer ')
    with connection() as c: c.execute('DELETE FROM sessions WHERE token=?',(hashlib.sha256(token.encode()).hexdigest(),))
    return {'message':'Sessão encerrada.'}

KINDS={'students','plans','enrollments','workouts','payments','assessments','notifications'}

def records(c,user,kind):
    rows=c.execute('SELECT * FROM records WHERE academy_id=? AND kind=? ORDER BY created DESC',(user['academy_id'],kind)).fetchall()
    return [{**json.loads(r['data']),'id':r['id'],'created_at':r['created']} for r in rows]

def get_record(c,user,kind,record_id):
    r=c.execute('SELECT * FROM records WHERE id=? AND academy_id=? AND kind=?',(record_id,user['academy_id'],kind)).fetchone()
    if not r: fail('Registro não encontrado.',404)
    return json.loads(r['data'])

def validate(c,user,kind,data):
    if kind not in KINDS: fail('Módulo inexistente.',404)
    if not isinstance(data,dict): fail('Formato inválido.')
    required={'students':['name','email'],'plans':['name','price'],'enrollments':['student_id','plan_id','start_date','end_date'],'workouts':['student_id','title','exercises'],'payments':['student_id','amount','due_date','status'],'assessments':['student_id','date','weight','notes'],'notifications':['title','message']}[kind]
    if any(k not in data or str(data[k]).strip()=='' for k in required): fail('Preencha todos os campos obrigatórios.')
    if 'student_id' in data: get_record(c,user,'students',data['student_id'])
    if 'plan_id' in data: get_record(c,user,'plans',data['plan_id'])
    for key in ['price','amount','weight']:
        if key in data:
            try: value=float(data[key])
            except (ValueError,TypeError): fail('Valor numérico inválido.')
            if not (0 <= value < 100000000): fail('Valor fora do intervalo permitido.')
            if key=='weight' and value==0: fail('Peso deve ser maior que zero.')
            data[key]=value
    for key in ['start_date','end_date','due_date','date']:
        if key in data:
            try: date.fromisoformat(data[key])
            except (ValueError,TypeError): fail('Data inválida.')
    if kind=='students' and '@' not in data['email']: fail('E-mail inválido.')
    if kind=='payments' and data['status'] not in ['pendente','pago']: fail('Status inválido.')
    if kind=='enrollments':
        if data['end_date']<data['start_date']: fail('O fim deve ser igual ou posterior ao início.')
        data.setdefault('status','ativa')
        if data['status'] not in ['ativa','cancelada']: fail('Status inválido.')
    if len(json.dumps(data))>16000: fail('Registro muito extenso.')
    return {k:data[k] for k in required+(['status'] if kind=='enrollments' else [])}

@app.get('/api/academies')
def academies(user=Depends(current)):
    with connection() as c: return records(c,user,'academies')

@app.get('/api/dashboard')
def dashboard(user=Depends(current)):
    with connection() as c:
        students=records(c,user,'students'); enrollments=records(c,user,'enrollments'); payments=records(c,user,'payments'); attendance=records(c,user,'attendance')
    today=date.today().isoformat()
    active=[e for e in enrollments if e.get('status')=='ativa' and e['start_date']<=today<=e['end_date']]
    risks=[]
    for student in students:
        dates=[a['day'] for a in attendance if a['student_id']==student['id']]
        last=max(dates) if dates else None
        if not last or (date.today()-date.fromisoformat(last)).days>=14: risks.append({'name':student['name'],'last_attendance':last,'reason':'Sem presença registrada' if not last else '14 dias ou mais sem presença'})
    return {'students':len(students),'active_enrollments':len(active),'attendance_today':sum(a['day']==today for a in attendance),'paid':round(sum(p['amount'] for p in payments if p['status']=='pago'),2),'pending':round(sum(p['amount'] for p in payments if p['status']=='pendente'),2),'attention':risks}

@app.get('/api/attendance/qr-code')
def qr(user=Depends(current)):
    image=qrcode.make('GORILAZONE:ACADEMY:'+user['academy_id']); output=io.BytesIO(); image.save(output,format='PNG')
    return Response(output.getvalue(),media_type='image/png',headers={'Cache-Control':'no-store'})

@app.get('/api/attendance')
def attendance(user=Depends(current)):
    with connection() as c: return records(c,user,'attendance')

@app.post('/api/attendance/check-in',status_code=201)
def checkin(data:dict,user=Depends(current)):
    sid=data.get('student_id'); today=date.today().isoformat()
    if data.get('qr_code')!='GORILAZONE:ACADEMY:'+user['academy_id']: fail('QR de outra academia ou inválido.')
    with connection() as c:
        c.execute('BEGIN IMMEDIATE')
        get_record(c,user,'students',sid)
        if not any(e['student_id']==sid and e.get('status')=='ativa' and e['start_date']<=today<=e['end_date'] for e in records(c,user,'enrollments')): fail('Aluno sem matrícula ativa nesta data.')
        record_id=hashlib.sha256((user['academy_id']+sid+today).encode()).hexdigest()
        try: c.execute('INSERT INTO records VALUES(?,?,?,?,?)',(record_id,user['academy_id'],'attendance',json.dumps({'student_id':sid,'day':today}),now()))
        except sqlite3.IntegrityError: fail('Presença de hoje já registrada.',409)
        audit(c,user,'Presença registrada')
    return {'message':'Presença registrada.','id':record_id}

@app.get('/api/export')
def export(user=Depends(current)):
    with connection() as c: result={k:records(c,user,k) for k in sorted(KINDS|{'academies','attendance'})}
    return Response(json.dumps(result,ensure_ascii=False,indent=2),media_type='application/json',headers={'Content-Disposition':'attachment; filename=gorilazone-dados.json'})

@app.get('/api/{kind}')
def list_records(kind:str,user=Depends(current)):
    if kind not in KINDS: fail('Módulo inexistente.',404)
    with connection() as c: return records(c,user,kind)

@app.post('/api/{kind}',status_code=201)
def create(kind:str,data:dict,user=Depends(current)):
    rid=secrets.token_hex(16)
    with connection() as c:
        clean=validate(c,user,kind,data)
        c.execute('INSERT INTO records VALUES(?,?,?,?,?)',(rid,user['academy_id'],kind,json.dumps(clean,ensure_ascii=False),now())); audit(c,user,'Criado: '+kind)
    return {**clean,'id':rid}

@app.put('/api/{kind}/{rid}')
def update(kind:str,rid:str,data:dict,user=Depends(current)):
    with connection() as c:
        get_record(c,user,kind,rid); clean=validate(c,user,kind,data)
        c.execute('UPDATE records SET data=? WHERE id=? AND academy_id=?',(json.dumps(clean,ensure_ascii=False),rid,user['academy_id']));audit(c,user,'Atualizado: '+kind)
    return {**clean,'id':rid}

@app.delete('/api/{kind}/{rid}')
def delete(kind:str,rid:str,user=Depends(current)):
    if kind not in KINDS: fail('Módulo inexistente.',404)
    with connection() as c:
        get_record(c,user,kind,rid)
        for child in records(c,user,'enrollments')+records(c,user,'workouts')+records(c,user,'payments')+records(c,user,'assessments')+records(c,user,'attendance'):
            if child.get('student_id')==rid or child.get('plan_id')==rid: fail('Registro vinculado a outros dados. Remova os vínculos primeiro.',409)
        c.execute('DELETE FROM records WHERE id=? AND academy_id=?',(rid,user['academy_id']));audit(c,user,'Excluído: '+kind)
    return {'message':'Registro excluído.'}
