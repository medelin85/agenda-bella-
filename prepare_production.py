"""Inicialização idempotente, executada no runtime após montar o disco."""
import os
from pathlib import Path

from werkzeug.security import generate_password_hash
from agenda_bella import create_app
from agenda_bella.db import get_db, init_db


def prepare():
    database = os.environ.get('DATABASE')
    if not database:
        raise RuntimeError('Defina DATABASE em armazenamento persistente.')
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    app = create_app()
    with app.app_context():
        init_db()
        db = get_db()
        if not db.execute('SELECT id FROM users LIMIT 1').fetchone():
            login = os.environ.get('ADMIN_LOGIN', '').strip()
            password = os.environ.get('ADMIN_PASSWORD', '')
            if not login or len(password) < 15:
                raise RuntimeError('Configure ADMIN_LOGIN e ADMIN_PASSWORD com pelo menos 15 caracteres na senha.')
            with db:
                db.execute('INSERT INTO users(login,password_hash) VALUES (?,?)', (login,generate_password_hash(password,method='scrypt')))
    # Não imprimir senha, hash ou variáveis secretas.


if __name__ == '__main__':
    prepare()
