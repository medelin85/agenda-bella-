import pytest
from prepare_production import prepare
from agenda_bella.db import get_db


def test_health_without_login(client):
    response=client.get('/health')
    assert response.status_code==200
    assert response.json=={'status':'ok'}


def test_health_missing_schema(app,client):
    with app.app_context():
        with get_db(): get_db().execute('DROP TABLE users')
    assert client.get('/health').status_code==503


def test_bootstrap_idempotent(tmp_path,monkeypatch):
    path=str(tmp_path/'data'/'prod.sqlite')
    monkeypatch.setenv('DATABASE',path)
    monkeypatch.setenv('SECRET_KEY','test-only-key')
    monkeypatch.setenv('ADMIN_LOGIN','responsavel')
    monkeypatch.setenv('ADMIN_PASSWORD','senha ficticia de teste')
    prepare(); prepare()
    import sqlite3
    with sqlite3.connect(path) as db:
        rows=db.execute('SELECT password_hash FROM users').fetchall()
        assert len(rows)==1 and rows[0][0].startswith('scrypt:')


def test_bootstrap_rejects_short_password(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE',str(tmp_path/'prod.sqlite'))
    monkeypatch.setenv('SECRET_KEY','test-only-key')
    monkeypatch.setenv('ADMIN_LOGIN','responsavel')
    monkeypatch.setenv('ADMIN_PASSWORD','curta')
    with pytest.raises(RuntimeError): prepare()
