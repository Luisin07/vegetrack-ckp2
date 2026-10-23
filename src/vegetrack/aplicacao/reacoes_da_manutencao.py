"""
reacoes_da_manutencao.py
Observadores concretos: traduzem TrechoAvaliado em ordem de serviço e em violação contratual.
É a fronteira entre os contextos de Monitoramento e de Manutenção.
"""

from vegetrack.aplicacao.publicador_de_avaliacoes import ObservadorDeAvaliacao
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico
from vegetrack.manutencao.dominio.plano_de_regularizacao import PlanoDeRegularizacao
from vegetrack.manutencao.dominio.portas import RepositorioDeOrdens, RepositorioDeViolacoes
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual
from vegetrack.monitoramento.dominio.eventos import TrechoAvaliado


class EmissorDeOrdensDeServico(ObservadorDeAvaliacao):
    def __init__(self, ordens: RepositorioDeOrdens) -> None:
        self._ordens = ordens

    def ao_avaliar(self, evento: TrechoAvaliado) -> None:
        if not evento.exige_ordem_de_servico:
            return
        plano = PlanoDeRegularizacao.para(
            evento.altura_cm, evento.data_da_medicao, evento.dias_ate_o_limite, evento.critico
        )
        ordem = self._ordens.aberta_do_trecho(evento.trecho_id)
        # RN-06: trecho com ordem aberta tem a ordem reavaliada, nunca uma segunda ordem
        if ordem is None:
            ordem = OrdemDeServico.emitir(
                self._ordens.proximo_numero(),
                evento.trecho_id,
                evento.altura_cm,
                plano.prioridade,
                plano.prazo,
            )
        else:
            ordem.reavaliar(plano.prioridade, plano.prazo)
        self._ordens.salvar(ordem)


class ApuradorDeViolacoes(ObservadorDeAvaliacao):
    def __init__(self, violacoes: RepositorioDeViolacoes) -> None:
        self._violacoes = violacoes

    def ao_avaliar(self, evento: TrechoAvaliado) -> None:
        if not evento.violou_limite:
            return
        violacao = self._violacoes.ativa_do_trecho(evento.trecho_id) or ViolacaoContratual.apontar(
            evento.trecho_id, evento.altura_cm, evento.data_da_medicao
        )
        violacao.apurar(evento.data_da_avaliacao)
        self._violacoes.salvar(violacao)
