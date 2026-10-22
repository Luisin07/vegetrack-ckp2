"""
consultar_fila.py
Caso de uso US-06 (RF-09): trechos ordenados do mais crítico ao menos crítico, com filtros.
"""

import math
from datetime import date
from pathlib import Path

from vegetrack.adaptadores.armazenamento_em_arquivo import ArmazenamentoEmArquivo
from vegetrack.monitoramento.dominio.avaliacao_de_risco import (
    DIAS_PARA_ATENCAO,
    DIAS_PARA_CRITICO,
    LIMITE_CONTRATUAL_CM,
    AvaliacaoDeRisco,
    NivelDeRisco,
)
from vegetrack.monitoramento.dominio.trecho import Trecho


class ConsultarFilaDeTrechos:
    def __init__(self, caminho_dos_dados: Path) -> None:
        self._caminho_dos_dados = caminho_dos_dados

    def executar(
        self,
        hoje: date,
        km_inicial: float | None = None,
        km_final: float | None = None,
        sentido: str | None = None,
    ) -> list[AvaliacaoDeRisco]:
        # ===== BLOCO 1: filtrar_trechos =====
        dados = ArmazenamentoEmArquivo(self._caminho_dos_dados)
        trechos = [
            t
            for t in dados.trechos.values()
            if t.medicoes
            and t.contem_km(km_inicial, km_final)
            and (sentido is None or t.sentido.lower() == sentido.lower())
        ]

        # ===== BLOCO 2: ordenar_por_criticidade =====
        avaliacoes = [self._avaliar(t, hoje) for t in trechos]
        return sorted(avaliacoes, key=_criterio_da_fila)

    def _avaliar(self, trecho: Trecho, hoje: date) -> AvaliacaoDeRisco:
        medicoes = trecho.medicoes
        ultima = medicoes[-1]
        altura = ultima.altura.centimetros
        taxa = None
        if len(medicoes) >= 2:
            anterior = medicoes[-2]
            taxa = (altura - anterior.altura.centimetros) / (ultima.data - anterior.data).days
        dias_ate_limite = None
        if altura >= LIMITE_CONTRATUAL_CM:
            dias_ate_limite = 0
        elif taxa is not None and taxa > 0:
            dias_ate_limite = math.floor((LIMITE_CONTRATUAL_CM - altura) / taxa)
        if altura >= LIMITE_CONTRATUAL_CM or (
            dias_ate_limite is not None and dias_ate_limite <= DIAS_PARA_CRITICO
        ):
            nivel = NivelDeRisco.CRITICO
        elif dias_ate_limite is not None and dias_ate_limite <= DIAS_PARA_ATENCAO:
            nivel = NivelDeRisco.ATENCAO
        else:
            nivel = NivelDeRisco.CONFORME
        return AvaliacaoDeRisco(
            trecho.identificacao, hoje, ultima.data, ultima.altura, taxa, dias_ate_limite, nivel
        )


def _criterio_da_fila(avaliacao: AvaliacaoDeRisco) -> tuple:
    # mais crítico primeiro; empate decidido por quem estoura o limite antes e depois pela altura
    dias = avaliacao.dias_ate_o_limite if avaliacao.dias_ate_o_limite is not None else 10**6
    return (-avaliacao.nivel, dias, -avaliacao.altura.centimetros, avaliacao.trecho_id)
