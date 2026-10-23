"""US-01 (RF-01) e RF-02 — registro de medição e importação do levantamento."""

from datetime import date

import pytest

from vegetrack.aplicacao.erros import TrechoNaoEncontrado
from vegetrack.aplicacao.importar_levantamento import LinhaDeLevantamento
from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaInvalida, AlturaVegetacao


def test_registra_medicao_valida_no_historico_do_trecho(sistema):
    # Arrange
    sistema.cadastrar("RD-001", ("2026-09-01", 18))

    # Act
    sistema.registrar.executar("RD-001", date(2026, 9, 9), 24.0, "Marcos Ribeiro")

    # Assert
    fila = sistema.fila.executar(hoje=date(2026, 9, 9))
    assert fila[0].altura == AlturaVegetacao(24.0)
    assert fila[0].data_da_medicao == date(2026, 9, 9)


def test_nao_permite_medicao_com_altura_negativa(sistema):
    sistema.cadastrar("RD-001", ("2026-09-01", 18))

    with pytest.raises(AlturaInvalida):
        sistema.registrar.executar("RD-001", date(2026, 9, 9), -5.0, "Marcos Ribeiro")

    assert sistema.fila.executar(hoje=date(2026, 9, 9))[0].altura == AlturaVegetacao(18.0)


def test_nao_permite_medicao_em_trecho_inexistente(sistema):
    with pytest.raises(TrechoNaoEncontrado):
        sistema.registrar.executar("RD-999", date(2026, 9, 9), 10.0, "Marcos Ribeiro")


def test_importacao_rejeita_linhas_invalidas_sem_abortar_o_lote(sistema):
    linhas = [
        LinhaDeLevantamento(1, "RD-001", "1+000", "1+500", "Norte", "2026-09-01", "12", "Ana"),
        LinhaDeLevantamento(2, "RD-002", "2+000", "2+500", "Norte", "2026-09-01", "-3", "Ana"),
        LinhaDeLevantamento(3, "RD-003", "3+500", "3+000", "Sul", "2026-09-01", "10", "Ana"),
        LinhaDeLevantamento(4, "RD-004", "4+000", "4+500", "Sul", "01/09/2026", "10", "Ana"),
        LinhaDeLevantamento(5, "RD-005", "5+000", "5+500", "Sul", "2026-09-01", "15,5", "Ana"),
    ]

    resultado = sistema.importar.executar(linhas)

    assert resultado.importadas == 2
    assert [r.split(":")[0] for r in resultado.rejeitadas] == ["linha 2", "linha 3", "linha 4"]
    assert {a.trecho_id for a in sistema.fila.executar(date(2026, 9, 9))} == {"RD-001", "RD-005"}


def test_reimportar_o_mesmo_levantamento_nao_duplica_medicoes(sistema):
    sistema.cadastrar("RD-001", ("2026-09-01", 18), ("2026-09-09", 26))
    sistema.cadastrar("RD-001", ("2026-09-01", 18), ("2026-09-09", 26))

    avaliacao = sistema.fila.executar(date(2026, 9, 9))[0]

    assert avaliacao.taxa_cm_por_dia == pytest.approx(1.0)
