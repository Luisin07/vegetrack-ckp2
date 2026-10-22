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

---

## Refatoração 1 — Regras de risco no domínio

**Code smells:** função longa (`AvaliarTrecho.executar`, ~70 linhas, `noqa: C901` para o ruff
aceitar), números mágicos (`30`, `2`, `7`, 48 h), **duplicação** (o cálculo de taxa, projeção e nível
existia copiado em `ConsultarFilaDeTrechos._avaliar`) e regra de negócio fora do domínio.

**Antes** — `aplicacao/avaliar_trecho.py` (trecho):

```python
dias_ate_limite = None
if altura >= 30:
    dias_ate_limite = 0
elif taxa is not None and taxa > 0:
    dias_ate_limite = math.floor((30 - altura) / taxa)

if altura >= 30 or (dias_ate_limite is not None and dias_ate_limite <= 2):
    nivel = NivelDeRisco.CRITICO
elif dias_ate_limite is not None and dias_ate_limite <= 7:
    nivel = NivelDeRisco.ATENCAO
```

**Depois** — o caso de uso só orquestra; a regra mora no agregado:

```python
avaliacao = trecho.avaliar(hoje)  # monitoramento/dominio/trecho.py
if avaliacao.exige_ordem_de_servico:
    ordem = _emitir_ou_reavaliar_ordem(dados, avaliacao)
if avaliacao.violou_limite:
    violacao = _apontar_violacao(dados, avaliacao, hoje)
```

**O que melhorou:** a regra contratual existe em um lugar só e com nome; mudar o limite de 30 cm é
editar uma constante e a fila e a ordem nunca mais divergem. A função principal caiu de ~70 para
~15 linhas e o `noqa` sumiu. Os 103 testes de caracterização passaram sem alteração em cada um dos
4 commits `refactor:`.

**Commits:** constantes → taxa em `Trecho` → classificação em `Trecho.avaliar` → prioridade/prazo em
`PlanoDeRegularizacao`.

---

## Refatoração 2 — Portas e adaptadores (componente redesenhado)

**Code smell:** acoplamento excessivo — a camada de aplicação dependia de um adaptador concreto.
Os 5 casos de uso faziam `ArmazenamentoEmArquivo(self._caminho_dos_dados)` dentro de `executar`, e
os testes de caso de uso gravavam em disco.

**Antes** — `aplicacao/avaliar_trecho.py`:

```python
class AvaliarTrecho:
    def __init__(self, caminho_dos_dados: Path) -> None:
        self._caminho_dos_dados = caminho_dos_dados

    def executar(self, trecho_id: str, hoje: date) -> ResultadoDaAvaliacao:
        dados = ArmazenamentoEmArquivo(self._caminho_dos_dados)  # adaptador criado por dentro
        trecho = dados.buscar_trecho(trecho_id)
```

**Depois** — o caso de uso recebe as portas; quem escolhe o adaptador é a raiz de composição (CLI):

```python
class AvaliarTrecho:
    def __init__(
        self,
        trechos: RepositorioDeTrechos,  # porta declarada em monitoramento/dominio/portas.py
        ordens: RepositorioDeOrdens,  # portas declaradas em manutencao/dominio/portas.py
        violacoes: RepositorioDeViolacoes,
    ) -> None: ...
```

| Porta (domínio) | Adaptador em memória | Adaptador em arquivo |
|---|---|---|
| `RepositorioDeTrechos` | `RepositorioDeTrechosEmMemoria` | `RepositorioDeTrechosEmArquivo` |
| `RepositorioDeOrdens` | `RepositorioDeOrdensEmMemoria` | `RepositorioDeOrdensEmArquivo` |
| `RepositorioDeViolacoes` | `RepositorioDeViolacoesEmMemoria` | `RepositorioDeViolacoesEmArquivo` |

**O que melhorou:** trocar o arquivo por banco no Checkpoint 3 é escrever um adaptador novo; nenhum
caso de uso muda. Os testes dos casos de uso rodam com o adaptador em memória, sem disco, e os testes
de contrato (`tests/contratos/`) provam que os dois adaptadores se comportam igual. Medido pelo
`import-linter`: antes, o contrato "aplicação não importa adaptadores" **quebrava em 5 imports**;
depois, **3 contratos mantidos, 0 quebrados**, verificados a cada pull request.

**Nota honesta:** um teste de caracterização dependia de o armazenamento em arquivo devolver cópias
dos objetos. Ele foi corrigido num commit `test:` próprio, **antes** da refatoração, sem mudar a regra
que verifica; a partir daí a mesma suíte passou antes e depois de cada commit `refactor:`.
