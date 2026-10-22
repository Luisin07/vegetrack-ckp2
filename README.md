# VegeTrack — monitoramento de vegetação na faixa de domínio

[![CI](https://github.com/SEU-USUARIO/vegetrack-ckp2/actions/workflows/ci.yml/badge.svg)](https://github.com/SEU-USUARIO/vegetrack-ckp2/actions/workflows/ci.yml)

Checkpoint 2 de Engenharia de Software (FIAP, Prof. Jorge Luiz Gomes) — Challenge Sprint Motiva/CCR,
Rodoanel Mário Covas. O sistema registra a altura da vegetação por trecho, calcula a velocidade de
crescimento, classifica o risco diante do limite contratual de 30 cm, emite a ordem de serviço de
roçada e aponta a violação contratual iminente antes da multa.

| Integrante | RM |
|---|---|
| Vitor Barbosa de Paiva | 565303 |
| Luis Otavio Santini Feitosa | 563556 |
| Lucas Andrade Souza | 564066 |
| Arthur Traldi Felix | 563477 |

---

## 1. Como rodar (máquina limpa)

Requisito único: **Python 3.12 ou superior**. Não há banco, Docker nem variável de ambiente.

```bash
git clone https://github.com/SEU-USUARIO/vegetrack-ckp2.git
cd vegetrack-ckp2
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

Fluxo principal completo com o levantamento de amostra (importação → avaliação → ordens → fila → índice):

```bash
python -m vegetrack demo
```

Uso passo a passo (a base fica em `.vegetrack/dados.json`, ignorada pelo git):

```bash
python -m vegetrack importar dados/levantamento_rodoanel_amostra.csv
python -m vegetrack avaliar --hoje 2026-09-09
python -m vegetrack fila --hoje 2026-09-09 --km-inicial 0 --km-final 20 --sentido Norte
python -m vegetrack registrar RD-005 12 --data 2026-09-10 --responsavel "Marcos Ribeiro"
python -m vegetrack concluir OS-0001 6 --data 2026-09-10
python -m vegetrack indice --hoje 2026-09-10
```

> O arquivo `dados/levantamento_rodoanel_amostra.csv` é uma **amostra sintética** no formato do
> levantamento da Motiva (separador `;`), criada para demonstração — não são os dados reais.

## 2. Como testar

```bash
pytest                                  # suíte completa
pytest --cov --cov-report=term-missing  # com cobertura
```

## 3. Padrões de código

### Comandos (os mesmos que o CI executa)

```bash
ruff check .            # linter
ruff format .           # formatador (aplica)
ruff format --check .   # formatador (só confere, como no CI)
lint-imports            # fronteiras: domínio não importa aplicação, adaptadores nem o outro contexto
```

Configuração versionada em `pyproject.toml` (ruff: E, F, I, N, B, UP, SIM e complexidade máxima 8;
linha de 100 colunas) e `.editorconfig`.

### Convenções de nome

| O quê | Convenção | Exemplo |
|---|---|---|
| Arquivos e módulos | `snake_case`, termo do glossário do CP1 | `ordem_de_servico.py` |
| Classes | `PascalCase`, termo do glossário | `OrdemDeServico`, `AlturaVegetacao` |
| Funções e métodos | `snake_case`, verbo do negócio | `registrar_medicao`, `concluir` |
| Constantes | `MAIUSCULAS` | `LIMITE_CONTRATUAL_CM` |
| Exceções | estado do negócio, sem sufixo `Error` | `AlturaInvalida`, `TrechoNaoEncontrado` |
| Testes | `test_` + o que a regra garante | `test_nao_permite_altura_negativa_ou_acima_de_300_cm` |
| Branches | `tipo/descricao-curta` | `refactor/strategy-politica-de-rocada` |

Proibido no código: `Manager`, `Handler`, `Service` genérico, `data`, `aux`, e os sinônimos rejeitados
no glossário do CP1 (chamado → ordem de serviço; corte → roçada; mato → vegetação).

### Commits — Conventional Commits

`feat:` funcionalidade · `fix:` correção · `refactor:` muda estrutura sem mudar comportamento ·
`test:` · `docs:` · `ci:` · `chore:`. Refatoração **nunca** vai junto com funcionalidade no mesmo commit.

### Fluxo de trabalho

Nada entra direto na `main`: branch → pull request → CI verde → revisão de um colega que não
escreveu o código (checklist em `.github/pull_request_template.md`) → merge por quem revisou.

## 4. Arquitetura

Hexagonal (portas e adaptadores) com dois bounded contexts — decisão em
[`docs/adr/0002-arquitetura-hexagonal.md`](docs/adr/0002-arquitetura-hexagonal.md) e mapa em
[`docs/bounded-contexts.md`](docs/bounded-contexts.md).

```
src/vegetrack/
├── monitoramento/dominio/   # Trecho (raiz), Medicao, AlturaVegetacao, AvaliacaoDeRisco, IndiceDeSaude
├── manutencao/dominio/      # OrdemDeServico (raiz), PrazoLegal, ViolacaoContratual
├── aplicacao/               # casos de uso: registrar, importar, avaliar, fila, índice, concluir
└── adaptadores/             # entrada (CLI, CSV) e saída (persistência)
```

## 5. Documentação do projeto

- [`DEBT.md`](DEBT.md) — registro de dívida técnica priorizado
- [`docs/refatoracoes.md`](docs/refatoracoes.md) — refatorações e padrões GoF aplicados
- [`docs/bounded-contexts.md`](docs/bounded-contexts.md) — mapa de contextos
- [`docs/adr/`](docs/adr/) — decisões arquiteturais
