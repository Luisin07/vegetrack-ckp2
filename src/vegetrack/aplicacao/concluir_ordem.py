"""
concluir_ordem.py
Caso de uso RF-08: conclui a roçada com a medição de comprovação e regulariza a violação (RN-04).
"""

from datetime import date
from pathlib import Path

from vegetrack.adaptadores.armazenamento_em_arquivo import ArmazenamentoEmArquivo
from vegetrack.aplicacao.erros import OrdemNaoEncontrada
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico
from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.medicao import Medicao


class ConcluirOrdemDeServico:
    def __init__(self, caminho_dos_dados: Path) -> None:
        self._caminho_dos_dados = caminho_dos_dados

    def executar(
        self, numero: str, data: date, altura_comprovada_cm: float, responsavel: str
    ) -> OrdemDeServico:
        # ===== BLOCO 1: localizar_ordem =====
        dados = ArmazenamentoEmArquivo(self._caminho_dos_dados)
        ordem = dados.ordens.get(numero)
        if ordem is None:
            raise OrdemNaoEncontrada(numero)

        # ===== BLOCO 2: concluir_e_regularizar =====
        # concluir primeiro: se a altura ainda viola o limite, nada mais é alterado
        ordem.concluir(altura_comprovada_cm)
        trecho = dados.buscar_trecho(ordem.trecho_id)
        trecho.registrar_medicao(Medicao(data, AlturaVegetacao(altura_comprovada_cm), responsavel))
        violacao = dados.violacao_ativa_do_trecho(ordem.trecho_id)
        if violacao is not None:
            violacao.regularizar()

        # ===== BLOCO 3: persistir =====
        dados.salvar_trecho(trecho)
        dados.salvar_ordem(ordem)
        dados.persistir()
        return ordem
