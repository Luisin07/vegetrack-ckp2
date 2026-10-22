from datetime import date

import pytest

from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.marco_quilometrico import MarcoQuilometrico
from vegetrack.monitoramento.dominio.medicao import Medicao, MedicaoInvalida
from vegetrack.monitoramento.dominio.trecho import Trecho, TrechoInvalido


def _trecho() -> Trecho:
    return Trecho("RD-001", MarcoQuilometrico(10, 0), MarcoQuilometrico(10, 500), "Norte")


def _medicao(dia: int, altura_cm: float) -> Medicao:
    return Medicao(date(2026, 9, dia), AlturaVegetacao(altura_cm), "Marcos Ribeiro")


def test_mantem_o_historico_de_medicoes_em_ordem_cronologica():
    trecho = _trecho()

    trecho.registrar_medicao(_medicao(9, 26.0))
    trecho.registrar_medicao(_medicao(1, 18.0))

    assert [m.data.day for m in trecho.medicoes] == [1, 9]
    assert trecho.ultima_medicao.altura == AlturaVegetacao(26.0)


def test_segunda_medicao_na_mesma_data_substitui_a_primeira():
    trecho = _trecho()

    trecho.registrar_medicao(_medicao(1, 18.0))
    trecho.registrar_medicao(_medicao(1, 21.0))

    assert len(trecho.medicoes) == 1
    assert trecho.ultima_medicao.altura == AlturaVegetacao(21.0)


def test_trecho_sem_medicao_nao_tem_ultima_medicao():
    assert _trecho().ultima_medicao is None


def test_nao_permite_trecho_com_marco_final_antes_do_inicial():
    with pytest.raises(TrechoInvalido):
        Trecho("RD-002", MarcoQuilometrico(10, 500), MarcoQuilometrico(10, 0), "Norte")


def test_nao_permite_trecho_sem_identificacao():
    with pytest.raises(TrechoInvalido):
        Trecho("  ", MarcoQuilometrico(1, 0), MarcoQuilometrico(2, 0), "Norte")


def test_nao_permite_medicao_sem_responsavel():
    with pytest.raises(MedicaoInvalida):
        Medicao(date(2026, 9, 1), AlturaVegetacao(10.0), "   ")


def test_trechos_com_mesma_identificacao_sao_o_mesmo_trecho():
    outro = Trecho("RD-001", MarcoQuilometrico(0, 0), MarcoQuilometrico(0, 100), "Sul")

    assert _trecho() == outro
    assert len({_trecho(), outro}) == 1


@pytest.mark.parametrize(
    ("km_inicial", "km_final", "esperado"),
    [(None, None, True), (5, 15, True), (11, None, False), (None, 9, False), (10, 10, True)],
)
def test_filtra_trecho_pela_faixa_de_quilometragem(km_inicial, km_final, esperado):
    assert _trecho().contem_km(km_inicial, km_final) is esperado
