"""
Caso de uso principal (US-02 a US-05) — testes de caracterização.
Congelam o comportamento antes das refatorações: precisam passar sem alteração antes e depois.
"""

from datetime import date

import pytest

from vegetrack.aplicacao.erros import TrechoNaoEncontrado
from vegetrack.manutencao.dominio.ordem_de_servico import Prioridade
from vegetrack.manutencao.dominio.violacao_contratual import SituacaoDaViolacao
from vegetrack.monitoramento.dominio.avaliacao_de_risco import NivelDeRisco

HOJE = date(2026, 9, 9)


# ===== US-02: taxa de crescimento =====
def test_taxa_de_crescimento_entre_duas_medicoes_consecutivas(sistema):
    sistema.cadastrar("RD-001", ("2026-09-01", 18), ("2026-09-09", 26))

    resultado = sistema.avaliar.executar("RD-001", HOJE)

    assert resultado.avaliacao.taxa_cm_por_dia == pytest.approx(1.0)


def test_taxa_usa_apenas_as_duas_medicoes_mais_recentes(sistema):
    sistema.cadastrar("RD-001", ("2026-08-01", 2), ("2026-09-01", 18), ("2026-09-09", 22))

    resultado = sistema.avaliar.executar("RD-001", HOJE)

    assert resultado.avaliacao.taxa_cm_por_dia == pytest.approx(0.5)


def test_com_uma_unica_medicao_a_taxa_fica_indisponivel_e_vale_a_altura(sistema):
    sistema.cadastrar("RD-001", ("2026-09-09", 12))

    resultado = sistema.avaliar.executar("RD-001", HOJE)

    assert resultado.avaliacao.taxa_cm_por_dia is None
    assert resultado.avaliacao.nivel is NivelDeRisco.CONFORME
    assert resultado.ordem is None


# ===== US-03: classificação diante do limite de 30 cm =====
@pytest.mark.parametrize(
    ("medicoes", "nivel", "dias"),
    [
        ([("2026-09-09", 31)], NivelDeRisco.CRITICO, 0),
        ([("2026-09-09", 30)], NivelDeRisco.CRITICO, 0),
        ([("2026-09-09", 29.9)], NivelDeRisco.CONFORME, None),
        ([("2026-09-07", 19), ("2026-09-09", 22)], NivelDeRisco.ATENCAO, 5),
        ([("2026-09-08", 25), ("2026-09-09", 27)], NivelDeRisco.CRITICO, 1),
        ([("2026-09-08", 24), ("2026-09-09", 26)], NivelDeRisco.CRITICO, 2),
        ([("2026-09-08", 22), ("2026-09-09", 24)], NivelDeRisco.ATENCAO, 3),
        ([("2026-09-08", 22), ("2026-09-09", 23)], NivelDeRisco.ATENCAO, 7),
        ([("2026-09-08", 21), ("2026-09-09", 22)], NivelDeRisco.CONFORME, 8),
        ([("2026-09-01", 10), ("2026-09-09", 18)], NivelDeRisco.CONFORME, 12),
        ([("2026-09-01", 20), ("2026-09-09", 12)], NivelDeRisco.CONFORME, None),
        ([("2026-09-01", 20), ("2026-09-09", 20)], NivelDeRisco.CONFORME, None),
    ],
)
def test_classifica_o_trecho_pelo_limite_e_pela_projecao(sistema, medicoes, nivel, dias):
    sistema.cadastrar("RD-001", *medicoes)

    avaliacao = sistema.avaliar.executar("RD-001", HOJE).avaliacao

    assert avaliacao.nivel is nivel
    assert avaliacao.dias_ate_o_limite == dias


# ===== US-04: ordem de serviço automática =====
def test_trecho_acima_do_limite_gera_ordem_urgente_com_prazo_de_48_horas(sistema):
    sistema.cadastrar("RD-001", ("2026-09-09", 34))

    ordem = sistema.avaliar.executar("RD-001", HOJE).ordem

    assert ordem.numero == "OS-0001"
    assert ordem.prioridade is Prioridade.URGENTE
    assert ordem.prazo.data_limite == date(2026, 9, 11)
    assert ordem.metodo_de_rocada and ordem.equipes_necessarias >= 1 and ordem.epi_obrigatorio


def test_trecho_que_estoura_o_limite_em_ate_2_dias_gera_ordem_alta(sistema):
    sistema.cadastrar("RD-001", ("2026-09-08", 25), ("2026-09-09", 27))

    ordem = sistema.avaliar.executar("RD-001", HOJE).ordem

    assert ordem.prioridade is Prioridade.ALTA
    assert ordem.prazo.data_limite == date(2026, 9, 10)


def test_trecho_em_atencao_gera_ordem_normal(sistema):
    sistema.cadastrar("RD-001", ("2026-09-07", 19), ("2026-09-09", 22))

    ordem = sistema.avaliar.executar("RD-001", HOJE).ordem

    assert ordem.prioridade is Prioridade.NORMAL
    assert ordem.prazo.data_limite == date(2026, 9, 14)


def test_trecho_conforme_nao_gera_ordem_nem_violacao(sistema):
    sistema.cadastrar("RD-001", ("2026-09-01", 10), ("2026-09-09", 12))

    resultado = sistema.avaliar.executar("RD-001", HOJE)

    assert resultado.ordem is None
    assert resultado.violacao is None


def test_reavaliar_trecho_com_ordem_aberta_nao_duplica_a_ordem(sistema):
    sistema.cadastrar("RD-001", ("2026-09-07", 19), ("2026-09-09", 22))
    primeira = sistema.avaliar.executar("RD-001", HOJE).ordem
    sistema.registrar.executar("RD-001", date(2026, 9, 10), 31.0, "Marcos")

    segunda = sistema.avaliar.executar("RD-001", date(2026, 9, 10)).ordem

    assert segunda.numero == primeira.numero
    assert segunda.prioridade is Prioridade.URGENTE


def test_cada_trecho_recebe_numero_de_ordem_proprio(sistema):
    sistema.cadastrar("RD-001", ("2026-09-09", 35))
    sistema.cadastrar("RD-002", ("2026-09-09", 40), marco_inicial="11+000", marco_final="11+500")

    numeros = {sistema.avaliar.executar(t, HOJE).ordem.numero for t in ("RD-001", "RD-002")}

    assert numeros == {"OS-0001", "OS-0002"}


# ===== US-05: violação contratual =====
def test_trecho_acima_do_limite_registra_violacao_iminente_na_artesp(sistema):
    sistema.cadastrar("RD-001", ("2026-09-09", 34))

    violacao = sistema.avaliar.executar("RD-001", HOJE).violacao

    assert violacao.situacao is SituacaoDaViolacao.IMINENTE
    assert violacao.orgao_regulador == "ARTESP"
    assert violacao.prazo_de_regularizacao.data_limite == date(2026, 9, 11)


def test_violacao_passa_a_configurada_quando_o_prazo_vence_sem_rocada(sistema):
    sistema.cadastrar("RD-001", ("2026-09-09", 34))
    sistema.avaliar.executar("RD-001", HOJE)

    violacao = sistema.avaliar.executar("RD-001", date(2026, 9, 12)).violacao

    assert violacao.situacao is SituacaoDaViolacao.CONFIGURADA


def test_trecho_projetado_mas_ainda_abaixo_do_limite_nao_tem_violacao(sistema):
    sistema.cadastrar("RD-001", ("2026-09-08", 25), ("2026-09-09", 27))

    assert sistema.avaliar.executar("RD-001", HOJE).violacao is None


# ===== Exceções do fluxo =====
def test_avaliar_trecho_inexistente_falha_com_erro_de_negocio(sistema):
    with pytest.raises(TrechoNaoEncontrado):
        sistema.avaliar.executar("RD-999", HOJE)
