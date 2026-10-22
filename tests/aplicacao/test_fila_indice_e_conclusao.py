"""US-06 (fila), US-07 (índice) e RF-08 (conclusão da ordem com regularização)."""

from datetime import date

import pytest

from vegetrack.aplicacao.erros import OrdemNaoEncontrada
from vegetrack.manutencao.dominio.ordem_de_servico import OperacaoNaoPermitida, SituacaoDaOrdem
from vegetrack.manutencao.dominio.violacao_contratual import SituacaoDaViolacao
from vegetrack.monitoramento.dominio.indice_de_saude import IndiceIndisponivel

HOJE = date(2026, 9, 9)


def _rodovia(sistema) -> None:
    sistema.cadastrar("CONFORME", ("2026-09-01", 10), ("2026-09-09", 12), marco_inicial="1+000",
                      marco_final="1+500", sentido="Norte")  # fmt: skip
    sistema.cadastrar("ATENCAO", ("2026-09-07", 19), ("2026-09-09", 22), marco_inicial="12+000",
                      marco_final="12+500", sentido="Sul")  # fmt: skip
    sistema.cadastrar("CRITICO", ("2026-09-09", 35), marco_inicial="15+000",
                      marco_final="15+500", sentido="Norte")  # fmt: skip
    sistema.cadastrar("PROJETADO", ("2026-09-08", 25), ("2026-09-09", 27), marco_inicial="25+000",
                      marco_final="25+500", sentido="Norte")  # fmt: skip


def test_fila_ordena_do_mais_critico_para_o_menos_critico(sistema):
    _rodovia(sistema)

    fila = sistema.fila.executar(HOJE)

    assert [a.trecho_id for a in fila] == ["CRITICO", "PROJETADO", "ATENCAO", "CONFORME"]


def test_fila_filtra_por_faixa_de_quilometragem_e_sentido(sistema):
    _rodovia(sistema)

    fila = sistema.fila.executar(HOJE, km_inicial=10, km_final=20, sentido="norte")

    assert [a.trecho_id for a in fila] == ["CRITICO"]


def test_fila_vazia_quando_nenhum_trecho_atende_ao_filtro(sistema):
    _rodovia(sistema)

    assert sistema.fila.executar(HOJE, km_inicial=100) == []


def test_indice_de_saude_da_rodovia_fica_entre_0_e_100(sistema):
    _rodovia(sistema)

    indice = sistema.indice.executar(HOJE)

    assert 0 <= indice.valor <= 100


def test_indice_sem_trechos_monitorados_nao_e_calculado(sistema):
    with pytest.raises(IndiceIndisponivel):
        sistema.indice.executar(HOJE)


def test_concluir_ordem_regulariza_violacao_e_melhora_o_indice(sistema):
    # Arrange
    _rodovia(sistema)
    indice_antes = sistema.indice.executar(HOJE).valor
    resultado = sistema.avaliar.executar("CRITICO", HOJE)

    # Act
    ordem = sistema.concluir.executar(resultado.ordem.numero, date(2026, 9, 10), 6.0, "Marcos")

    # Assert
    assert ordem.situacao is SituacaoDaOrdem.CONCLUIDA
    reavaliacao = sistema.avaliar.executar("CRITICO", date(2026, 9, 10))
    assert reavaliacao.ordem is None
    assert reavaliacao.violacao is None
    assert sistema.indice.executar(date(2026, 9, 10)).valor > indice_antes


def test_violacao_regularizada_nao_se_configura_mesmo_apos_o_prazo(sistema):
    sistema.cadastrar("RD-001", ("2026-09-09", 34))
    resultado = sistema.avaliar.executar("RD-001", HOJE)

    sistema.concluir.executar(resultado.ordem.numero, date(2026, 9, 10), 5.0, "Marcos")

    assert resultado.violacao.situacao is SituacaoDaViolacao.IMINENTE
    assert sistema.avaliar.executar("RD-001", date(2026, 9, 12)).violacao is None


def test_nao_conclui_ordem_se_a_vegetacao_continua_acima_do_limite(sistema):
    sistema.cadastrar("RD-001", ("2026-09-09", 34))
    numero = sistema.avaliar.executar("RD-001", HOJE).ordem.numero

    with pytest.raises(OperacaoNaoPermitida):
        sistema.concluir.executar(numero, date(2026, 9, 10), 31.0, "Marcos")

    assert sistema.avaliar.executar("RD-001", date(2026, 9, 10)).ordem.numero == numero


def test_nao_conclui_ordem_inexistente(sistema):
    with pytest.raises(OrdemNaoEncontrada):
        sistema.concluir.executar("OS-9999", HOJE, 5.0, "Marcos")
