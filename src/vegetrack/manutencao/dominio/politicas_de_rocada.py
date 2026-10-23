"""
politicas_de_rocada.py
Padrão Strategy: cada política de roçada sabe para qual altura serve e como planejar o serviço.
Usado por OrdemDeServico.emitir através do SeletorDePoliticaDeRocada (papel de Context).
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

EPI_BASICO = ("capacete", "protetor auricular", "óculos de proteção", "perneira", "luvas")
ALTURA_MAXIMA_ROCADA_MANUAL_CM = 50.0
ALTURA_MAXIMA_ROCADA_MECANIZADA_CM = 100.0


@dataclass(frozen=True)
class PlanoDeRocada:
    metodo: str
    equipes_necessarias: int
    epi_obrigatorio: tuple[str, ...]


class SemPoliticaDeRocada(ValueError):
    """Nenhuma política cadastrada atende à altura informada."""


# ===== BLOCO 1: strategy =====
class PoliticaDeRocada(ABC):
    @abstractmethod
    def aplica_se_a(self, altura_cm: float) -> bool: ...

    @abstractmethod
    def planejar(self, altura_cm: float) -> PlanoDeRocada: ...


# ===== BLOCO 2: concrete_strategies =====
class RocadaManual(PoliticaDeRocada):
    def aplica_se_a(self, altura_cm: float) -> bool:
        return altura_cm <= ALTURA_MAXIMA_ROCADA_MANUAL_CM

    def planejar(self, altura_cm: float) -> PlanoDeRocada:
        return PlanoDeRocada("Roçada manual com roçadeira costal", 1, EPI_BASICO)


class RocadaMecanizada(PoliticaDeRocada):
    def aplica_se_a(self, altura_cm: float) -> bool:
        return ALTURA_MAXIMA_ROCADA_MANUAL_CM < altura_cm <= ALTURA_MAXIMA_ROCADA_MECANIZADA_CM

    def planejar(self, altura_cm: float) -> PlanoDeRocada:
        # trator na faixa de domínio expõe a equipe ao tráfego: colete refletivo obrigatório
        return PlanoDeRocada(
            "Roçada mecanizada com trator e roçadeira acoplada",
            2,
            EPI_BASICO + ("colete refletivo",),
        )


class RocadaMecanizadaPesada(PoliticaDeRocada):
    def aplica_se_a(self, altura_cm: float) -> bool:
        return altura_cm > ALTURA_MAXIMA_ROCADA_MECANIZADA_CM

    def planejar(self, altura_cm: float) -> PlanoDeRocada:
        return PlanoDeRocada(
            "Roçada mecanizada pesada com trator e apoio manual",
            3,
            EPI_BASICO + ("colete refletivo", "máscara contra poeira"),
        )


# ===== BLOCO 3: context =====
class SeletorDePoliticaDeRocada:
    def __init__(self, politicas: Sequence[PoliticaDeRocada]) -> None:
        if not politicas:
            raise ValueError("O seletor precisa de ao menos uma política de roçada.")
        self._politicas = tuple(politicas)

    def planejar(self, altura_cm: float) -> PlanoDeRocada:
        # a primeira política que aceitar a altura vence: a ordem da lista é a prioridade
        for politica in self._politicas:
            if politica.aplica_se_a(altura_cm):
                return politica.planejar(altura_cm)
        raise SemPoliticaDeRocada(f"Nenhuma política de roçada atende {altura_cm:g} cm.")


# imutável e sem estado: compartilhar a instância não cria acoplamento global (não é Singleton)
SELETOR_PADRAO = SeletorDePoliticaDeRocada(
    [RocadaManual(), RocadaMecanizada(), RocadaMecanizadaPesada()]
)
