# Registro de refatorações

Cada refatoração entra por um pull request próprio, com commits `refactor:` pequenos e a mesma suíte
de testes verde antes e depois. Os testes de caracterização de `tests/aplicacao/` foram escritos
**antes** de qualquer refatoração para congelar o comportamento do caso de uso principal.

| # | Code smell | Técnica | Dívida paga | Branch |
|---|---|---|---|---|
| 1 | Função longa, números mágicos, duplicação, regra fora do domínio | Extrair função, mover método, constantes nomeadas | DT-01 | `refactor/regras-de-risco-no-dominio` |
| 2 | Acoplamento da aplicação a um adaptador concreto | Portas e adaptadores com injeção de dependência | DT-02 | `refactor/portas-e-adaptadores` |
| 3 | Cadeia de `if` por tipo | Padrão Strategy | DT-03 | `refactor/strategy-politica-de-rocada` |
| 4 | Caso de uso que conhece outro contexto | Padrão Observer | DT-04 | `refactor/observer-trecho-avaliado` |
