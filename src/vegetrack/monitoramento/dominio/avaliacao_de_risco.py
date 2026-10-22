"""
avaliacao_de_risco.py
Resultado da avaliação de um trecho diante do limite contratual -- usado pela fila e pelo índice.
"""

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

    @property
    def taxa_disponivel(self) -> bool:
        return self.taxa_cm_por_dia is not None
