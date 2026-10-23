"""
portas.py
Portas de saída do contexto de Manutenção -- o que o domínio precisa do mundo externo.
Implementadas em vegetrack.adaptadores; o domínio nunca conhece a implementação.
"""

from abc import ABC, abstractmethod

from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual


class RepositorioDeOrdens(ABC):
    @abstractmethod
    def proximo_numero(self) -> str: ...

    @abstractmethod
    def buscar(self, numero: str) -> OrdemDeServico | None: ...

    @abstractmethod
    def aberta_do_trecho(self, trecho_id: str) -> OrdemDeServico | None: ...

    @abstractmethod
    def salvar(self, ordem: OrdemDeServico) -> None: ...

    @abstractmethod
    def listar(self) -> list[OrdemDeServico]: ...


class RepositorioDeViolacoes(ABC):
    @abstractmethod
    def ativa_do_trecho(self, trecho_id: str) -> ViolacaoContratual | None: ...

    @abstractmethod
    def salvar(self, violacao: ViolacaoContratual) -> None: ...

    @abstractmethod
    def listar(self) -> list[ViolacaoContratual]: ...
