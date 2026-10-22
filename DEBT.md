# Registro de dívida técnica — VegeTrack

Lugar único de registro da dívida técnica do projeto. Cada item diz o que é, onde está, por que foi
assumido, o impacto de mantê-lo e o custo de conviver com ele. Quando uma dívida é paga, o item
continua aqui com o status e o pull request que a pagou.

**Prioridade:** 🔴 **Alta** compromete o projeto · 🟠 **Média** adia melhorias · 🟢 **Baixa** cosmética

| ID | Dívida | Prioridade | Status |
|----|--------|-----------|--------|
| DT-01 | Regra de avaliação de risco duplicada e fora do domínio | 🔴 Alta | ✅ Paga — refatoração 1 |
| DT-02 | Casos de uso instanciam o armazenamento em arquivo por dentro | 🔴 Alta | ✅ Paga — refatoração 2 |
| DT-03 | Cadeia de `if` decide método de roçada, equipes e EPI | 🟠 Média | ✅ Paga — refatoração 3 |
| DT-04 | `AvaliarTrecho` conhece os detalhes do contexto de Manutenção | 🟠 Média | A pagar — refatoração 4 |
| DT-05 | Persistência em um único arquivo JSON reescrito a cada operação | 🔴 Alta | Aberta |
| DT-06 | Órgão regulador e prazo de 48 h fixos no código | 🟠 Média | Aberta |
| DT-07 | Limite de 30 cm declarado nos dois contextos | 🟠 Média | Aberta |
| DT-08 | Levantamento importado em CSV, não no XLSX/KMZ original | 🟢 Baixa | Aberta |
| DT-09 | Número da ordem calculado pela quantidade de ordens | 🟢 Baixa | Aberta |

---

### DT-01 — Regra de avaliação de risco duplicada e fora do domínio
- **Onde:** `aplicacao/avaliar_trecho.py` (`executar`, ~70 linhas) e `aplicacao/consultar_fila.py` (`_avaliar`)
- **Por que foi assumido:** prazo curto para ter o fluxo principal rodando ponta a ponta na Aula 05.
- **Impacto:** o cálculo de taxa, projeção e nível existe em duas cópias com os números mágicos `30`, `2` e `7`. Mudar o limite contratual em uma cópia e esquecer a outra faz a fila mostrar um nível e a ordem de serviço ser emitida com outro.
- **Custo de conviver:** toda mudança de regra contratual exige editar 2 arquivos e revisar ~15 condições; o ruff já acusava complexidade (`noqa: C901`).

### DT-02 — Casos de uso instanciam o armazenamento em arquivo por dentro
- **Onde:** todos os arquivos de `aplicacao/` fazem `ArmazenamentoEmArquivo(self._caminho_dos_dados)`
- **Por que foi assumido:** era o jeito mais rápido de persistir sem banco.
- **Impacto:** a camada de aplicação depende de um adaptador concreto; trocar o arquivo por banco (Checkpoint 3) obriga a reescrever os 5 casos de uso, e os testes do caso de uso tocam o disco.
- **Custo de conviver:** ~1 h por caso de uso para migrar a persistência; testes mais lentos e frágeis.

### DT-03 — Cadeia de `if` decide método de roçada, equipes e EPI
- **Onde:** `manutencao/dominio/ordem_de_servico.py`, `OrdemDeServico.emitir`
- **Por que foi assumido:** só existiam três métodos de roçada no levantamento da Motiva.
- **Impacto:** cada método novo (roçada em talude, química, de canteiro central) exige abrir a entidade e acrescentar um ramo, com risco de quebrar as faixas existentes.
- **Custo de conviver:** ~1 h e reteste de toda a emissão de ordens por método novo.

### DT-04 — `AvaliarTrecho` conhece os detalhes do contexto de Manutenção
- **Onde:** `aplicacao/avaliar_trecho.py`
- **Por que foi assumido:** o fluxo principal foi escrito como uma sequência única.
- **Impacto:** o Monitoramento decide prioridade, prazo, emissão e violação; qualquer reação nova (notificar a coordenação, alimentar o relatório) exige mexer no caso de uso principal.
- **Custo de conviver:** toda reação nova a uma avaliação mexe no arquivo mais crítico do sistema.

### DT-05 — Persistência em um único arquivo JSON reescrito a cada operação
- **Onde:** `adaptadores/repositorios_em_arquivo.py` (um JSON por repositório, regravado a cada `salvar`)
- **Por que foi assumido:** o enunciado do CKP2 aceita persistência em arquivo; banco real, transação e migração são escopo do Checkpoint 3.
- **Impacto:** dois técnicos registrando ao mesmo tempo podem sobrescrever a medição um do outro (última escrita vence); o arquivo é regravado inteiro a cada `salvar`, então importar 248 trechos regrava o arquivo 248 vezes.
- **Custo de conviver:** inaceitável em produção; aceitável enquanto o sistema roda numa só máquina.
- **Plano:** adaptador de banco relacional atrás das mesmas portas, no Checkpoint 3.

### DT-06 — Órgão regulador e prazo de 48 h fixos no código
- **Onde:** criação de `ViolacaoContratual` e de `PrazoLegal` (origem "Contrato ARTESP — 48 h")
- **Por que foi assumido:** o MVP é validado só no Rodoanel, concessão estadual (ARTESP).
- **Impacto:** trecho de rodovia federal (ANTT) ou contrato com outro prazo recebe violação com base legal errada no relatório ao regulador.
- **Custo de conviver:** zero enquanto só houver o Rodoanel; bloqueia o item Won't have W2 (múltiplas rodovias).

### DT-07 — Limite de 30 cm declarado nos dois contextos
- **Onde:** Monitoramento (limite da avaliação) e Manutenção (`LIMITE_CONTRATUAL_CM` na conclusão da ordem)
- **Por que foi assumido:** cada bounded context é dono das próprias regras e não importa o outro (contrato do import-linter).
- **Impacto:** se a ARTESP mudar o limite, a mudança precisa ser feita nos dois lugares.
- **Custo de conviver:** baixo hoje (2 constantes, ambas testadas); vira configuração por contrato junto com a DT-06.

### DT-08 — Levantamento importado em CSV, não no XLSX/KMZ original
- **Onde:** `adaptadores/importador_csv.py`
- **Por que foi assumido:** evitar dependência de leitura de planilha no MVP; o CSV sai da planilha em um clique.
- **Impacto:** a coordenação precisa exportar a planilha antes de importar.
- **Custo de conviver:** ~2 min por levantamento.

### DT-09 — Número da ordem calculado pela quantidade de ordens
- **Onde:** `proximo_numero` em `adaptadores/repositorios_em_memoria.py` (herdado pelo adaptador em arquivo)
- **Por que foi assumido:** ordens nunca são excluídas no MVP.
- **Impacto:** se exclusão de ordem for criada, números passam a se repetir.
- **Custo de conviver:** nenhum enquanto não houver exclusão.
