"""Adaptadores de entrada: leitura do CSV e CLI de ponta a ponta (usam arquivo temporário)."""

import pytest

from vegetrack.adaptadores.cli import main
from vegetrack.adaptadores.importador_csv import LevantamentoMalFormado, ler_levantamento_csv

CABECALHO = "trecho;marco_inicial;marco_final;sentido;data;altura_cm;responsavel\n"


def test_le_as_linhas_do_levantamento_numeradas_como_no_arquivo(tmp_path):
    arquivo = tmp_path / "levantamento.csv"
    arquivo.write_text(CABECALHO + "RD-001;1+000;1+500;Norte;2026-09-01; 12 ;Ana\n", "utf-8")

    linhas = ler_levantamento_csv(arquivo)

    assert len(linhas) == 1
    assert linhas[0].numero == 2
    assert linhas[0].altura_cm == "12"


def test_recusa_levantamento_sem_as_colunas_obrigatorias(tmp_path):
    arquivo = tmp_path / "levantamento.csv"
    arquivo.write_text("trecho;altura_cm\nRD-001;12\n", "utf-8")

    with pytest.raises(LevantamentoMalFormado):
        ler_levantamento_csv(arquivo)


def test_demo_executa_o_fluxo_principal_de_ponta_a_ponta(capsys):
    codigo = main(["demo"])

    saida = capsys.readouterr().out
    assert codigo == 0
    assert "32 medições importadas, 1 rejeitadas" in saida
    assert "URGENTE" in saida and "VIOLAÇÃO IMINENTE" in saida
    assert "!! RD-004 acima de 30 cm" in saida
    assert "Índice de saúde da rodovia" in saida


def test_cli_registra_avalia_e_conclui_usando_a_base_em_arquivo(tmp_path, capsys):
    dados = ["--dados", str(tmp_path / "base")]
    arquivo = tmp_path / "levantamento.csv"
    arquivo.write_text(CABECALHO + "RD-001;1+000;1+500;Norte;2026-09-09;34;Ana\n", "utf-8")

    assert main([*dados, "importar", str(arquivo)]) == 0
    assert main([*dados, "avaliar", "--hoje", "2026-09-09"]) == 0
    assert main([*dados, "concluir", "OS-0001", "6", "--data", "2026-09-10"]) == 0
    assert main([*dados, "registrar", "RD-001", "8", "--data", "2026-09-15"]) == 0
    assert main([*dados, "fila", "--hoje", "2026-09-15", "--sentido", "Norte"]) == 0
    assert main([*dados, "indice", "--hoje", "2026-09-15"]) == 0

    saida = capsys.readouterr().out
    assert "OS-0001 concluída" in saida
    assert "100/100" in saida


def test_cli_mostra_erro_de_negocio_sem_stack_trace(tmp_path, capsys):
    codigo = main(["--dados", str(tmp_path / "base"), "registrar", "RD-404", "10"])

    assert codigo == 1
    assert "Erro: Trecho 'RD-404' não existe" in capsys.readouterr().out
