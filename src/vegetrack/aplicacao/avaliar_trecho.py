"""
avaliar_trecho.py
Caso de uso principal (US-02 a US-05): avalia o risco do trecho, emite a ordem de serviço
e registra a violação contratual iminente.
"""

from dataclasses import dataclass
from datetime import date

from vegetrack.aplicacao.erros import TrechoNaoEncontrado
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico
from vegetrack.manutencao.dominio.plano_de_regularizacao import PlanoDeRegularizacao
from vegetrack.manutencao.dominio.portas import RepositorioDeOrdens, RepositorioDeViolacoes
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual
from vegetrack.monitoramento.dominio.avaliacao_de_risco import AvaliacaoDeRisco, NivelDeRisco
from vegetrack.monitoramento.dominio.portas import RepositorioDeTrechos


@dataclass(frozen=True)
class ResultadoDaAvaliacao:
    avaliacao: AvaliacaoDeRisco
    ordem: OrdemDeServico | None
    violacao: ViolacaoContratual | None


class AvaliarTrecho:
    def __init__(
        self,
        trechos: RepositorioDeTrechos,
        ordens: RepositorioDeOrdens,
        violacoes: RepositorioDeViolacoes,
    ) -> None:
        self._trechos = trechos
        self._ordens = ordens
        self._violacoes = violacoes

    def executar(self, trecho_id: str, hoje: date) -> ResultadoDaAvaliacao:
        # ===== BLOCO 1: avaliar_no_dominio =====
        trecho = self._trechos.buscar(trecho_id)
        if trecho is None:
            raise TrechoNaoEncontrado(trecho_id)
        avaliacao = trecho.avaliar(hoje)

        # ===== BLOCO 2: reacoes_da_manutencao =====
        ordem = None
        if avaliacao.exige_ordem_de_servico:
            ordem = _emitir_ou_reavaliar_ordem(self._ordens, avaliacao)
        violacao = None
        if avaliacao.violou_limite:
            violacao = _apontar_violacao(self._violacoes, avaliacao, hoje)
        return ResultadoDaAvaliacao(avaliacao, ordem, violacao)


def _emitir_ou_reavaliar_ordem(
    ordens: RepositorioDeOrdens, avaliacao: AvaliacaoDeRisco
) -> OrdemDeServico:
    altura_cm = avaliacao.altura.centimetros
    plano = PlanoDeRegularizacao.para(
        altura_cm,
        avaliacao.data_da_medicao,
        avaliacao.dias_ate_o_limite,
        critico=avaliacao.nivel is NivelDeRisco.CRITICO,
    )
    ordem = ordens.aberta_do_trecho(avaliacao.trecho_id)
    # RN-06: trecho com ordem aberta tem a ordem reavaliada, nunca uma segunda ordem
    if ordem is None:
        numero = ordens.proximo_numero()
        ordem = OrdemDeServico.emitir(
            numero, avaliacao.trecho_id, altura_cm, plano.prioridade, plano.prazo
        )
    else:
        ordem.reavaliar(plano.prioridade, plano.prazo)
    ordens.salvar(ordem)
    return ordem


def _apontar_violacao(
    violacoes: RepositorioDeViolacoes, avaliacao: AvaliacaoDeRisco, hoje: date
) -> ViolacaoContratual:
    violacao = violacoes.ativa_do_trecho(avaliacao.trecho_id)
    if violacao is None:
        violacao = ViolacaoContratual.apontar(
            avaliacao.trecho_id, avaliacao.altura.centimetros, avaliacao.data_da_medicao
        )
    violacao.apurar(hoje)
    violacoes.salvar(violacao)
    return violacao
