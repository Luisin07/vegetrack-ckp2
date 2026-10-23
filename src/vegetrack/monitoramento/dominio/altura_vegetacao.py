"""
altura_vegetacao.py
Value object da altura da vegetação, em centímetros -- usado por Medicao e pela avaliação de risco.
Implementa a RN-02 do Checkpoint 1.
"""

import math
from dataclasses import dataclass

ALTURA_MINIMA_CM = 0.0
ALTURA_MAXIMA_CM = 300.0


class AlturaInvalida(ValueError):
    """Altura fora da faixa admitida para uma medição de campo."""


@dataclass(frozen=True, order=True)
class AlturaVegetacao:
    centimetros: float

    def __post_init__(self) -> None:
        # RN-02: fora de 0..300 cm é erro de leitura em campo, não vegetação real
        if math.isnan(self.centimetros) or not (
            ALTURA_MINIMA_CM <= self.centimetros <= ALTURA_MAXIMA_CM
        ):
            raise AlturaInvalida(
                f"Altura de {self.centimetros} cm é inválida: deve estar entre "
                f"{ALTURA_MINIMA_CM:g} e {ALTURA_MAXIMA_CM:g} cm."
            )

    def __str__(self) -> str:
        return f"{self.centimetros:g} cm"
