"""
avaliar_trecho.py
Caso de uso principal (US-02 a US-05): avalia o risco do trecho e publica TrechoAvaliado.
Ordem de serviço e violação são reações da Manutenção (reacoes_da_manutencao.py).
"""

from dataclasses import dataclass
from datetime import date

from vegetrack.aplicacao.erros import TrechoNaoEncontrado
from vegetrack.aplicacao.publicador_de_avaliacoes import PublicadorDeAvaliacoes
from vegetrack.aplicacao.reacoes_da_manutencao import (
    ApuradorDeViolacoes,
    EmissorDeOrdensDeServico,
)
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico
from vegetrack.manutencao.dominio.portas import RepositorioDeOrdens, RepositorioDeViolacoes
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual
from vegetrack.monitoramento.dominio.avaliacao_de_risco import AvaliacaoDeRisco
from vegetrack.monitoramento.dominio.eventos import TrechoAvaliado
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
        publicador: PublicadorDeAvaliacoes | None = None,
    ) -> None:
        self._trechos = trechos
        self._ordens = ordens
        self._violacoes = violacoes
        self.publicador = publicador or PublicadorDeAvaliacoes(
            [EmissorDeOrdensDeServico(ordens), ApuradorDeViolacoes(violacoes)]
        )

    def executar(self, trecho_id: str, hoje: date) -> ResultadoDaAvaliacao:
        # ===== BLOCO 1: avaliar_no_dominio =====
        trecho = self._trechos.buscar(trecho_id)
        if trecho is None:
            raise TrechoNaoEncontrado(trecho_id)
        avaliacao = trecho.avaliar(hoje)

        # ===== BLOCO 2: publicar_evento =====
        self.publicador.publicar(TrechoAvaliado.de(avaliacao))

        # ===== BLOCO 3: montar_resultado =====
        # só consulta: quem decide emitir ordem ou apontar violação são os observadores
        ordem = (
            self._ordens.aberta_do_trecho(trecho_id) if avaliacao.exige_ordem_de_servico else None
        )
        violacao = self._violacoes.ativa_do_trecho(trecho_id) if avaliacao.violou_limite else None
        return ResultadoDaAvaliacao(avaliacao, ordem, violacao)
