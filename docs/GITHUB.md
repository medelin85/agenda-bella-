# Publicar e criar Pull Request

O repositório remoto precisa ter um commit na branch principal antes de abrir um PR de outra branch. Não declarar PR ou CI como realizados sem seus links e resultados reais.

## Opção sem terminal: upload
1. Abra https://github.com/medelin85/agenda-bella- . Se estiver vazio, crie um README simples para inicializar a branch principal.
2. Na página do repositório, selecione Add file → Upload files.
3. Extraia o ZIP do projeto e envie o conteúdo da pasta, incluindo a pasta `.github` (ative a exibição de arquivos ocultos se necessário). Não envie o ZIP inteiro como único arquivo: o GitHub precisa dos arquivos extraídos para executar a CI.
4. Selecione criar uma nova branch, nome `feature/mvp-agenda-bella`, e abra o Pull Request.
5. Em Actions, confira o workflow. Em Files changed, faça revisão técnica e registre observações verdadeiras. Se a disciplina exigir outro revisor, convide a pessoa autorizada.
6. Corrija os problemas encontrados na mesma branch, aguarde a CI e faça o merge quando aprovado.

## Opção terminal, com GitHub autenticado
Clone o repositório, inicialize a branch principal com README se ele estiver vazio, depois crie a branch de implementação e copie os arquivos do pacote. Use `git add .`, `git commit` e `git push` para enviar a branch. Abra PR para a branch principal e confira Actions. Nunca inclua `.env`, bancos ou backups.

## Texto sugerido para o PR
Implementa o Agenda Bella para centralizar clientes, agendamentos e pagamentos. Inclui autenticação, bloqueios de deslocamento, prevenção de conflitos, interface responsiva e testes unitários/de integração, com CI em GitHub Actions.

Validação: executar pytest e auditoria de dependências. Validação externa em duas rodadas ainda pendente; formulários de coleta em docs/VALIDACAO_CAMPO.md.
