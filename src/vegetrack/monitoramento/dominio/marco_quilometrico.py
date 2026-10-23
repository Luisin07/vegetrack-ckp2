"""
marco_quilometrico.py
Value object da posição na rodovia (ex.: KM 29+300) -- delimita o início e o fim de um Trecho.
"""

import re
from dataclasses import dataclass

_FORMATO = re.compile(r"^\s*(?:KM\s*)?(\d{1,4})\+(\d{1,3})\s*$", re.IGNORECASE)


class MarcoInvalido(ValueError):
    """Marco quilométrico em formato ou valor inválido."""


@dataclass(frozen=True, order=True)
class MarcoQuilometrico:
    km: int
    metro: int = 0

    def __post_init__(self) -> None:
        if self.km < 0 or not 0 <= self.metro <= 999:
            raise MarcoInvalido(f"Marco KM {self.km}+{self.metro} fora da faixa válida.")

    @classmethod
    def de_texto(cls, texto: str) -> "MarcoQuilometrico":
        correspondencia = _FORMATO.match(texto)
        if correspondencia is None:
            raise MarcoInvalido(f"'{texto}' não está no formato KM+metro (ex.: 29+300).")
        return cls(km=int(correspondencia.group(1)), metro=int(correspondencia.group(2)))

    @property
    def em_metros(self) -> int:
        return self.km * 1000 + self.metro

    def __str__(self) -> str:
        return f"KM {self.km}+{self.metro:03d}"
