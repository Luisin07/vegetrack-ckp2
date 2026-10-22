"""
plano_de_regularizacao.py
Value object com a prioridade e o prazo da ordem de serviço -- decide quão rápido roçar o trecho.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from vegetrack.manutencao.dominio.ordem_de_servico import LIMITE_CONTRATUAL_CM, Prioridade
from vegetrack.manutencao.dominio.prazo_legal import (
    ORIGEM_CONTRATUAL,
    ORIGEM_PROJECAO,
    PRAZO_CONTRATUAL_DE_REGULARIZACAO,
    PrazoLegal,
)


@dataclass(frozen=True)
class PlanoDeRegularizacao:
    prioridade: Prioridade
    prazo: PrazoLegal

    @classmethod
    def para(
        cls,
        altura_cm: float,
        data_da_medicao: date,
        dias_ate_o_limite: int | None,
        critico: bool,
    ) -> "PlanoDeRegularizacao":
        # ===== BLOCO 1: limite_ja_violado =====
        # já acima de 30 cm: vale o prazo contratual de 48 h contado da medição
        if altura_cm >= LIMITE_CONTRATUAL_CM:
            prazo = PrazoLegal(
                data_da_medicao + PRAZO_CONTRATUAL_DE_REGULARIZACAO, ORIGEM_CONTRATUAL
            )
            return cls(Prioridade.URGENTE, prazo)

        # ===== BLOCO 2: limite_projetado =====
        prazo = PrazoLegal(data_da_medicao + timedelta(days=dias_ate_o_limite), ORIGEM_PROJECAO)
        return cls(Prioridade.ALTA if critico else Prioridade.NORMAL, prazo)
