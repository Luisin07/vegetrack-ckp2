"""
importar_levantamento.py
Caso de uso RF-02: importa em lote as linhas de um levantamento, rejeitando as inválidas.
A leitura do arquivo CSV fica no adaptador importador_csv.py.
"""

from dataclasses import dataclass, field
from datetime import date

from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.marco_quilometrico import MarcoQuilometrico
from vegetrack.monitoramento.dominio.medicao import Medicao
from vegetrack.monitoramento.dominio.portas import RepositorioDeTrechos
from vegetrack.monitoramento.dominio.trecho import Trecho


@dataclass(frozen=True)
class LinhaDeLevantamento:
    numero: int
    trecho: str
    marco_inicial: str
    marco_final: str
    sentido: str
    data: str
    altura_cm: str
    responsavel: str


@dataclass
class ResultadoDaImportacao:
    importadas: int = 0
    rejeitadas: list[str] = field(default_factory=list)


class ImportarLevantamento:
    def __init__(self, trechos: RepositorioDeTrechos) -> None:
        self._trechos = trechos

    def executar(self, linhas: list[LinhaDeLevantamento]) -> ResultadoDaImportacao:
        resultado = ResultadoDaImportacao()

        # ===== BLOCO 1: importar_linha_a_linha =====
        for linha in linhas:
            # linha inválida é rejeitada com motivo, sem abortar o lote (RF-02)
            try:
                trecho = self._trechos.buscar(linha.trecho) or _novo_trecho(linha)
                trecho.registrar_medicao(_medicao(linha))
            except ValueError as erro:
                resultado.rejeitadas.append(f"linha {linha.numero}: {erro}")
                continue
            self._trechos.salvar(trecho)
            resultado.importadas += 1
        return resultado


def _novo_trecho(linha: LinhaDeLevantamento) -> Trecho:
    return Trecho(
        linha.trecho,
        MarcoQuilometrico.de_texto(linha.marco_inicial),
        MarcoQuilometrico.de_texto(linha.marco_final),
        linha.sentido,
    )


def _medicao(linha: LinhaDeLevantamento) -> Medicao:
    altura = AlturaVegetacao(float(linha.altura_cm.replace(",", ".")))
    return Medicao(date.fromisoformat(linha.data), altura, linha.responsavel)
