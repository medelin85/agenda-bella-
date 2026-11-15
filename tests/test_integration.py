from agenda_bella.db import get_db


def test_protected_routes(client):
    for path in ['/','/clients','/agenda','/appointments/new','/blocks','/payments']:
        assert client.get(path).status_code==302
    assert client.post('/appointments/new',data={}).status_code==302


def test_login_and_revoked_logout(logged,app):
    old=logged.get_cookie('session').value
    assert logged.get('/').status_code==200
    logged.post('/logout')
    logged.set_cookie('session',old)
    assert logged.get('/').status_code==302
    with app.app_context():
        row=get_db().execute('SELECT * FROM users').fetchone()
        assert row['password_hash'].startswith('scrypt:')
        assert 'senha ficticia longa' not in row['password_hash']


def test_lockout(client):
    for _ in range(5): client.post('/login',data={'login':'marina','password':'wrong'})
    response=client.post('/login',data={'login':'marina','password':'senha ficticia longa'})
    assert response.status_code==200
    assert client.get('/').status_code==302


def test_full_flow(logged,appointment_data,app):
    response=logged.post('/clients',data={'name':'Bia Fictícia','phone':'11999998888'},follow_redirects=True)
    assert 'Cliente cadastrada' in response.text
    response=logged.post('/appointments/new',data=appointment_data,follow_redirects=True)
    assert 'Atendimento agendado' in response.text
    assert 'Ana Exemplo' in response.text
    assert 'Rua Fictícia' in response.text
    assert logged.post('/appointments/1/pay',data={'day':'2026-10-20'}).status_code==302
    response=logged.post('/appointments/1/pay',data={'day':'2026-10-20'},follow_redirects=True)
    assert 'já foi pago' in response.text
    with app.app_context(): assert get_db().execute('SELECT COUNT(*) FROM payments').fetchone()[0]==1
    assert logged.get('/payments?start=2026-01-01&end=2027-12-31').status_code==200


def test_overlap_and_adjacent(logged,appointment_data,app):
    logged.post('/appointments/new',data=appointment_data)
    response=logged.post('/appointments/new',data=appointment_data)
    assert 'Horário indisponível' in response.text
    adjacent={**appointment_data,'start':'2026-10-20T15:00','end':'2026-10-20T16:00'}
    assert logged.post('/appointments/new',data=adjacent).status_code==302
    assert logged.post('/appointments/1/edit',data=appointment_data).status_code==302
    with app.app_context(): assert get_db().execute('SELECT COUNT(*) FROM appointments').fetchone()[0]==2


def test_blocks_and_cancel(logged,appointment_data):
    logged.post('/blocks',data={'start':'2026-10-20T14:00','end':'2026-10-20T15:00','reason':'Deslocamento'})
    assert 'Horário indisponível' in logged.post('/appointments/new',data=appointment_data).text
    logged.post('/blocks/1/delete',data={'day':'2026-10-20'})
    logged.post('/appointments/new',data=appointment_data)
    logged.post('/appointments/1/cancel',data={'day':'2026-10-20'})
    assert logged.post('/appointments/new',data=appointment_data).status_code==302


def test_invalid_client_address_and_injection(logged,appointment_data,app):
    for changes in [{'client_id':'999'},{'address':''},{'service':'<script>alert(1)</script>'}]:
        assert logged.post('/appointments/new',data={**appointment_data,**changes}).status_code==200
    logged.post('/clients',data={'name':"Ana'); DROP TABLE clients;--",'phone':'11999990000'})
    assert logged.get('/clients?q=%27%20OR%201=1--').status_code==200
    with app.app_context(): assert get_db().execute('SELECT COUNT(*) FROM clients').fetchone()[0]==2


def test_csrf_and_headers(app):
    app.config['WTF_CSRF_ENABLED']=True
    client=app.test_client()
    assert client.post('/login',data={'login':'marina','password':'senha ficticia longa'}).status_code==400
    response=client.get('/login')
    assert "default-src 'self'" in response.headers['Content-Security-Policy']
    assert response.headers['Cache-Control']=='no-store'


def test_expired_session(logged,app):
    with app.app_context():
        with get_db(): get_db().execute('UPDATE users SET last_seen=0')
    assert logged.get('/agenda').status_code==302


def test_backup_and_persistence(app,tmp_path):
    backup=tmp_path/'backup.sqlite'
    assert app.test_cli_runner().invoke(args=['backup',str(backup)]).exit_code==0
    import sqlite3
    with sqlite3.connect(backup) as db: assert db.execute('SELECT COUNT(*) FROM clients').fetchone()[0]==1
