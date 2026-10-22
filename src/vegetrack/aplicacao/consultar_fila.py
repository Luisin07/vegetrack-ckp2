"""
consultar_fila.py
Caso de uso US-06 (RF-09): trechos ordenados do mais crítico ao menos crítico, com filtros.
"""

from datetime import date

from vegetrack.monitoramento.dominio.avaliacao_de_risco import AvaliacaoDeRisco
from vegetrack.monitoramento.dominio.portas import RepositorioDeTrechos


class ConsultarFilaDeTrechos:
    def __init__(self, trechos: RepositorioDeTrechos) -> None:
        self._trechos = trechos

    def executar(
        self,
        hoje: date,
        km_inicial: float | None = None,
        km_final: float | None = None,
        sentido: str | None = None,
    ) -> list[AvaliacaoDeRisco]:
        # ===== BLOCO 1: filtrar_trechos =====
        trechos = [
            t
            for t in self._trechos.listar()
            if t.medicoes
            and t.contem_km(km_inicial, km_final)
            and (sentido is None or t.sentido.lower() == sentido.lower())
        ]

        # ===== BLOCO 2: ordenar_por_criticidade =====
        avaliacoes = [t.avaliar(hoje) for t in trechos]
        return sorted(avaliacoes, key=_criterio_da_fila)


def _criterio_da_fila(avaliacao: AvaliacaoDeRisco) -> tuple:
    # mais crítico primeiro; empate decidido por quem estoura o limite antes e depois pela altura
    dias = avaliacao.dias_ate_o_limite if avaliacao.dias_ate_o_limite is not None else 10**6
    return (-avaliacao.nivel, dias, -avaliacao.altura.centimetros, avaliacao.trecho_id)
