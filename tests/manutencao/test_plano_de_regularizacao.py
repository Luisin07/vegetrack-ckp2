"""Prioridade e prazo da ordem de serviço — regra do domínio de manutenção, sem infraestrutura."""

from datetime import date

from vegetrack.manutencao.dominio.ordem_de_servico import Prioridade
from vegetrack.manutencao.dominio.plano_de_regularizacao import PlanoDeRegularizacao
from vegetrack.manutencao.dominio.violacao_contratual import SituacaoDaViolacao, ViolacaoContratual

MEDICAO = date(2026, 9, 9)


def test_trecho_que_ja_violou_o_limite_e_urgente_com_prazo_contratual_de_48_horas():
    plano = PlanoDeRegularizacao.para(30.0, MEDICAO, 0, critico=True)

    assert plano.prioridade is Prioridade.URGENTE
    assert plano.prazo.data_limite == date(2026, 9, 11)
    assert "ARTESP" in plano.prazo.origem


def test_trecho_critico_por_projecao_e_alta_com_prazo_na_data_projetada():
    plano = PlanoDeRegularizacao.para(29.9, MEDICAO, 1, critico=True)

    assert plano.prioridade is Prioridade.ALTA
    assert plano.prazo.data_limite == date(2026, 9, 10)


def test_trecho_em_atencao_e_normal():
    plano = PlanoDeRegularizacao.para(22.0, MEDICAO, 5, critico=False)

    assert plano.prioridade is Prioridade.NORMAL
    assert plano.prazo.data_limite == date(2026, 9, 14)


def test_violacao_apontada_nasce_iminente_na_artesp_com_prazo_de_48_horas():
    violacao = ViolacaoContratual.apontar("RD-001", 34.0, MEDICAO)

    assert violacao.situacao is SituacaoDaViolacao.IMINENTE
    assert violacao.orgao_regulador == "ARTESP"
    assert violacao.prazo_de_regularizacao.data_limite == date(2026, 9, 11)
