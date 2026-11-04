# Validação desta entrega — 04/11/2026

- `npm run build`: aprovado (React 19 / Vite 6.4.5).
- `python test_fluxo.py`: aprovado com as dependências Python de `requirements.txt` instaladas.
- Fluxos verificados: criação de duas academias, senha errada, acesso sem autenticação, isolamento de leitura/escrita, alunos, planos, matrícula, check-in bloqueado sem matrícula, QR inválido, QR PNG válido, presença duplicada, mensalidades pendente/pago, treinos, avaliações, avisos, dashboard, exportação, contato e revogação da sessão no logout.
- Navegador: landing renderizada em desktop; modal de aplicativo abre e apresenta indisponibilidade dos links corretamente. Conferência visual do hero, marca, mockup e navegação.
- Responsividade implementada em CSS; não houve teste em dispositivo móvel real.
- Scripts `.bat`: revisão estática; não foram executados em Windows.
- Não foi feita integração de navegador ponta a ponta com API em produção, auditoria de segurança, teste de carga ou validação com academia real.

O teste Python requer `httpx`, além das dependências normais. Para reproduzir no ambiente virtual: `python -m pip install httpx` e `python test_fluxo.py` (ou use o caminho completo para `.venv/Scripts/python.exe` no Windows).
