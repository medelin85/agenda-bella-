# Agenda Bella

MVP web de gestão de atendimentos de manicure, implementado em Python, Flask e SQLite. Interface responsiva em português, com visual inspirado no protótipo das experiências anteriores.

## Funcionalidades implementadas

- Login da profissional, senha com hash scrypt, sessão com expiração por inatividade e revogação no logout.
- Cadastro e busca de clientes.
- Agenda por data, cadastro e edição de atendimentos e verificação de sobreposição.
- Intervalos de deslocamento, cancelamento com preservação do histórico e conclusão de serviços.
- Registro de pagamento integral, prevenção de quitação duplicada, pendências e resumo por período.
- Validação no servidor, consultas parametrizadas, escape de HTML, CSP e proteção CSRF.

O primeiro fluxo obrigatório é clientes → agendamento → agenda. Bloqueios e pagamentos foram implementados como complementos previstos na modelagem. Não há integração automática com WhatsApp, pagamento online, vários profissionais ou modo offline.

## Executar localmente

Requer Python 3.12. No terminal, dentro da pasta do projeto:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Configure a chave secreta e permita cookie HTTP somente no desenvolvimento local:

Linux/macOS:
```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
flask --app agenda_bella init-db
flask --app agenda_bella create-user
flask --app 'agenda_bella:create_app({"SESSION_COOKIE_SECURE":False})' run
```

Windows PowerShell:
```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
flask --app agenda_bella init-db
flask --app agenda_bella create-user
python run_local.py
```

A conta é criada por comando interativo; escolha sua senha com pelo menos 15 caracteres. Não existe senha padrão. Abra http://127.0.0.1:5000. O comando `init-db` cria tabelas ausentes sem apagar registros.

## Testes

```bash
python -m pytest -v --junitxml=test-results.xml
pip-audit -r requirements.txt
```

Os testes usam banco temporário e dados fictícios. Veja `docs/TESTES.md` para limites e roteiro de validação humana. O arquivo `.github/workflows/ci.yml` executa testes e auditoria em pushes e Pull Requests. Só será possível comprovar uma execução de CI após publicar no GitHub e consultar seu resultado em Actions.

## Implantação Linux

1. Instale dependências de `requirements.txt` em ambiente virtual.
2. Configure `SECRET_KEY` com valor aleatório e estável; configure `DATABASE` para um caminho em disco persistente com permissão restrita.
3. Execute `flask --app agenda_bella init-db` e `create-user` uma única vez.
4. Execute `gunicorn --workers 1 --threads 2 --bind 127.0.0.1:8000 'agenda_bella:create_app()'` atrás de proxy HTTPS. Em plataforma gerenciada, use o bind/PORT exigido pela hospedagem, sem expor HTTP diretamente ao público.
5. Mantenha `SESSION_COOKIE_SECURE=True`, debug desativado e instância única.

Não há hospedagem já contratada/publicada. Planos gratuitos podem suspender o serviço e não oferecer disco persistente: confirme isso antes de usar. O SQLite fica no servidor, não no celular. Falta de internet impede o uso. Para concorrência elevada ou múltiplas instâncias, migre para PostgreSQL.

## Backup

```bash
flask --app agenda_bella backup /caminho/privado/backup-2026-11-15.sqlite
```

Agende diariamente, copie para armazenamento privado fora do servidor e teste a restauração em ambiente separado. Nunca envie banco, backups, senhas, `.env` ou dados de clientes ao GitHub. Para restaurar, pare a aplicação, preserve o arquivo atual e substitua o banco por uma cópia válida, mantendo permissões restritas.

## GitHub e Pull Request

O repositório de destino informado é https://github.com/medelin85/agenda-bella- . Consulte `docs/GITHUB.md`. O código local e a configuração de CI não são, por si, prova de publicação, revisão por PR ou validação de campo.
