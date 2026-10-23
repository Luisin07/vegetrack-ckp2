"""
repositorios_em_memoria.py
Adaptadores de saída em memória -- usados nos testes e quando não se quer persistir nada.
Implementam as mesmas portas que os repositórios em arquivo.
"""

from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico
from vegetrack.manutencao.dominio.portas import RepositorioDeOrdens, RepositorioDeViolacoes
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual
from vegetrack.monitoramento.dominio.portas import RepositorioDeTrechos
from vegetrack.monitoramento.dominio.trecho import Trecho


class RepositorioDeTrechosEmMemoria(RepositorioDeTrechos):
    def __init__(self) -> None:
        self._trechos: dict[str, Trecho] = {}

    def buscar(self, identificacao: str) -> Trecho | None:
        return self._trechos.get(identificacao)

    def salvar(self, trecho: Trecho) -> None:
        self._trechos[trecho.identificacao] = trecho

    def listar(self) -> list[Trecho]:
        return list(self._trechos.values())


class RepositorioDeOrdensEmMemoria(RepositorioDeOrdens):
    def __init__(self) -> None:
        self._ordens: dict[str, OrdemDeServico] = {}

    def proximo_numero(self) -> str:
        return f"OS-{len(self._ordens) + 1:04d}"

    def buscar(self, numero: str) -> OrdemDeServico | None:
        return self._ordens.get(numero)

    def aberta_do_trecho(self, trecho_id: str) -> OrdemDeServico | None:
        return next(
            (o for o in self._ordens.values() if o.trecho_id == trecho_id and o.em_aberto), None
        )

    def salvar(self, ordem: OrdemDeServico) -> None:
        self._ordens[ordem.numero] = ordem

    def listar(self) -> list[OrdemDeServico]:
        return list(self._ordens.values())


class RepositorioDeViolacoesEmMemoria(RepositorioDeViolacoes):
    def __init__(self) -> None:
        self._violacoes: list[ViolacaoContratual] = []

    def ativa_do_trecho(self, trecho_id: str) -> ViolacaoContratual | None:
        return next((v for v in self._violacoes if v.trecho_id == trecho_id and v.ativa), None)

    def salvar(self, violacao: ViolacaoContratual) -> None:
        # identidade, não igualdade: duas violações com os mesmos dados são registros distintos
        if all(existente is not violacao for existente in self._violacoes):
            self._violacoes.append(violacao)

    def listar(self) -> list[ViolacaoContratual]:
        return list(self._violacoes)
