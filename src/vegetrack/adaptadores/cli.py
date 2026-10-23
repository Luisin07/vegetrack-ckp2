"""
cli.py
Adaptador de entrada em linha de comando -- executa o fluxo principal sem interface gráfica.
Chamado por `python -m vegetrack <comando>`; ver README para os exemplos.
"""

import argparse
import tempfile
from datetime import date
from pathlib import Path

from vegetrack.adaptadores.importador_csv import ler_levantamento_csv
from vegetrack.adaptadores.repositorios_em_arquivo import (
    RepositorioDeOrdensEmArquivo,
    RepositorioDeTrechosEmArquivo,
    RepositorioDeViolacoesEmArquivo,
)
from vegetrack.aplicacao.avaliar_trecho import AvaliarTrecho, ResultadoDaAvaliacao
from vegetrack.aplicacao.calcular_indice import CalcularIndiceDeSaude
from vegetrack.aplicacao.concluir_ordem import ConcluirOrdemDeServico
from vegetrack.aplicacao.consultar_fila import ConsultarFilaDeTrechos
from vegetrack.aplicacao.importar_levantamento import ImportarLevantamento
from vegetrack.aplicacao.publicador_de_avaliacoes import ObservadorDeAvaliacao
from vegetrack.aplicacao.registrar_medicao import RegistrarMedicao
from vegetrack.monitoramento.dominio.avaliacao_de_risco import AvaliacaoDeRisco
from vegetrack.monitoramento.dominio.eventos import TrechoAvaliado

DADOS_PADRAO = Path(".vegetrack")
AMOSTRA = Path(__file__).resolve().parents[3] / "dados" / "levantamento_rodoanel_amostra.csv"
DATA_DA_AMOSTRA = date(2026, 9, 9)


# ===== BLOCO 1: composicao_dos_casos_de_uso =====
class AvisoDeViolacaoNoTerminal(ObservadorDeAvaliacao):
    # observador acrescentado sem alterar AvaliarTrecho: é o ganho do padrão Observer
    def ao_avaliar(self, evento: TrechoAvaliado) -> None:
        if evento.violou_limite:
            print(f"!! {evento.trecho_id} acima de 30 cm: avisar a coordenação de manutenção")


class Aplicacao:
    # raiz de composição: único lugar que escolhe quais adaptadores cumprem as portas
    def __init__(self, pasta_dos_dados: Path) -> None:
        trechos = RepositorioDeTrechosEmArquivo(pasta_dos_dados)
        ordens = RepositorioDeOrdensEmArquivo(pasta_dos_dados)
        violacoes = RepositorioDeViolacoesEmArquivo(pasta_dos_dados)
        self.importar = ImportarLevantamento(trechos)
        self.registrar = RegistrarMedicao(trechos)
        self.avaliar = AvaliarTrecho(trechos, ordens, violacoes)
        self.avaliar.publicador.inscrever(AvisoDeViolacaoNoTerminal())
        self.fila = ConsultarFilaDeTrechos(trechos)
        self.indice = CalcularIndiceDeSaude(self.fila)
        self.concluir = ConcluirOrdemDeServico(trechos, ordens, violacoes)


# ===== BLOCO 2: comandos =====
def _importar(app: Aplicacao, args: argparse.Namespace) -> None:
    resultado = app.importar.executar(ler_levantamento_csv(args.arquivo))
    print(f"{resultado.importadas} medições importadas, {len(resultado.rejeitadas)} rejeitadas.")
    for motivo in resultado.rejeitadas:
        print(f"  rejeitada -> {motivo}")


def _avaliar(app: Aplicacao, args: argparse.Namespace) -> None:
    for avaliacao in app.fila.executar(args.hoje):
        _imprimir_resultado(app.avaliar.executar(avaliacao.trecho_id, args.hoje))


def _fila(app: Aplicacao, args: argparse.Namespace) -> None:
    fila = app.fila.executar(args.hoje, args.km_inicial, args.km_final, args.sentido)
    print(f"{'TRECHO':<8} {'NÍVEL':<9} {'ALTURA':>8} {'CM/DIA':>7} {'DIAS P/ 30CM':>12}")
    for avaliacao in fila:
        print(_linha_da_fila(avaliacao))


def _indice(app: Aplicacao, args: argparse.Namespace) -> None:
    indice = app.indice.executar(args.hoje)
    print(f"Índice de saúde da rodovia em {args.hoje:%d/%m/%Y}: {indice.valor}/100")


def _registrar(app: Aplicacao, args: argparse.Namespace) -> None:
    medicao = app.registrar.executar(args.trecho, args.data, args.altura, args.responsavel)
    print(f"Medição registrada: {args.trecho} com {medicao.altura} em {medicao.data:%d/%m/%Y}.")


def _concluir(app: Aplicacao, args: argparse.Namespace) -> None:
    ordem = app.concluir.executar(args.numero, args.data, args.altura, args.responsavel)
    print(
        f"{ordem.numero} concluída; trecho {ordem.trecho_id} regularizado com {args.altura:g} cm."
    )


def _demo(_: Aplicacao, args: argparse.Namespace) -> None:
    # demo usa base temporária para rodar igual em qualquer máquina, sem sujar .vegetrack/
    with tempfile.TemporaryDirectory() as pasta:
        app = Aplicacao(Path(pasta))
        args.arquivo, args.hoje = AMOSTRA, DATA_DA_AMOSTRA
        args.km_inicial = args.km_final = args.sentido = None
        for titulo, comando in [
            ("1. Importação do levantamento", _importar),
            ("2. Avaliação de risco e emissão de ordens", _avaliar),
            ("3. Fila de trabalho por criticidade", _fila),
            ("4. Índice de saúde", _indice),
        ]:
            print(f"\n=== {titulo} ===")
            comando(app, args)


# ===== BLOCO 3: formatacao_da_saida =====
def _linha_da_fila(a: AvaliacaoDeRisco) -> str:
    taxa = f"{a.taxa_cm_por_dia:.2f}" if a.taxa_disponivel else "—"
    dias = "—" if a.dias_ate_o_limite is None else str(a.dias_ate_o_limite)
    return f"{a.trecho_id:<8} {a.nivel.name:<9} {str(a.altura):>8} {taxa:>7} {dias:>12}"


def _imprimir_resultado(resultado: ResultadoDaAvaliacao) -> None:
    linha = _linha_da_fila(resultado.avaliacao)
    if resultado.ordem is not None:
        o = resultado.ordem
        prazo = f"{o.prazo.data_limite:%d/%m}"
        linha += f" | {o.numero} {o.prioridade.name} até {prazo} — {o.metodo_de_rocada}"
    if resultado.violacao is not None:
        linha += f" | VIOLAÇÃO {resultado.violacao.situacao.value.upper()}"
    print(linha)


# ===== BLOCO 4: argumentos =====
def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vegetrack", description="VegeTrack — CLI")
    parser.add_argument("--dados", type=Path, default=DADOS_PADRAO, help="pasta da base JSON")
    sub = parser.add_subparsers(dest="comando", required=True)

    sub.add_parser("demo", help="roda o fluxo completo com o levantamento de amostra")
    sub.add_parser("importar", help="importa levantamento CSV").add_argument("arquivo", type=Path)
    for nome, ajuda in [("avaliar", "avalia todos os trechos"), ("indice", "índice de saúde")]:
        sub.add_parser(nome, help=ajuda).add_argument(
            "--hoje", type=date.fromisoformat, default=date.today()
        )

    fila = sub.add_parser("fila", help="trechos por criticidade")
    fila.add_argument("--hoje", type=date.fromisoformat, default=date.today())
    fila.add_argument("--km-inicial", type=float)
    fila.add_argument("--km-final", type=float)
    fila.add_argument("--sentido")

    for nome, alvo in [("registrar", "trecho"), ("concluir", "numero")]:
        comando = sub.add_parser(nome, help=f"{nome} ({alvo} e altura em cm)")
        comando.add_argument(alvo)
        comando.add_argument("altura", type=float)
        comando.add_argument("--data", type=date.fromisoformat, default=date.today())
        comando.add_argument("--responsavel", default="Técnico de campo")
    return parser


COMANDOS = {
    "demo": _demo,
    "importar": _importar,
    "avaliar": _avaliar,
    "fila": _fila,
    "indice": _indice,
    "registrar": _registrar,
    "concluir": _concluir,
}


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        COMANDOS[args.comando](Aplicacao(args.dados), args)
    except (LookupError, ValueError) as erro:
        print(f"Erro: {erro}")
        return 1
    return 0
