"""
registrar_medicao.py
Caso de uso US-01 (RF-01): o técnico registra a altura medida num trecho existente.
"""

from datetime import date
from pathlib import Path

from vegetrack.adaptadores.armazenamento_em_arquivo import ArmazenamentoEmArquivo
from vegetrack.aplicacao.erros import TrechoNaoEncontrado
from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.medicao import Medicao


class RegistrarMedicao:
    def __init__(self, caminho_dos_dados: Path) -> None:
        self._caminho_dos_dados = caminho_dos_dados

    def executar(self, trecho_id: str, data: date, altura_cm: float, responsavel: str) -> Medicao:
        # ===== BLOCO 1: localizar_trecho =====
        dados = ArmazenamentoEmArquivo(self._caminho_dos_dados)
        trecho = dados.buscar_trecho(trecho_id)
        if trecho is None:
            raise TrechoNaoEncontrado(trecho_id)

        # ===== BLOCO 2: registrar_e_persistir =====
        medicao = Medicao(data, AlturaVegetacao(altura_cm), responsavel)
        trecho.registrar_medicao(medicao)
        dados.salvar_trecho(trecho)
        dados.persistir()
        return medicao
