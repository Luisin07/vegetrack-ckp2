"""
conftest.py
Monta os casos de uso para os testes -- único ponto que sabe como as dependências são criadas.
"""

from dataclasses import dataclass

import pytest

from vegetrack.adaptadores.repositorios_em_memoria import (
    RepositorioDeOrdensEmMemoria,
    RepositorioDeTrechosEmMemoria,
    RepositorioDeViolacoesEmMemoria,
)
from vegetrack.aplicacao.avaliar_trecho import AvaliarTrecho
from vegetrack.aplicacao.calcular_indice import CalcularIndiceDeSaude
from vegetrack.aplicacao.concluir_ordem import ConcluirOrdemDeServico
from vegetrack.aplicacao.consultar_fila import ConsultarFilaDeTrechos
from vegetrack.aplicacao.importar_levantamento import ImportarLevantamento, LinhaDeLevantamento
from vegetrack.aplicacao.registrar_medicao import RegistrarMedicao


@dataclass
class Sistema:
    importar: ImportarLevantamento
    registrar: RegistrarMedicao
    avaliar: AvaliarTrecho
    fila: ConsultarFilaDeTrechos
    indice: CalcularIndiceDeSaude
    concluir: ConcluirOrdemDeServico

    def cadastrar(
        self,
        trecho_id: str,
        *medicoes: tuple[str, float],
        marco_inicial: str = "10+000",
        marco_final: str = "10+500",
        sentido: str = "Norte",
    ) -> None:
        linhas = [
            LinhaDeLevantamento(
                n, trecho_id, marco_inicial, marco_final, sentido, data, str(altura), "Marcos"
            )
            for n, (data, altura) in enumerate(medicoes, start=1)
        ]
        resultado = self.importar.executar(linhas)
        assert not resultado.rejeitadas, resultado.rejeitadas


@pytest.fixture
def sistema() -> Sistema:
    # adaptadores falsos em memória: casos de uso testados sem disco, banco nem servidor
    trechos = RepositorioDeTrechosEmMemoria()
    ordens = RepositorioDeOrdensEmMemoria()
    violacoes = RepositorioDeViolacoesEmMemoria()
    fila = ConsultarFilaDeTrechos(trechos)
    return Sistema(
        importar=ImportarLevantamento(trechos),
        registrar=RegistrarMedicao(trechos),
        avaliar=AvaliarTrecho(trechos, ordens, violacoes),
        fila=fila,
        indice=CalcularIndiceDeSaude(fila),
        concluir=ConcluirOrdemDeServico(trechos, ordens, violacoes),
    )
