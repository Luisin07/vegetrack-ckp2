"""
indice_de_saude.py
Value object que resume a rodovia numa nota de 0 a 100 (RF-11) -- exibido ao gestor de contrato.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from vegetrack.monitoramento.dominio.avaliacao_de_risco import AvaliacaoDeRisco, NivelDeRisco

LIMITE_CONTRATUAL_DO_INDICE_CM = 30.0
TAXA_DE_CRESCIMENTO_ACELERADO_CM_POR_DIA = 1.0
PESO_CONFORMIDADE = 50
PESO_TRECHOS_NAO_CRITICOS = 30
PESO_CRESCIMENTO_CONTROLADO = 20


class IndiceIndisponivel(ValueError):
    """Não há trechos avaliados para compor o índice."""


@dataclass(frozen=True)
class IndiceDeSaude:
    valor: int

    def __post_init__(self) -> None:
        if not 0 <= self.valor <= 100:
            raise ValueError(f"Índice de saúde deve estar entre 0 e 100, recebido {self.valor}.")

    @classmethod
    def calcular(cls, avaliacoes: Sequence[AvaliacaoDeRisco]) -> "IndiceDeSaude":
        # ===== BLOCO 1: guarda_sem_trechos =====
        if not avaliacoes:
            raise IndiceIndisponivel("Nenhum trecho avaliado para compor o índice de saúde.")

        # ===== BLOCO 2: proporcoes_por_criterio =====
        total = len(avaliacoes)
        conformes = sum(a.altura.centimetros < LIMITE_CONTRATUAL_DO_INDICE_CM for a in avaliacoes)
        nao_criticos = sum(a.nivel != NivelDeRisco.CRITICO for a in avaliacoes)
        crescimento_controlado = sum(
            not a.taxa_disponivel or a.taxa_cm_por_dia < TAXA_DE_CRESCIMENTO_ACELERADO_CM_POR_DIA
            for a in avaliacoes
        )

        # ===== BLOCO 3: media_ponderada =====
        pontos = (
            PESO_CONFORMIDADE * conformes
            + PESO_TRECHOS_NAO_CRITICOS * nao_criticos
            + PESO_CRESCIMENTO_CONTROLADO * crescimento_controlado
        ) / total
        return cls(round(pontos))
