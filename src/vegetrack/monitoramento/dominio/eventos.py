"""
eventos.py
Evento de domínio publicado pelo Monitoramento quando um trecho é avaliado.
Linguagem publicada para o contexto de Manutenção: só dados primitivos, sem objetos do domínio.
"""

from dataclasses import dataclass
from datetime import date

from vegetrack.monitoramento.dominio.avaliacao_de_risco import AvaliacaoDeRisco, NivelDeRisco


@dataclass(frozen=True)
class TrechoAvaliado:
    trecho_id: str
    data_da_avaliacao: date
    data_da_medicao: date
    altura_cm: float
    dias_ate_o_limite: int | None
    critico: bool
    exige_ordem_de_servico: bool
    violou_limite: bool

    @classmethod
    def de(cls, avaliacao: AvaliacaoDeRisco) -> "TrechoAvaliado":
        return cls(
            trecho_id=avaliacao.trecho_id,
            data_da_avaliacao=avaliacao.data_da_avaliacao,
            data_da_medicao=avaliacao.data_da_medicao,
            altura_cm=avaliacao.altura.centimetros,
            dias_ate_o_limite=avaliacao.dias_ate_o_limite,
            critico=avaliacao.nivel is NivelDeRisco.CRITICO,
            exige_ordem_de_servico=avaliacao.exige_ordem_de_servico,
            violou_limite=avaliacao.violou_limite,
        )
