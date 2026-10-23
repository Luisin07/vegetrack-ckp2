from datetime import date

import pytest

from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.avaliacao_de_risco import AvaliacaoDeRisco, NivelDeRisco
from vegetrack.monitoramento.dominio.indice_de_saude import IndiceDeSaude, IndiceIndisponivel

HOJE = date(2026, 9, 9)


def _avaliacao(altura_cm: float, nivel: NivelDeRisco, taxa: float | None = 0.2):
    return AvaliacaoDeRisco("T", HOJE, HOJE, AlturaVegetacao(altura_cm), taxa, None, nivel)


def test_rodovia_toda_conforme_e_sem_crescimento_acelerado_vale_100():
    avaliacoes = [_avaliacao(10.0, NivelDeRisco.CONFORME) for _ in range(5)]

    assert IndiceDeSaude.calcular(avaliacoes).valor == 100


def test_rodovia_toda_critica_e_em_crescimento_acelerado_vale_0():
    avaliacoes = [_avaliacao(40.0, NivelDeRisco.CRITICO, taxa=2.0) for _ in range(3)]

    assert IndiceDeSaude.calcular(avaliacoes).valor == 0


def test_regularizar_um_trecho_critico_aumenta_o_indice():
    antes = [_avaliacao(40.0, NivelDeRisco.CRITICO, 1.5), _avaliacao(10.0, NivelDeRisco.CONFORME)]
    depois = [_avaliacao(5.0, NivelDeRisco.CONFORME), _avaliacao(10.0, NivelDeRisco.CONFORME)]

    assert IndiceDeSaude.calcular(depois).valor > IndiceDeSaude.calcular(antes).valor


def test_trecho_sem_taxa_conta_como_crescimento_controlado():
    avaliacoes = [_avaliacao(10.0, NivelDeRisco.CONFORME, taxa=None)]

    assert IndiceDeSaude.calcular(avaliacoes).valor == 100


def test_nao_calcula_indice_sem_nenhum_trecho_avaliado():
    with pytest.raises(IndiceIndisponivel):
        IndiceDeSaude.calcular([])


@pytest.mark.parametrize("valor", [-1, 101])
def test_indice_fora_de_0_a_100_e_recusado(valor):
    with pytest.raises(ValueError):
        IndiceDeSaude(valor)
