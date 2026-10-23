"""
calcular_indice.py
Caso de uso US-07 (RF-11): índice de saúde de 0 a 100 da rodovia inteira.
"""

from datetime import date

from vegetrack.aplicacao.consultar_fila import ConsultarFilaDeTrechos
from vegetrack.monitoramento.dominio.indice_de_saude import IndiceDeSaude


class CalcularIndiceDeSaude:
    def __init__(self, fila: ConsultarFilaDeTrechos) -> None:
        self._fila = fila

    def executar(self, hoje: date) -> IndiceDeSaude:
        return IndiceDeSaude.calcular(self._fila.executar(hoje))
