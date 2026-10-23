"""Regras de avaliação no próprio domínio (RF-03 a RF-05) — sem arquivo, banco ou caso de uso."""

from datetime import date

import pytest

from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.avaliacao_de_risco import NivelDeRisco
from vegetrack.monitoramento.dominio.marco_quilometrico import MarcoQuilometrico
from vegetrack.monitoramento.dominio.medicao import Medicao
from vegetrack.monitoramento.dominio.trecho import Trecho, TrechoSemMedicao

HOJE = date(2026, 9, 9)


def _trecho_com(*medicoes: tuple[int, float]) -> Trecho:
    trecho = Trecho("RD-001", MarcoQuilometrico(0, 0), MarcoQuilometrico(0, 500), "Norte")
    for dia, altura in medicoes:
        trecho.registrar_medicao(Medicao(date(2026, 9, dia), AlturaVegetacao(altura), "Ana"))
    return trecho


def test_taxa_de_crescimento_em_cm_por_dia_entre_as_duas_ultimas_medicoes():
    assert _trecho_com((1, 18.0), (9, 26.0)).taxa_de_crescimento() == pytest.approx(1.0)


def test_taxa_negativa_quando_a_vegetacao_foi_rocada_entre_medicoes():
    assert _trecho_com((1, 28.0), (5, 4.0)).taxa_de_crescimento() == pytest.approx(-6.0)


def test_sem_segunda_medicao_nao_ha_taxa():
    assert _trecho_com((1, 18.0)).taxa_de_crescimento() is None


def test_avaliacao_usa_a_ultima_medicao_e_a_data_de_referencia():
    avaliacao = _trecho_com((1, 18.0), (9, 26.0)).avaliar(HOJE)

    assert avaliacao.altura == AlturaVegetacao(26.0)
    assert avaliacao.data_da_medicao == date(2026, 9, 9)
    assert avaliacao.dias_ate_o_limite == 4
    assert avaliacao.nivel is NivelDeRisco.ATENCAO
    assert avaliacao.exige_ordem_de_servico and not avaliacao.violou_limite


def test_avaliacao_no_limite_exato_ja_e_violacao():
    avaliacao = _trecho_com((9, 30.0)).avaliar(HOJE)

    assert avaliacao.violou_limite
    assert avaliacao.nivel is NivelDeRisco.CRITICO


def test_trecho_sem_medicao_nao_pode_ser_avaliado():
    with pytest.raises(TrechoSemMedicao):
        _trecho_com().avaliar(HOJE)
