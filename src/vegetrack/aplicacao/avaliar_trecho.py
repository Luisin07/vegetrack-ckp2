"""
avaliar_trecho.py
Caso de uso principal (US-02 a US-05): avalia o risco do trecho, emite a ordem de serviço
e registra a violação contratual iminente.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from vegetrack.adaptadores.armazenamento_em_arquivo import ArmazenamentoEmArquivo
from vegetrack.aplicacao.erros import TrechoNaoEncontrado
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico
from vegetrack.manutencao.dominio.plano_de_regularizacao import PlanoDeRegularizacao
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual
from vegetrack.monitoramento.dominio.avaliacao_de_risco import AvaliacaoDeRisco, NivelDeRisco


@dataclass(frozen=True)
class ResultadoDaAvaliacao:
    avaliacao: AvaliacaoDeRisco
    ordem: OrdemDeServico | None
    violacao: ViolacaoContratual | None


class AvaliarTrecho:
    def __init__(self, caminho_dos_dados: Path) -> None:
        self._caminho_dos_dados = caminho_dos_dados

    def executar(self, trecho_id: str, hoje: date) -> ResultadoDaAvaliacao:
        # ===== BLOCO 1: avaliar_no_dominio =====
        dados = ArmazenamentoEmArquivo(self._caminho_dos_dados)
        trecho = dados.buscar_trecho(trecho_id)
        if trecho is None:
            raise TrechoNaoEncontrado(trecho_id)
        avaliacao = trecho.avaliar(hoje)

        # ===== BLOCO 2: reacoes_da_manutencao =====
        ordem = None
        if avaliacao.exige_ordem_de_servico:
            ordem = _emitir_ou_reavaliar_ordem(dados, avaliacao)
        violacao = None
        if avaliacao.violou_limite:
            violacao = _apontar_violacao(dados, avaliacao, hoje)

        dados.persistir()
        return ResultadoDaAvaliacao(avaliacao, ordem, violacao)


def _emitir_ou_reavaliar_ordem(
    dados: ArmazenamentoEmArquivo, avaliacao: AvaliacaoDeRisco
) -> OrdemDeServico:
    altura_cm = avaliacao.altura.centimetros
    plano = PlanoDeRegularizacao.para(
        altura_cm,
        avaliacao.data_da_medicao,
        avaliacao.dias_ate_o_limite,
        critico=avaliacao.nivel is NivelDeRisco.CRITICO,
    )
    ordem = dados.ordem_aberta_do_trecho(avaliacao.trecho_id)
    # RN-06: trecho com ordem aberta tem a ordem reavaliada, nunca uma segunda ordem
    if ordem is None:
        numero = dados.proximo_numero_de_ordem()
        ordem = OrdemDeServico.emitir(
            numero, avaliacao.trecho_id, altura_cm, plano.prioridade, plano.prazo
        )
    else:
        ordem.reavaliar(plano.prioridade, plano.prazo)
    dados.salvar_ordem(ordem)
    return ordem


def _apontar_violacao(
    dados: ArmazenamentoEmArquivo, avaliacao: AvaliacaoDeRisco, hoje: date
) -> ViolacaoContratual:
    violacao = dados.violacao_ativa_do_trecho(avaliacao.trecho_id)
    if violacao is None:
        violacao = ViolacaoContratual.apontar(
            avaliacao.trecho_id, avaliacao.altura.centimetros, avaliacao.data_da_medicao
        )
    violacao.apurar(hoje)
    dados.salvar_violacao(violacao)
    return violacao
