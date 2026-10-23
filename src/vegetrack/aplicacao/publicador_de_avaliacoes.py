"""
publicador_de_avaliacoes.py
Padrão Observer: o PublicadorDeAvaliacoes (Subject) avisa cada observador inscrito quando um
trecho é avaliado. Reações concretas em reacoes_da_manutencao.py e na CLI.
"""

from abc import ABC, abstractmethod

from vegetrack.monitoramento.dominio.eventos import TrechoAvaliado


class ObservadorDeAvaliacao(ABC):
    @abstractmethod
    def ao_avaliar(self, evento: TrechoAvaliado) -> None: ...


class PublicadorDeAvaliacoes:
    def __init__(self, observadores: list[ObservadorDeAvaliacao] | None = None) -> None:
        self._observadores: list[ObservadorDeAvaliacao] = list(observadores or [])

    def inscrever(self, observador: ObservadorDeAvaliacao) -> None:
        self._observadores.append(observador)

    def publicar(self, evento: TrechoAvaliado) -> None:
        # ordem de inscrição = ordem de reação; observadores não dependem uns dos outros
        for observador in self._observadores:
            observador.ao_avaliar(evento)
