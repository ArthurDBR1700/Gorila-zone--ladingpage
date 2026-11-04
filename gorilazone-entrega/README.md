# GorilaZone — landing page e painel local

Reconstrução de 04/11/2026 baseada no componente React original de 09/09 e nas decisões recuperadas das conversas. Este pacote não é uma cópia exata da pasta do computador do Arthur: o backend Python anterior e suas bases não estavam disponíveis. O componente original está preservado em `referencia/GorilaZoneLanding_original.jsx`, sem alterações.

## Comece aqui — Windows

1. Extraia este ZIP para uma NOVA pasta (não substitua seu projeto anterior).
2. Tenha Python estável 3.11–3.14 e Node.js 20.19+ instalados. Não precisa Docker nem alterar a política de execução do PowerShell. A instalação de dependências precisa de internet.
3. Abra `INSTALAR_WINDOWS.bat`. Ele cria a `.venv`, instala as dependências Python e Node e compila o frontend.
4. Abra `INICIAR_WINDOWS.bat`.
5. Acesse http://127.0.0.1:5173. API: http://127.0.0.1:8000/docs.
6. Clique em **Entrar no painel → Primeiro acesso? Criar academia**. Não existe senha padrão. Cada cadastro cria uma academia separada.

Mantenha as duas janelas abertas. Ctrl+C em cada uma encerra os servidores.

Se o Windows não encontrar o Python, confira `py --version`. Não use Python beta para esta instalação. Os atalhos foram revisados, mas não executados em um Windows real nesta entrega.

### Comandos manuais — PowerShell

Na pasta `backend_gorila`:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Em OUTRO terminal, na pasta `frontend`:

```powershell
npm.cmd ci
npm.cmd run dev
```

O `package.json` fica em `frontend`, não em `backend_gorila`.

## O que você recebe

- Landing React com logo original, preto/grafite, creme/bege e laranja, navegação móvel, títulos revistos, narrativa de gestão/alunos/planos/QR/treinos/evolução/app, mockups identificados como ilustrativos, dúvidas e contato.
- Navegação para login e painel, modal do aplicativo sem links fictícios, textos de termos e privacidade identificados como acadêmicos.
- Formulário conectado à API com validação, consentimento e armazenamento persistente. Não envia e-mail/WhatsApp.
- Backend FastAPI com banco SQLite local e isolamento dos registros por academia.
- Cadastro de academia, login, sessão com prazo de 8 horas, logout e senha com scrypt. Token aleatório opaco; NÃO é JWT nem refresh rotativo.
- CRUD de alunos, planos, matrículas, treinos em texto, avaliações manuais, mensalidades manuais e avisos internos.
- Frequência manual da equipe, QR real da unidade, verificação de matrícula ativa e bloqueio de presença duplicada no dia.
- Dashboard com dados cadastrados, sinalização simples de ausência e exportação JSON dos dados da própria unidade.

Não existem clientes, depoimentos, preços comerciais ou números de desempenho inventados. Os números no mockup são explicitamente ilustrativos; o painel começa vazio.

## Teste de demonstração

1. Crie sua academia e entre.
2. Cadastre um aluno e um plano.
3. Cadastre uma matrícula com início até hoje e fim depois de hoje, situação ativa.
4. Em Frequência / QR, selecione o aluno e confirme a presença. Tente novamente: a duplicação deve ser impedida.
5. Crie uma ficha, avaliação, aviso e mensalidade; altere a mensalidade para pago.
6. Consulte o dashboard e exporte seus dados.
7. Saia e entre novamente: os dados devem permanecer.

## Dados, contato e cópia de segurança

Os dados são gravados em `backend_gorila/data/gorila.db`, criado na primeira execução. Não apague essa pasta. Para copiar a base, pare a API primeiro e copie o arquivo para um local seguro. O banco contém dados pessoais e hashes de senhas; não publique ou envie o arquivo.

Contatos públicos ficam na tabela `leads` do mesmo banco e não aparecem para administradores de academias. O operador da instalação pode consultá-los localmente:

```powershell
cd backend_gorila
.\.venv\Scripts\python.exe consultar_contatos.py
```

## Limites e próximos incrementos

Consulte `ESCOPO_E_PROXIMOS_PASSOS.md` para separar o que foi implementado do que depende de material, integrações ou código não recuperado. Esta versão é para demonstração LOCAL, vinculada a 127.0.0.1. Não foi publicada e não está validada como SaaS de produção.

Não migre dados nem substitua a implementação anterior automaticamente. O schema e os IDs desta reconstrução são novos. O pacote não contém `.env`, senhas, banco de testes, `.venv` ou `node_modules`; os ambientes são recriados na instalação.
