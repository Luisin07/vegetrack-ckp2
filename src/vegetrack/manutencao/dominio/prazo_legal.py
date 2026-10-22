"""
prazo_legal.py
Value object da data-limite para regularizar um trecho e da sua origem contratual.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, order=True)
class PrazoLegal:
    data_limite: date
    origem: str

    def vencido_em(self, hoje: date) -> bool:
        return hoje > self.data_limite

    def dias_restantes(self, hoje: date) -> int:
        return (self.data_limite - hoje).days

    def __str__(self) -> str:
        return f"{self.data_limite:%d/%m/%Y} ({self.origem})"
