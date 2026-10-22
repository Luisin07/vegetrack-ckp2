import pytest

from vegetrack.monitoramento.dominio.marco_quilometrico import MarcoInvalido, MarcoQuilometrico


def test_interpreta_marco_no_formato_usado_em_campo():
    marco = MarcoQuilometrico.de_texto("KM 29+300")

    assert marco == MarcoQuilometrico(km=29, metro=300)
    assert str(marco) == "KM 29+300"


def test_interpreta_marco_sem_o_prefixo_km():
    assert MarcoQuilometrico.de_texto("0+050").em_metros == 50


@pytest.mark.parametrize("texto", ["29,300", "KM 29", "abc", ""])
def test_recusa_marco_fora_do_formato_km_mais_metro(texto):
    with pytest.raises(MarcoInvalido):
        MarcoQuilometrico.de_texto(texto)


@pytest.mark.parametrize(("km", "metro"), [(-1, 0), (10, 1000), (10, -1)])
def test_recusa_marco_com_valores_fora_da_faixa(km, metro):
    with pytest.raises(MarcoInvalido):
        MarcoQuilometrico(km=km, metro=metro)


def test_marcos_sao_ordenados_pela_posicao_na_rodovia():
    assert MarcoQuilometrico(10, 500) < MarcoQuilometrico(11, 0)
