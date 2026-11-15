# Demonstração gratuita no Render

Autorizada pelo usuário para avaliação acadêmica, sem contratação de plano pago.

Aplicação Python/Flask com Gunicorn, SQLite temporário em /tmp/agenda-bella/agenda.sqlite e HTTPS. DEMO_MODE=true apresenta aviso em todas as telas: somente dados fictícios e registros sujeitos a perda em reinício/hibernação. O plano gratuito hiberna após 15 minutos sem tráfego e pode demorar cerca de um minuto para retornar. A franquia gratuita é compartilhada com outros serviços da conta.

Esta demonstração não oferece persistência de produção e não deve ser descrita como implantação durável. Nenhum dado local foi importado.

A inicialização cria tabelas e uma conta apenas quando não existe usuário. ADMIN_LOGIN e ADMIN_PASSWORD são definidos no ambiente, nunca no código. A senha usa hash scrypt. SECRET_KEY é configurado fora do repositório.

GET /health verifica acesso à tabela users: 200 para saudável, 503 para falha. Logs registram endpoint, status e duração, sem formulários, senhas ou dados de clientes. Monitoramento de disponibilidade e resultados deve ser documentado após medir.

Build: pip install -r requirements.txt. Start: sh start_production.sh. Executar uma única instância. Para produção real, será necessário disco persistente ou migração para banco externo.
