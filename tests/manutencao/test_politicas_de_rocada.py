"""Padrão Strategy — cada política de roçada isolada e o seletor (Context) escolhendo."""

from datetime import date

import pytest

from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico, Prioridade
from vegetrack.manutencao.dominio.politicas_de_rocada import (
    SELETOR_PADRAO,
    PlanoDeRocada,
    PoliticaDeRocada,
    RocadaManual,
    RocadaMecanizada,
    RocadaMecanizadaPesada,
    SeletorDePoliticaDeRocada,
    SemPoliticaDeRocada,
)
from vegetrack.manutencao.dominio.prazo_legal import PrazoLegal


@pytest.mark.parametrize(
    ("politica", "aceitas", "recusadas"),
    [
        (RocadaManual(), [0.0, 30.0, 50.0], [50.1, 200.0]),
        (RocadaMecanizada(), [50.1, 100.0], [50.0, 100.1]),
        (RocadaMecanizadaPesada(), [100.1, 300.0], [100.0, 30.0]),
    ],
)
def test_cada_politica_atende_so_a_propria_faixa_de_altura(politica, aceitas, recusadas):
    assert all(politica.aplica_se_a(a) for a in aceitas)
    assert not any(politica.aplica_se_a(a) for a in recusadas)


def test_faixas_padrao_nao_se_sobrepoem_nem_deixam_buraco():
    politicas = [RocadaManual(), RocadaMecanizada(), RocadaMecanizadaPesada()]

    for altura in [x / 10 for x in range(0, 3001)]:
        assert sum(p.aplica_se_a(altura) for p in politicas) == 1, altura


def test_seletor_recusa_altura_sem_politica_que_atenda():
    seletor = SeletorDePoliticaDeRocada([RocadaManual()])

    with pytest.raises(SemPoliticaDeRocada):
        seletor.planejar(80.0)


def test_seletor_sem_nenhuma_politica_e_invalido():
    with pytest.raises(ValueError):
        SeletorDePoliticaDeRocada([])


def test_politica_nova_entra_sem_alterar_a_ordem_de_servico():
    # Arrange: método que a Motiva poderia adotar, criado só neste teste
    class RocadaEmTalude(PoliticaDeRocada):
        def aplica_se_a(self, altura_cm: float) -> bool:
            return True

        def planejar(self, altura_cm: float) -> PlanoDeRocada:
            return PlanoDeRocada("Roçada em talude com cinto de segurança", 2, ("cinto",))

    seletor = SeletorDePoliticaDeRocada([RocadaEmTalude()])
    prazo = PrazoLegal(date(2026, 9, 11), "Contrato ARTESP — 48 h")

    # Act
    ordem = OrdemDeServico.emitir("OS-0001", "RD-001", 40.0, Prioridade.URGENTE, prazo, seletor)

    # Assert
    assert ordem.metodo_de_rocada == "Roçada em talude com cinto de segurança"
    assert ordem.epi_obrigatorio == ("cinto",)


def test_seletor_padrao_e_o_usado_quando_nenhum_e_informado():
    plano = SELETOR_PADRAO.planejar(120.0)

    assert plano.equipes_necessarias == 3
    assert "máscara contra poeira" in plano.epi_obrigatorio
