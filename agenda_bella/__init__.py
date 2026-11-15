import os
import secrets
import sqlite3
import time
from datetime import date, datetime, timedelta
from functools import wraps
from pathlib import Path

import click
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from .db import close_db, get_db, init_db
from . import services


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=os.environ.get('SECRET_KEY'), DATABASE=os.environ.get('DATABASE', str(Path(app.instance_path)/'agenda.sqlite')), SESSION_COOKIE_SECURE=True, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', MAX_CONTENT_LENGTH=65536)
    if config:
        app.config.update(config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('Defina SECRET_KEY no ambiente antes de iniciar.')
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    CSRFProtect(app)

    @app.template_filter('brl')
    def brl(value):
        return f'R$ {value/100:,.2f}'.replace(',', 'X').replace('.', ',').replace('X','.')

    @app.before_request
    def identify():
        g.user = None
        if session.get('uid'):
            user = get_db().execute('SELECT * FROM users WHERE id=?',(session['uid'],)).fetchone()
            now = int(time.time())
            if user and user['active'] and user['session_token'] and secrets.compare_digest(user['session_token'], session.get('token','')) and now-(user['last_seen'] or 0)<1800:
                g.user = user
                with get_db():
                    get_db().execute('UPDATE users SET last_seen=? WHERE id=?',(now,user['id']))
            else:
                session.clear()

    def protected(fn):
        @wraps(fn)
        def wrapper(*args,**kwargs):
            if not g.user:
                return redirect(url_for('login'))
            return fn(*args,**kwargs)
        return wrapper

    @app.after_request
    def headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='same-origin'
        response.headers['Cache-Control']='no-store'
        if request.is_secure:
            response.headers['Strict-Transport-Security']='max-age=31536000'
        return response

    @app.route('/login',methods=['GET','POST'])
    def login():
        error = None
        if request.method=='POST':
            db=get_db(); now=int(time.time())
            user=db.execute('SELECT * FROM users WHERE login=?',(request.form.get('login',''),)).fetchone()
            valid=user and user['active'] and now>=user['locked_until'] and check_password_hash(user['password_hash'],request.form.get('password',''))
            if valid:
                token=secrets.token_hex(32)
                with db:
                    db.execute('UPDATE users SET failures=0,locked_until=0,session_token=?,last_seen=? WHERE id=?',(token,now,user['id']))
                session.clear(); session.update(uid=user['id'],token=token)
                return redirect(url_for('index'))
            if user and now>=user['locked_until']:
                failures=user['failures']+1 if user['locked_until']==0 else 1
                with db:
                    db.execute('UPDATE users SET failures=?,locked_until=? WHERE id=?',(failures, now+900 if failures>=5 else 0,user['id']))
            error='Não foi possível entrar. Confira os dados ou tente novamente mais tarde.'
        return render_template('login.html',error=error)

    @app.post('/logout')
    @protected
    def logout():
        with get_db():
            get_db().execute('UPDATE users SET session_token=NULL WHERE id=?',(g.user['id'],))
        session.clear()
        return redirect(url_for('login'))

    @app.get('/')
    @protected
    def index():
        return render_template('index.html')

    @app.route('/clients',methods=['GET','POST'])
    @protected
    def clients():
        error=None
        if request.method=='POST':
            try:
                services.create_client(request.form)
                flash('Cliente cadastrada.','success')
                return redirect(url_for('clients'))
            except services.ValidationError as exc:
                error=str(exc)
        q=request.args.get('q','')[:150]
        rows=get_db().execute('SELECT * FROM clients WHERE active=1 AND (name LIKE ? OR phone LIKE ?) ORDER BY name LIMIT 100',('%'+q+'%','%'+q+'%')).fetchall()
        return render_template('clients.html',rows=rows,error=error,q=q)

    @app.route('/appointments/new',methods=['GET','POST'])
    @app.route('/appointments/<int:item_id>/edit',methods=['GET','POST'])
    @protected
    def appointment(item_id=None):
        db=get_db(); error=None
        data=dict(request.form) if request.method=='POST' else {}
        if item_id and request.method=='GET':
            row=db.execute("SELECT * FROM appointments WHERE id=? AND status='agendado'",(item_id,)).fetchone()
            if not row: abort(404)
            data=dict(row); data['amount']=f"{row['amount']/100:.2f}"
        if request.method=='POST':
            try:
                services.create_appointment(data,g.user['id'],item_id)
                flash('Atendimento atualizado.' if item_id else 'Atendimento agendado.','success')
                return redirect(url_for('agenda',day=data['start'][:10]))
            except services.ValidationError as exc:
                error=str(exc)
        rows=db.execute('SELECT id,name FROM clients WHERE active=1 ORDER BY name').fetchall()
        return render_template('appointment.html',data=data,clients=rows,error=error,editing=item_id is not None)

    @app.get('/agenda')
    @protected
    def agenda():
        day=request.args.get('day',date.today().isoformat())
        try: current=date.fromisoformat(day)
        except ValueError: abort(400)
        end=(current+timedelta(days=1)).isoformat()
        rows=get_db().execute('SELECT a.*,c.name,p.id AS payment_id FROM appointments a JOIN clients c ON c.id=a.client_id LEFT JOIN payments p ON p.appointment_id=a.id WHERE a.start>=? AND a.start<? ORDER BY a.start',(day,end)).fetchall()
        blocks=get_db().execute('SELECT * FROM blocks WHERE start>=? AND start<? ORDER BY start',(day,end)).fetchall()
        return render_template('agenda.html',rows=rows,blocks=blocks,day=day)

    @app.post('/appointments/<int:item_id>/<action>')
    @protected
    def update(item_id,action):
        db=get_db()
        try:
            if action=='pay': services.pay(item_id)
            elif action in ('cancel','complete'):
                with db:
                    row=db.execute('SELECT * FROM appointments WHERE id=?',(item_id,)).fetchone()
                    if not row or row['status']!='agendado': raise services.ValidationError('Atendimento não pode ser alterado.')
                    if action=='cancel' and db.execute('SELECT id FROM payments WHERE appointment_id=?',(item_id,)).fetchone(): raise services.ValidationError('Não é possível cancelar um atendimento pago.')
                    if action=='complete' and row['end']>datetime.now().isoformat(timespec='minutes'): raise services.ValidationError('Aguarde o término previsto para concluir.')
                    db.execute('UPDATE appointments SET status=? WHERE id=?',('cancelado' if action=='cancel' else 'concluido',item_id))
            else: abort(404)
            flash('Operação concluída.','success')
        except services.ValidationError as exc: flash(str(exc),'error')
        return redirect(url_for('agenda',day=request.form.get('day',date.today().isoformat())))

    @app.route('/blocks',methods=['GET','POST'])
    @protected
    def blocks():
        error=None
        if request.method=='POST':
            try:
                services.create_block(request.form)
                flash('Intervalo reservado.','success')
                return redirect(url_for('agenda',day=request.form['start'][:10]))
            except services.ValidationError as exc: error=str(exc)
        return render_template('blocks.html',error=error)

    @app.post('/blocks/<int:item_id>/delete')
    @protected
    def delete_block(item_id):
        with get_db(): get_db().execute('DELETE FROM blocks WHERE id=?',(item_id,))
        flash('Intervalo removido.','success')
        return redirect(url_for('agenda',day=request.form.get('day',date.today().isoformat())))

    @app.get('/payments')
    @protected
    def payments():
        start=request.args.get('start',date.today().replace(day=1).isoformat())
        end=request.args.get('end',date.today().isoformat())
        try:
            if date.fromisoformat(start)>date.fromisoformat(end): raise ValueError
            until=(date.fromisoformat(end)+timedelta(days=1)).isoformat()
        except ValueError: abort(400)
        rows=get_db().execute('SELECT p.*,c.name FROM payments p JOIN appointments a ON a.id=p.appointment_id JOIN clients c ON c.id=a.client_id WHERE received_at>=? AND received_at<? ORDER BY received_at',(start,until)).fetchall()
        pending=get_db().execute("SELECT a.*,c.name FROM appointments a JOIN clients c ON c.id=a.client_id LEFT JOIN payments p ON p.appointment_id=a.id WHERE a.status!='cancelado' AND p.id IS NULL ORDER BY a.start LIMIT 100").fetchall()
        return render_template('payments.html',rows=rows,pending=pending,total=sum(r['amount'] for r in rows),start=start,end=end)

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(413)
    def client_error(error):
        return render_template('error.html',message='Não foi possível processar a solicitação. Confira os dados e tente novamente.'),error.code

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', message='Não foi possível concluir a operação. Tente novamente mais tarde.'), 500

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        get_db().rollback()
        app.logger.error('Falha de persistência: %s',type(error).__name__)
        return render_template('error.html',message='Não foi possível confirmar o salvamento. Consulte a agenda antes de tentar novamente.'),503

    @app.cli.command('init-db')
    def initialize():
        init_db(); click.echo('Banco inicializado.')

    @app.cli.command('create-user')
    @click.option('--login',prompt=True)
    @click.password_option()
    def user_command(login,password):
        if len(password)<15: raise click.ClickException('Use pelo menos 15 caracteres na senha.')
        with get_db(): get_db().execute('INSERT INTO users(login,password_hash) VALUES (?,?)',(services.text(login,'Login',80),generate_password_hash(password,method='scrypt')))
        click.echo('Conta criada. Nenhuma senha foi gravada em texto limpo.')

    @app.cli.command('backup')
    @click.argument('destination')
    def backup(destination):
        target=Path(destination)
        if target.exists(): raise click.ClickException('Escolha um arquivo novo para o backup.')
        with sqlite3.connect(target) as out: get_db().backup(out)
        os.chmod(target,0o600)
        click.echo('Backup criado. Guarde uma cópia fora do servidor.')

    return app
