"""Valida fluxo real em uma base temporária, sem alterar dados da instalação."""
import os,tempfile
from pathlib import Path
from datetime import date,timedelta
with tempfile.TemporaryDirectory() as tmp:
    os.environ['GORILA_DB']=str(Path(tmp)/'test.db')
    from fastapi.testclient import TestClient
    from app.main import app
    c=TestClient(app)
    def create_account(email):
        r=c.post('/api/auth/register',json={'name':'Teste','email':email,'password':'SenhaTeste1234','academy_name':'Unidade de teste'})
        assert r.status_code==201,r.text
        login=c.post('/api/auth/login',json={'email':email,'password':'SenhaTeste1234'})
        assert login.status_code==200,login.text
        data=login.json()
        return {'Authorization':'Bearer '+data['access_token']},data['user']
    h,u=create_account('um@teste.local'); other,_=create_account('dois@teste.local')
    assert c.get('/api/students').status_code==401
    def post(kind,data):
        r=c.post('/api/'+kind,json=data,headers=h)
        assert r.status_code==201,r.text
        return r.json()
    s=post('students',{'name':'Aluno teste','email':'aluno@teste.local'})
    p=post('plans',{'name':'Mensal','price':100})
    assert c.get('/api/students',headers=other).json()==[]
    assert c.put('/api/students/'+s['id'],headers=other,json={'name':'Invasão','email':'x@x.com'}).status_code==404
    payload={'student_id':s['id'],'qr_code':'GORILAZONE:ACADEMY:'+u['academy_id']}
    assert c.post('/api/attendance/check-in',headers=h,json=payload).status_code==400
    post('enrollments',{'student_id':s['id'],'plan_id':p['id'],'start_date':date.today().isoformat(),'end_date':(date.today()+timedelta(days=30)).isoformat(),'status':'ativa'})
    assert c.post('/api/attendance/check-in',headers=h,json={**payload,'qr_code':'falso'}).status_code==400
    assert c.post('/api/attendance/check-in',headers=h,json=payload).status_code==201
    assert c.post('/api/attendance/check-in',headers=h,json=payload).status_code==409
    assert c.get('/api/attendance/qr-code',headers=h).content.startswith(b'\x89PNG')
    payment=post('payments',{'student_id':s['id'],'amount':100,'due_date':date.today().isoformat(),'status':'pendente'})
    assert c.get('/api/dashboard',headers=h).json()['pending']==100
    r=c.put('/api/payments/'+payment['id'],headers=h,json={**payment,'status':'pago'})
    assert r.status_code==200,r.text
    post('workouts',{'student_id':s['id'],'title':'Treino A','exercises':'Supino 3x12'})
    post('assessments',{'student_id':s['id'],'date':date.today().isoformat(),'weight':70,'notes':'Avaliação inicial'})
    post('notifications',{'title':'Aviso teste','message':'Horário de treino'})
    dashboard=c.get('/api/dashboard',headers=h).json()
    assert dashboard['paid']==100 and dashboard['attendance_today']==1 and dashboard['active_enrollments']==1
    assert c.delete('/api/students/'+s['id'],headers=h).status_code==409
    assert c.get('/api/export',headers=h).json()['students'][0]['name']=='Aluno teste'
    assert c.post('/api/contact',json={'name':'Pessoa teste','email':'contato@teste.local','message':'Quero conhecer','consent':True}).status_code==201
    assert c.post('/api/auth/login',json={'email':'um@teste.local','password':'errada'}).status_code==401
    assert c.post('/api/auth/logout',headers=h).status_code==200
    assert c.get('/api/auth/me',headers=h).status_code==401
    print('OK: autenticação, isolamento, vínculos, módulos, QR, duplicação, financeiro, exportação, contato e logout.')
