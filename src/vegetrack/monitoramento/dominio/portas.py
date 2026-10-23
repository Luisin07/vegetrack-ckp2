"""
portas.py
Portas de saída do contexto de Monitoramento -- o que o domínio precisa do mundo externo.
Implementadas em vegetrack.adaptadores; o domínio nunca conhece a implementação.
"""

from abc import ABC, abstractmethod

from vegetrack.monitoramento.dominio.trecho import Trecho


class RepositorioDeTrechos(ABC):
    @abstractmethod
    def buscar(self, identificacao: str) -> Trecho | None: ...

    @abstractmethod
    def salvar(self, trecho: Trecho) -> None: ...

    @abstractmethod
    def listar(self) -> list[Trecho]: ...
