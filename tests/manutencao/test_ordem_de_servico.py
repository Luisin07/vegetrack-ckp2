from datetime import date

import pytest

from vegetrack.manutencao.dominio.ordem_de_servico import (
    OperacaoNaoPermitida,
    OrdemDeServico,
    Prioridade,
    SituacaoDaOrdem,
)
from vegetrack.manutencao.dominio.prazo_legal import PrazoLegal

PRAZO = PrazoLegal(date(2026, 9, 11), "Contrato ARTESP — 48 h")


def _emitir(altura_cm: float = 35.0) -> OrdemDeServico:
    return OrdemDeServico.emitir("OS-0001", "RD-001", altura_cm, Prioridade.URGENTE, PRAZO)


@pytest.mark.parametrize(
    ("altura_cm", "metodo_esperado", "equipes"),
    [
        (30.0, "Roçada manual com roçadeira costal", 1),
        (50.0, "Roçada manual com roçadeira costal", 1),
        (50.1, "Roçada mecanizada com trator e roçadeira acoplada", 2),
        (100.0, "Roçada mecanizada com trator e roçadeira acoplada", 2),
        (100.1, "Roçada mecanizada pesada com trator e apoio manual", 3),
    ],
)
def test_metodo_de_rocada_e_equipes_dependem_da_altura(altura_cm, metodo_esperado, equipes):
    ordem = _emitir(altura_cm)

    assert ordem.metodo_de_rocada == metodo_esperado
    assert ordem.equipes_necessarias == equipes


def test_rocada_mecanizada_exige_colete_refletivo_e_a_pesada_exige_mascara():
    assert "colete refletivo" not in _emitir(40.0).epi_obrigatorio
    assert "colete refletivo" in _emitir(80.0).epi_obrigatorio
    assert "máscara contra poeira" in _emitir(150.0).epi_obrigatorio


def test_ordem_emitida_nasce_aberta_com_prioridade_e_prazo():
    ordem = _emitir()

    assert ordem.situacao is SituacaoDaOrdem.ABERTA
    assert ordem.prioridade is Prioridade.URGENTE
    assert ordem.prazo == PRAZO


def test_conclui_ordem_com_medicao_de_comprovacao_abaixo_do_limite():
    ordem = _emitir()

    ordem.concluir(altura_comprovada_cm=8.0)

    assert ordem.situacao is SituacaoDaOrdem.CONCLUIDA
    assert not ordem.em_aberto


@pytest.mark.parametrize("altura_cm", [30.0, 45.0])
def test_nao_permite_concluir_ordem_com_vegetacao_ainda_no_limite_ou_acima(altura_cm):
    ordem = _emitir()

    with pytest.raises(OperacaoNaoPermitida):
        ordem.concluir(altura_comprovada_cm=altura_cm)
    assert ordem.em_aberto


def test_nao_permite_concluir_duas_vezes():
    ordem = _emitir()
    ordem.concluir(5.0)

    with pytest.raises(OperacaoNaoPermitida):
        ordem.concluir(5.0)


def test_reavaliacao_atualiza_prioridade_e_prazo_da_ordem_aberta():
    ordem = _emitir()
    novo_prazo = PrazoLegal(date(2026, 9, 20), "Projeção de crescimento")

    ordem.reavaliar(Prioridade.ALTA, novo_prazo)

    assert ordem.prioridade is Prioridade.ALTA
    assert ordem.prazo == novo_prazo


def test_nao_permite_reavaliar_ordem_concluida():
    ordem = _emitir()
    ordem.concluir(5.0)

    with pytest.raises(OperacaoNaoPermitida):
        ordem.reavaliar(Prioridade.NORMAL, PRAZO)


def test_execucao_so_comeca_a_partir_de_ordem_aberta():
    ordem = _emitir()
    ordem.iniciar_execucao()

    assert ordem.situacao is SituacaoDaOrdem.EM_EXECUCAO
    with pytest.raises(OperacaoNaoPermitida):
        ordem.iniciar_execucao()
