"""
registrar_medicao.py
Caso de uso US-01 (RF-01): o técnico registra a altura medida num trecho existente.
"""

from datetime import date

from vegetrack.aplicacao.erros import TrechoNaoEncontrado
from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.medicao import Medicao
from vegetrack.monitoramento.dominio.portas import RepositorioDeTrechos


class RegistrarMedicao:
    def __init__(self, trechos: RepositorioDeTrechos) -> None:
        self._trechos = trechos

    def executar(self, trecho_id: str, data: date, altura_cm: float, responsavel: str) -> Medicao:
        # ===== BLOCO 1: localizar_trecho =====
        trecho = self._trechos.buscar(trecho_id)
        if trecho is None:
            raise TrechoNaoEncontrado(trecho_id)

        # ===== BLOCO 2: registrar_e_salvar =====
        medicao = Medicao(data, AlturaVegetacao(altura_cm), responsavel)
        trecho.registrar_medicao(medicao)
        self._trechos.salvar(trecho)
        return medicao
