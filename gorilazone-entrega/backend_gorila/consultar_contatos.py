from app.main import connection
import json
with connection() as c:
    rows=c.execute('SELECT data,created FROM leads ORDER BY created DESC').fetchall()
for r in rows:
    print(r['created'],json.dumps(json.loads(r['data']),ensure_ascii=False))
if not rows: print('Nenhuma solicitação recebida.')
