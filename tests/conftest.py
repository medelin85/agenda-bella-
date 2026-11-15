import pytest
from werkzeug.security import generate_password_hash
from agenda_bella import create_app
from agenda_bella.db import get_db, init_db

@pytest.fixture
def app(tmp_path):
    app=create_app({'TESTING':True,'SECRET_KEY':'test-only-key','DATABASE':str(tmp_path/'test.sqlite'),'SESSION_COOKIE_SECURE':False,'WTF_CSRF_ENABLED':False})
    with app.app_context():
        init_db()
        with get_db():
            get_db().execute('INSERT INTO users(login,password_hash) VALUES (?,?)',('marina',generate_password_hash('senha ficticia longa')))
            get_db().execute('INSERT INTO clients(name,phone) VALUES (?,?)',('Ana Exemplo','11999990000'))
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def logged(client):
    client.post('/login',data={'login':'marina','password':'senha ficticia longa'})
    return client

@pytest.fixture
def appointment_data():
    return dict(client_id='1',service='Manicure',start='2026-10-20T14:00',end='2026-10-20T15:00',amount='30,00',location='domiciliar',address='Rua Fictícia, 100')
