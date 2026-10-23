# ADR 0002 — Adotar arquitetura hexagonal com dois bounded contexts

- **Data:** 22/10/2026
- **Status:** aceito
- **Substitui parcialmente:** ADR 0001 (monólito modular em camadas), que continua valendo para a implantação

## Contexto

O ADR 0001 separou o sistema em camadas, mas no código da Aula 05 a camada de aplicação instanciava
o armazenamento em arquivo dentro de cada caso de uso, e o caso de uso principal decidia regras
contratuais (prioridade, prazo de 48 h, violação) que pertencem a outro conceito do negócio. O
Checkpoint 3 vai trocar o arquivo JSON por banco relacional e expor uma API REST; com o código
como estava, as duas mudanças exigiriam reescrever as regras de negócio.

## Decisão

1. Organizar o código em **portas e adaptadores**: o domínio declara as portas
   (`RepositorioDeTrechos`, `RepositorioDeOrdens`, `RepositorioDeViolacoes`) e os adaptadores
   (memória, arquivo JSON, CSV, CLI) as implementam; os casos de uso recebem as portas no construtor.
2. Separar o domínio em **dois bounded contexts**, Monitoramento e Manutenção, que não se importam.
3. Tornar as duas regras **verificáveis pela máquina**: contratos do `import-linter` rodam no CI.

## Alternativas consideradas

- **Manter camadas sem portas:** descartada — os testes de caso de uso continuariam tocando o disco e
  a troca para banco no CKP3 continuaria cara.
- **Um único contexto com todas as classes:** descartada — "Trecho", "Prazo" e "Situação" têm
  significados diferentes para quem mede e para quem executa a roçada (ver `docs/bounded-contexts.md`).
- **Microsserviços por contexto já agora:** descartada — o enunciado deixa a decomposição para o
  CKP3 e a equipe não tem infraestrutura para operar dois serviços; a fronteira em pacote prepara essa
  decisão sem pagar o custo agora.

## Consequências

- ➕ O domínio roda e é testado sem framework, banco ou disco (`grep import` na pasta de domínio só
  encontra a biblioteca padrão e o próprio contexto).
- ➕ Trocar JSON por banco no CKP3 é escrever um adaptador novo; os casos de uso não mudam.
- ➕ A fronteira entre contextos é medida a cada pull request, não só desenhada.
- ➖ Mais arquivos e uma indireção a mais para quem chega ao projeto.
- ➖ O limite de 30 cm aparece nos dois contextos (DT-07), preço de não acoplar um ao outro.

- ➕ A regra contratual de risco existe uma única vez, em AvaliacaoDeRisco.classificar (refatoração 1, DT-01).
