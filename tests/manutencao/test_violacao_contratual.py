from datetime import date

from vegetrack.manutencao.dominio.prazo_legal import PrazoLegal
from vegetrack.manutencao.dominio.violacao_contratual import SituacaoDaViolacao, ViolacaoContratual

PRAZO = PrazoLegal(date(2026, 9, 11), "Contrato ARTESP — 48 h")


def _violacao() -> ViolacaoContratual:
    return ViolacaoContratual("RD-001", "ARTESP", 34.0, PRAZO)


def test_violacao_continua_iminente_ate_o_ultimo_dia_do_prazo():
    violacao = _violacao()

    violacao.apurar(hoje=date(2026, 9, 11))

    assert violacao.situacao is SituacaoDaViolacao.IMINENTE


def test_violacao_passa_a_configurada_no_dia_seguinte_ao_prazo():
    violacao = _violacao()

    violacao.apurar(hoje=date(2026, 9, 12))

    assert violacao.situacao is SituacaoDaViolacao.CONFIGURADA


def test_violacao_regularizada_nao_volta_a_ser_configurada():
    violacao = _violacao()
    violacao.regularizar()

    violacao.apurar(hoje=date(2026, 12, 1))

    assert violacao.situacao is SituacaoDaViolacao.REGULARIZADA
    assert not violacao.ativa


def test_prazo_legal_informa_dias_restantes_e_vencimento():
    assert PRAZO.dias_restantes(date(2026, 9, 9)) == 2
    assert not PRAZO.vencido_em(date(2026, 9, 11))
    assert PRAZO.vencido_em(date(2026, 9, 12))
