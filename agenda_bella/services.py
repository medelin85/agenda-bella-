from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

from .db import get_db


class ValidationError(ValueError):
    pass


def text(value, label, maximum=150):
    value = (value or '').strip()
    if not value or len(value) > maximum or '<' in value or '>' in value:
        raise ValidationError(f'{label}: preencha um texto válido, sem HTML, com até {maximum} caracteres.')
    return value


def period(start, end):
    try:
        a, b = datetime.fromisoformat(start), datetime.fromisoformat(end)
    except (ValueError, TypeError):
        raise ValidationError('Informe data e horários válidos.')
    if a.tzinfo or b.tzinfo or b <= a or a.date() != b.date():
        raise ValidationError('O término deve ser posterior ao início, no mesmo dia.')
    return a.isoformat(timespec='minutes'), b.isoformat(timespec='minutes')


def money(value):
    try:
        number = Decimal(str(value).replace(',', '.'))
        if not number.is_finite() or number < 0 or number > 999999 or number != number.quantize(Decimal('.01')):
            raise InvalidOperation
        return int(number * 100)
    except (InvalidOperation, ValueError):
        raise ValidationError('Informe um valor não negativo com até duas casas decimais.')


def create_client(data):
    name = text(data.get('name'), 'Nome')
    phone = text(data.get('phone'), 'Telefone', 25)
    if not re.fullmatch(r'[0-9()+ .-]{8,25}', phone):
        raise ValidationError('Informe um telefone válido com 8 a 25 caracteres.')
    db = get_db()
    with db:
        return db.execute('INSERT INTO clients(name,phone) VALUES (?,?)', (name, phone)).lastrowid


def conflict(db, start, end, exclude=-1):
    return db.execute("SELECT id FROM appointments WHERE status!='cancelado' AND id!=? AND start<? AND end>? LIMIT 1", (exclude,end,start)).fetchone() or db.execute('SELECT id FROM blocks WHERE start<? AND end>? LIMIT 1', (end,start)).fetchone()


def create_appointment(data, user_id, appointment_id=None):
    start, end = period(data.get('start'), data.get('end'))
    service = text(data.get('service'), 'Serviço', 100)
    amount = money(data.get('amount'))
    location = data.get('location')
    if location not in ('fixo', 'domiciliar'):
        raise ValidationError('Selecione o local do atendimento.')
    address = text(data.get('address'), 'Endereço', 250) if location == 'domiciliar' else ''
    try:
        client_id = int(data.get('client_id', ''))
    except (ValueError, TypeError):
        raise ValidationError('Selecione uma cliente cadastrada.')
    db = get_db()
    try:
        db.execute('BEGIN IMMEDIATE')
        if not db.execute('SELECT id FROM clients WHERE id=? AND active=1', (client_id,)).fetchone():
            raise ValidationError('Selecione uma cliente ativa.')
        if appointment_id is not None:
            old = db.execute("SELECT id FROM appointments WHERE id=? AND status='agendado'", (appointment_id,)).fetchone()
            if not old:
                raise ValidationError('Somente atendimentos agendados podem ser editados.')
        if conflict(db,start,end,appointment_id or -1):
            raise ValidationError('Horário indisponível. Escolha outro período.')
        values = (client_id,user_id,service,start,end,amount,location,address)
        if appointment_id is None:
            result = db.execute('INSERT INTO appointments(client_id,user_id,service,start,end,amount,location,address) VALUES (?,?,?,?,?,?,?,?)', values).lastrowid
        else:
            db.execute('UPDATE appointments SET client_id=?,user_id=?,service=?,start=?,end=?,amount=?,location=?,address=? WHERE id=?', values+(appointment_id,))
            result = appointment_id
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def create_block(data):
    start,end = period(data.get('start'),data.get('end'))
    reason = text(data.get('reason'), 'Motivo',100)
    db = get_db()
    try:
        db.execute('BEGIN IMMEDIATE')
        if conflict(db,start,end):
            raise ValidationError('O bloqueio conflita com um compromisso existente.')
        db.execute('INSERT INTO blocks(start,end,reason) VALUES (?,?,?)',(start,end,reason))
        db.commit()
    except Exception:
        db.rollback()
        raise


def pay(appointment_id):
    db = get_db()
    try:
        db.execute('BEGIN IMMEDIATE')
        item = db.execute('SELECT * FROM appointments WHERE id=?',(appointment_id,)).fetchone()
        if not item or item['status']=='cancelado':
            raise ValidationError('Atendimento indisponível para pagamento.')
        if db.execute('SELECT id FROM payments WHERE appointment_id=?',(appointment_id,)).fetchone():
            raise ValidationError('Este atendimento já foi pago.')
        db.execute('INSERT INTO payments(appointment_id,amount,received_at) VALUES (?,?,?)',(appointment_id,item['amount'],datetime.now().isoformat(timespec='seconds')))
        db.commit()
    except Exception:
        db.rollback()
        raise
