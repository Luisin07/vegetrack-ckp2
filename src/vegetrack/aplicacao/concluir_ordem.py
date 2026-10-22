"""
concluir_ordem.py
Caso de uso RF-08: conclui a roçada com a medição de comprovação e regulariza a violação (RN-04).
"""

from datetime import date

from vegetrack.aplicacao.erros import OrdemNaoEncontrada
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico
from vegetrack.manutencao.dominio.portas import RepositorioDeOrdens, RepositorioDeViolacoes
from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.medicao import Medicao
from vegetrack.monitoramento.dominio.portas import RepositorioDeTrechos


class ConcluirOrdemDeServico:
    def __init__(
        self,
        trechos: RepositorioDeTrechos,
        ordens: RepositorioDeOrdens,
        violacoes: RepositorioDeViolacoes,
    ) -> None:
        self._trechos = trechos
        self._ordens = ordens
        self._violacoes = violacoes

    def executar(
        self, numero: str, data: date, altura_comprovada_cm: float, responsavel: str
    ) -> OrdemDeServico:
        # ===== BLOCO 1: localizar_ordem =====
        ordem = self._ordens.buscar(numero)
        if ordem is None:
            raise OrdemNaoEncontrada(numero)

        # ===== BLOCO 2: concluir_e_regularizar =====
        # concluir primeiro: se a altura ainda viola o limite, nada mais é alterado
        ordem.concluir(altura_comprovada_cm)
        trecho = self._trechos.buscar(ordem.trecho_id)
        trecho.registrar_medicao(Medicao(data, AlturaVegetacao(altura_comprovada_cm), responsavel))
        violacao = self._violacoes.ativa_do_trecho(ordem.trecho_id)
        if violacao is not None:
            violacao.regularizar()
            self._violacoes.salvar(violacao)

        # ===== BLOCO 3: salvar =====
        self._trechos.salvar(trecho)
        self._ordens.salvar(ordem)
        return ordem
