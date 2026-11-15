# Verificação técnica e validação em campo

## Executado localmente
Consulte `test-results.xml` para os testes automatizados desta entrega. São testes unitários de valores, períodos e texto, e testes de integração de autenticação, revogação da sessão, expiração, bloqueio de tentativas, CSRF, cadastro, agenda, conflitos, bloqueios, cancelamento, pagamento único, cabeçalhos e backup. O resultado local não substitui a execução do GitHub Actions.

## Ainda precisa de execução humana
Realizar duas rodadas com a representante externa; não existem resultados de campo nesta entrega. A segunda deve usar ajustes concretos obtidos na primeira. Obter consentimento, usar dados fictícios e registrar apenas o necessário.

Duração de 20 a 30 minutos, no celular da participante. Apresentar objetivos sem indicar controles. Cronometrar após a leitura; esclarecimentos não pausam. Registrar ajuda, erros corrigidos, resultado e opinião separadamente.

1. Localizar o início de novo atendimento a partir do menu.
2. Agendar Ana Exemplo, manicure domiciliar em uma data fictícia combinada, das 14h às 15h, R$30, endereço Rua Fictícia, 100; iniciar sem compromisso conflitante.
3. Conferir confirmação e informações na agenda e identificar como continuar, explicando texto e símbolo de confirmação.

Critérios: 3/3 tarefas corretas sem ajuda (100%); tarefa 2 em até 180s; nota mínima 4/5 à pergunta: “Como você avalia a facilidade de navegar pelas telas e compreender as ações disponíveis?”, de 1 Muito difícil a 5 Muito fácil. Resultados incorretos são falha. Intervenções são sucesso com ajuda, sem contar no sucesso independente. Cada rodada tem resultados separados.

Falha crítica, perda de informação, alerta inacessível ou critério não atendido exige correção e novo teste. Somente ajustes cosméticos não bloqueantes permitem aceite com ajustes. Não compensar dificuldade por velocidade ou nota alta.

## Desempenho RNF03
Ainda não medido em rede móvel real. Preparar 100 clientes e 1.000 atendimentos fictícios, sendo 20 na data selecionada. Celular Android 2GB RAM, viewport de 360 CSS px ou emulação identificada. Usar DevTools/CDP com 1,6Mbps download, 750Kbps upload, latência 150ms, cache desativado. Aquecer uma vez, medir cinco navegações com API Performance até lista exibida e exigir mediana <=3s. Guardar versão, ambiente, rede, tempos individuais, mediana e capturas. Testar reinicialização sem perda de dados e instalação limpa. Repetir condições após otimizações.

## Acessibilidade
Conferir mínimo 44x44 CSS px (CSS usa 48px), contraste de texto 4,5:1 e elementos essenciais 3:1, ampliação 200%, foco visível, percurso por teclado, anúncio de erros e labels. Não declarar conformidade integral com WCAG apenas por inspeção visual.
