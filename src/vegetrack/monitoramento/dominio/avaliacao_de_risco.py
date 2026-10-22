"""
avaliacao_de_risco.py
Resultado da avaliação de um trecho diante do limite contratual -- usado pela fila e pelo índice.
Classificação de RF-04/RF-05: crítico, em atenção ou conforme.
"""

import math
from dataclasses import dataclass
from datetime import date
from enum import IntEnum

from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao

LIMITE_CONTRATUAL_CM = 30.0
DIAS_PARA_CRITICO = 2
DIAS_PARA_ATENCAO = 7


class NivelDeRisco(IntEnum):
    CONFORME = 0
    ATENCAO = 1
    CRITICO = 2


@dataclass(frozen=True)
class AvaliacaoDeRisco:
    trecho_id: str
    data_da_avaliacao: date
    data_da_medicao: date
    altura: AlturaVegetacao
    taxa_cm_por_dia: float | None
    dias_ate_o_limite: int | None
    nivel: NivelDeRisco

    @classmethod
    def classificar(
        cls,
        trecho_id: str,
        hoje: date,
        data_da_medicao: date,
        altura: AlturaVegetacao,
        taxa_cm_por_dia: float | None,
    ) -> "AvaliacaoDeRisco":
        dias = _dias_ate_o_limite(altura.centimetros, taxa_cm_por_dia)
        nivel = _nivel(altura.centimetros, dias)
        return cls(trecho_id, hoje, data_da_medicao, altura, taxa_cm_por_dia, dias, nivel)

    @property
    def taxa_disponivel(self) -> bool:
        return self.taxa_cm_por_dia is not None

    @property
    def violou_limite(self) -> bool:
        return self.altura.centimetros >= LIMITE_CONTRATUAL_CM

    @property
    def exige_ordem_de_servico(self) -> bool:
        return self.nivel is not NivelDeRisco.CONFORME


def _dias_ate_o_limite(altura_cm: float, taxa: float | None) -> int | None:
    if altura_cm >= LIMITE_CONTRATUAL_CM:
        return 0
    # sem crescimento a vegetação nunca atinge o limite: não há projeção
    if taxa is None or taxa <= 0:
        return None
    return math.floor((LIMITE_CONTRATUAL_CM - altura_cm) / taxa)


def _nivel(altura_cm: float, dias: int | None) -> NivelDeRisco:
    if altura_cm >= LIMITE_CONTRATUAL_CM or (dias is not None and dias <= DIAS_PARA_CRITICO):
        return NivelDeRisco.CRITICO
    if dias is not None and dias <= DIAS_PARA_ATENCAO:
        return NivelDeRisco.ATENCAO
    return NivelDeRisco.CONFORME
