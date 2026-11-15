"""Somente para desenvolvimento local; não usar na hospedagem pública."""
from agenda_bella import create_app

if __name__ == '__main__':
    create_app({'SESSION_COOKIE_SECURE': False}).run(host='127.0.0.1', port=5000)
