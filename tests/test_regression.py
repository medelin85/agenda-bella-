"""Regressões para preservar histórico e limites financeiros."""
from datetime import datetime,timedelta
from agenda_bella.db import get_db


def test_paid_appointment_cannot_be_cancelled(logged,appointment_data,app):
    logged.post('/appointments/new',data=appointment_data)
    logged.post('/appointments/1/pay',data={})
    response=logged.post('/appointments/1/cancel',data={'day':'2026-10-20'},follow_redirects=True)
    assert 'Não é possível cancelar um atendimento pago' in response.text
    with app.app_context():
        assert get_db().execute('SELECT status FROM appointments WHERE id=1').fetchone()[0]=='agendado'
        assert get_db().execute('SELECT COUNT(*) FROM payments').fetchone()[0]==1


def test_future_appointment_cannot_be_completed(logged,appointment_data,app):
    day=(datetime.now()+timedelta(days=30)).date().isoformat()
    data={**appointment_data,'start':day+'T14:00','end':day+'T15:00'}
    logged.post('/appointments/new',data=data)
    response=logged.post('/appointments/1/complete',data={'day':day},follow_redirects=True)
    assert 'Aguarde o término previsto' in response.text
    with app.app_context():
        assert get_db().execute('SELECT status FROM appointments').fetchone()[0]=='agendado'


def test_payment_summary_includes_final_day(logged,appointment_data,app):
    logged.post('/appointments/new',data=appointment_data)
    logged.post('/appointments/1/pay',data={})
    with app.app_context():
        with get_db():
            get_db().execute("UPDATE payments SET received_at='2026-10-31T23:59:59'")
    response=logged.get('/payments?start=2026-10-01&end=2026-10-31')
    assert 'Total recebido: R$ 30,00' in response.text
    assert 'Total recebido: R$ 0,00' in logged.get('/payments?start=2026-11-01&end=2026-11-30').text


def test_invalid_date_returns_safe_error(logged):
    response=logged.get('/agenda?day=data-invalida')
    assert response.status_code==400
    assert 'Traceback' not in response.text
    assert 'Não foi possível processar' in response.text
