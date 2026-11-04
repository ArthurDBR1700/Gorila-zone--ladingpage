# Escopo recuperado e situação da entrega

## Evidências e preservação

Fonte de código recuperada: `GorilaZoneLanding.jsx`, de 09/09/2026, preservada integralmente em `referencia/`. A logo embutida foi extraída para `frontend/public/logo.png`.

Nas conversas de 23/09 foram pedidos título/subtítulo mais concretos, remoção da etiqueta retangular inicial, mais contraste sem neon, menos cards repetitivos, variação de fundos e narrativa academia → gestão → alunos → planos/matrículas → frequência/QR → treinos → evolução → app. Esses ajustes orientaram a nova landing.

A versão antiga tinha CTAs sem destino, QR representado apenas por um ícone, links de loja impedidos e texto de lançamento futuro. A nova versão oferece login/painel e contato conectados, QR real para a academia e informação explícita sobre a distribuição do app.

O backend em `backend_gorila` é NOVO, reconstruído para demonstração. Não recupera todos os arquivos e comportamentos anteriores. O histórico fala em versões distintas Python/FastAPI e Node/Prisma; não foram misturadas silenciosamente.

## Matriz de funcionalidades

| Item | Situação neste pacote |
|---|---|
| React, marca/logo, cores e landing antes do login | Implementado |
| Navegação, contato, modal, termos/privacidade provisórios | Implementado |
| Alunos, planos e matrículas | CRUD integrado |
| Login e logout | Implementado com sessão opaca e scrypt |
| JWT, Argon2, refresh rotativo, vinculação usuário-aluno | Não reproduzidos; exigem recuperar e integrar o backend original |
| Banco persistente | SQLite local; PostgreSQL/SQLAlchemy/Alembic não incluídos |
| Isolamento por academia | Implementado nos endpoints do painel |
| Treinador, nutricionista, aluno e admin | Esta versão tem somente conta administradora da própria academia |
| QR da unidade | PNG real com `GORILAZONE:ACADEMY:{id}` |
| Check-in da equipe | Implementado com matrícula ativa e unicidade diária |
| Leitura pela câmera e check-in do aluno autenticado | Ainda não integrados |
| Treinos | Ficha textual; sem biblioteca/vídeos ou controle de cargas |
| Evolução | Avaliação manual de peso e observações; sem gráficos históricos |
| Financeiro | Registro manual; sem Pix, cartão, boleto, recorrência ou conciliação |
| Avisos | Internos no painel; sem envio externo |
| Dashboard e exportação | Dados reais da unidade e JSON; sem relatórios avançados/PDF |
| Risco | Regra transparente de ausência; sem IA ou previsão estatística |
| App Flutter / login por CPF | Não incluído; falta código atual do app e integração |
| App Store, Google Play, APK | Links e distribuição não fornecidos |
| Loja integrada | Prevista no componente antigo; comércio/estoque/checkout não implementados |
| White-label e planos comerciais | Planejamento; condições e implementação não definidas |
| Telas reais do app | Não recuperadas; imagens atuais são mockups identificados |
| Depoimentos | Não adicionados: não há depoimentos verificáveis |
| Publicação / domínio | Não executados; entrega solicitada em ZIP local |

## O que falta para cumprir toda a visão anterior

1. Recuperar a pasta atual de backend e o app para comparar funcionalidades e migrar sem perda.
2. Decidir a arquitetura definitiva (Python foi a preferência registrada), migrar para PostgreSQL e criar migrações.
3. Integrar autenticação completa, papéis e vínculo usuário-aluno; reforçar proteção contra tentativas, recuperação de senha e políticas de sessão.
4. Integrar a leitura de QR com o aluno autenticado. QR estático não prova presença física; uso real pede validação adicional.
5. Integrar app Flutter, links de lojas e imagens reais. Testar em dispositivos.
6. Implementar biblioteca de treinos, vídeos, gráficos de evolução, loja e integrações somente com requisitos definidos.
7. Definir preços, política de dados, canal de contato e provedor de mensagens antes de ativar operações comerciais.
8. Validar com academia real, implantar HTTPS, backups/restauração, monitoramento e revisão de segurança.

Esta entrega torna utilizável uma reconstrução local e mantém as pendências explícitas. Não representa a conclusão de todos os itens planejados no histórico.
