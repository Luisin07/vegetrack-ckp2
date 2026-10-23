import pytest

from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaInvalida, AlturaVegetacao


@pytest.mark.parametrize("centimetros", [0.0, 0.1, 29.9, 30.0, 299.9, 300.0])
def test_aceita_altura_dentro_da_faixa_de_0_a_300_cm(centimetros):
    # Arrange / Act
    altura = AlturaVegetacao(centimetros)

    # Assert
    assert altura.centimetros == centimetros


@pytest.mark.parametrize("centimetros", [-5.0, -0.1, 300.1, 1000.0])
def test_nao_permite_altura_negativa_ou_acima_de_300_cm(centimetros):
    with pytest.raises(AlturaInvalida):
        AlturaVegetacao(centimetros)


def test_nao_permite_altura_nao_numerica():
    with pytest.raises(AlturaInvalida):
        AlturaVegetacao(float("nan"))


def test_alturas_com_mesmo_valor_sao_iguais_por_serem_value_object():
    assert AlturaVegetacao(24.0) == AlturaVegetacao(24.0)
