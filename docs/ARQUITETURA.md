# Estrutura e decisões

Aplicação monolítica em camadas. `templates/` e `static/` apresentam a interface; rotas em `__init__.py` verificam a sessão e encaminham operações; `services.py` aplica as regras; `db.py` administra conexões; `schema.sql` define a persistência.

## Modelo
- users 1:N appointments; inclui hash, token revogável, último acesso e contador de falhas.
- clients 1:N appointments; nome e telefone, sem CPF.
- appointments 1:0..1 payments, com unicidade do vínculo de quitação.
- blocks representa indisponibilidade independente de cliente.

Datas são texto ISO no horário local de operação e valores são inteiros em centavos. O MVP se destina a uma profissional em um único fuso local; agenda internacional não é suportada. Atendimentos devem começar e terminar no mesmo dia.

A validação de conflitos e a gravação ocorrem em transação BEGIN IMMEDIATE: duas solicitações não devem inserir períodos conflitantes entre a consulta e a gravação. Intervalos consecutivos são permitidos. Cancelados não bloqueiam horários; recebimentos não podem se repetir. A aplicação exige autenticação em todas as rotas de negócio e tokens CSRF nos POSTs.

O endereço pertence ao atendimento domiciliar; local fixo não exige endereço. Não coletamos CPF, documentos ou dados bancários. Clientes inativas não podem receber novo agendamento, mas inativação por interface não faz parte desta entrega. O login é criado por comando administrativo e não há cadastro público ou recuperação automática de senha.

## Limitações
Sem modo offline, notificações automáticas, estorno/correção de pagamento pela interface ou gestão de equipes. A expiração é de 30 minutos de inatividade e há uma sessão ativa por conta. O bloqueio após cinco falhas dura 15 minutos e é persistido; endurecimento por IP e proteção de infraestrutura devem ser avaliados para exposição pública ampla. É necessário proxy HTTPS e disco persistente.

## Relação com os requisitos
RF01: cadastro em /clients. RF02: /appointments/new. RF03: /agenda. RF04 desejável: /payments. Bloqueios, edição, conclusão, cancelamento e recebimento possuem fluxos explícitos como complementos. RNF01/02: sessões, scrypt, CSRF, validações, SQL parametrizado e CSP. RNF03: portabilidade por Python 3.12 e Gunicorn; meta de rede móvel ainda depende de medição no ambiente alvo. RNF04: labels, foco, skip link, controles de 48px, mensagens por texto e símbolo; avaliação com público e leitor de tela permanece necessária.
