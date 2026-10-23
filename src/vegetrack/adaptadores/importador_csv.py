"""
importador_csv.py
Adaptador de entrada: lê o levantamento em CSV (exportado da planilha da Motiva) em linhas.
As regras de validação ficam no caso de uso ImportarLevantamento.
"""

import csv
from pathlib import Path

from vegetrack.aplicacao.importar_levantamento import LinhaDeLevantamento

COLUNAS = ("trecho", "marco_inicial", "marco_final", "sentido", "data", "altura_cm", "responsavel")


class LevantamentoMalFormado(ValueError):
    """Arquivo sem as colunas esperadas do levantamento."""


def ler_levantamento_csv(caminho: Path) -> list[LinhaDeLevantamento]:
    with Path(caminho).open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        # ===== BLOCO 1: validar_cabecalho =====
        faltantes = set(COLUNAS) - set(leitor.fieldnames or [])
        if faltantes:
            raise LevantamentoMalFormado(f"Colunas ausentes no levantamento: {sorted(faltantes)}")

        # ===== BLOCO 2: converter_linhas =====
        # numeração começa em 2 porque a linha 1 do arquivo é o cabeçalho
        return [
            LinhaDeLevantamento(numero, *(linha[c].strip() for c in COLUNAS))
            for numero, linha in enumerate(leitor, start=2)
        ]
