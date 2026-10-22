"""
violacao_contratual.py
Entidade da violação do limite de 30 cm perante o órgão regulador -- RN-05 do Checkpoint 1.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum

from vegetrack.manutencao.dominio.prazo_legal import PrazoLegal


class SituacaoDaViolacao(Enum):
    IMINENTE = "Iminente"
    CONFIGURADA = "Configurada"
    REGULARIZADA = "Regularizada"


@dataclass
class ViolacaoContratual:
    trecho_id: str
    orgao_regulador: str
    altura_apurada_cm: float
    prazo_de_regularizacao: PrazoLegal
    situacao: SituacaoDaViolacao = SituacaoDaViolacao.IMINENTE

    @property
    def ativa(self) -> bool:
        return self.situacao is not SituacaoDaViolacao.REGULARIZADA

    def apurar(self, hoje: date) -> None:
        # RN-05: prazo vencido sem regularização configura a violação, sujeita a multa
        prazo_vencido = self.prazo_de_regularizacao.vencido_em(hoje)
        if self.situacao is SituacaoDaViolacao.IMINENTE and prazo_vencido:
            self.situacao = SituacaoDaViolacao.CONFIGURADA

    def regularizar(self) -> None:
        self.situacao = SituacaoDaViolacao.REGULARIZADA
