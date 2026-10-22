"""
medicao.py
Registro da altura da vegetação de um trecho em uma data -- só existe dentro do agregado Trecho.
"""

from dataclasses import dataclass
from datetime import date

from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao


class MedicaoInvalida(ValueError):
    """Medição sem os dados mínimos exigidos para entrar no histórico do trecho."""


@dataclass(frozen=True)
class Medicao:
    data: date
    altura: AlturaVegetacao
    responsavel: str

    def __post_init__(self) -> None:
        # RNF-06: toda medição precisa de responsável para ser rastreável até a ordem que originar
        if not self.responsavel.strip():
            raise MedicaoInvalida("A medição precisa informar o responsável.")
