"""
Testes de contrato das portas de repositório.
Os mesmos testes rodam contra o adaptador em memória e o em arquivo: prova de que são trocáveis.
"""

from datetime import date

import pytest

from vegetrack.adaptadores.repositorios_em_arquivo import (
    RepositorioDeOrdensEmArquivo,
    RepositorioDeTrechosEmArquivo,
    RepositorioDeViolacoesEmArquivo,
)
from vegetrack.adaptadores.repositorios_em_memoria import (
    RepositorioDeOrdensEmMemoria,
    RepositorioDeTrechosEmMemoria,
    RepositorioDeViolacoesEmMemoria,
)
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico, Prioridade
from vegetrack.manutencao.dominio.prazo_legal import PrazoLegal
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual
from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.marco_quilometrico import MarcoQuilometrico
from vegetrack.monitoramento.dominio.medicao import Medicao
from vegetrack.monitoramento.dominio.trecho import Trecho

PRAZO = PrazoLegal(date(2026, 9, 11), "Contrato ARTESP — 48 h")


@pytest.fixture(params=["memoria", "arquivo"])
def repositorios(request, tmp_path):
    if request.param == "memoria":
        return (
            RepositorioDeTrechosEmMemoria(),
            RepositorioDeOrdensEmMemoria(),
            RepositorioDeViolacoesEmMemoria(),
        )
    return (
        RepositorioDeTrechosEmArquivo(tmp_path),
        RepositorioDeOrdensEmArquivo(tmp_path),
        RepositorioDeViolacoesEmArquivo(tmp_path),
    )


def _trecho(identificacao: str = "RD-001") -> Trecho:
    trecho = Trecho(identificacao, MarcoQuilometrico(1, 0), MarcoQuilometrico(1, 500), "Norte")
    trecho.registrar_medicao(Medicao(date(2026, 9, 9), AlturaVegetacao(31.5), "Ana"))
    return trecho


def _ordem(numero: str, trecho_id: str = "RD-001") -> OrdemDeServico:
    return OrdemDeServico.emitir(numero, trecho_id, 31.5, Prioridade.URGENTE, PRAZO)


def test_trecho_salvo_e_encontrado_com_o_historico(repositorios):
    trechos, _, _ = repositorios

    trechos.salvar(_trecho())

    encontrado = trechos.buscar("RD-001")
    assert encontrado.ultima_medicao.altura == AlturaVegetacao(31.5)
    assert trechos.buscar("RD-404") is None
    assert len(trechos.listar()) == 1


def test_numeracao_de_ordens_e_sequencial(repositorios):
    _, ordens, _ = repositorios

    ordens.salvar(_ordem(ordens.proximo_numero()))

    assert ordens.proximo_numero() == "OS-0002"


def test_so_a_ordem_em_aberto_e_devolvida_para_o_trecho(repositorios):
    _, ordens, _ = repositorios
    concluida = _ordem("OS-0001")
    concluida.concluir(5.0)
    ordens.salvar(concluida)
    ordens.salvar(_ordem("OS-0002"))

    assert ordens.aberta_do_trecho("RD-001").numero == "OS-0002"
    assert ordens.aberta_do_trecho("RD-999") is None
    assert ordens.buscar("OS-0001").altura_comprovada_cm == 5.0


def test_so_a_violacao_ativa_e_devolvida_para_o_trecho(repositorios):
    _, _, violacoes = repositorios
    regularizada = ViolacaoContratual("RD-001", "ARTESP", 34.0, PRAZO)
    regularizada.regularizar()
    ativa = ViolacaoContratual("RD-001", "ARTESP", 34.0, PRAZO)

    violacoes.salvar(regularizada)
    violacoes.salvar(ativa)
    violacoes.salvar(ativa)

    assert violacoes.ativa_do_trecho("RD-001").ativa
    assert len(violacoes.listar()) == 2


def test_repositorios_em_arquivo_recarregam_o_que_foi_gravado(tmp_path):
    RepositorioDeTrechosEmArquivo(tmp_path).salvar(_trecho())
    RepositorioDeOrdensEmArquivo(tmp_path).salvar(_ordem("OS-0001"))
    RepositorioDeViolacoesEmArquivo(tmp_path).salvar(
        ViolacaoContratual("RD-001", "ARTESP", 34.0, PRAZO)
    )

    assert RepositorioDeTrechosEmArquivo(tmp_path).buscar("RD-001").medicoes
    assert RepositorioDeOrdensEmArquivo(tmp_path).buscar("OS-0001").prazo == PRAZO
    assert RepositorioDeViolacoesEmArquivo(tmp_path).ativa_do_trecho("RD-001").orgao_regulador == (
        "ARTESP"
    )
