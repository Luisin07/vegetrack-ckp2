"""
avaliar_trecho.py
Caso de uso principal (US-02 a US-05): avalia o risco do trecho, emite a ordem de serviço
e registra a violação contratual iminente.
"""

import math
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from vegetrack.adaptadores.armazenamento_em_arquivo import ArmazenamentoEmArquivo
from vegetrack.aplicacao.erros import TrechoNaoEncontrado, TrechoSemMedicao
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico, Prioridade
from vegetrack.manutencao.dominio.prazo_legal import PrazoLegal
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual
from vegetrack.monitoramento.dominio.avaliacao_de_risco import AvaliacaoDeRisco, NivelDeRisco


@dataclass(frozen=True)
class ResultadoDaAvaliacao:
    avaliacao: AvaliacaoDeRisco
    ordem: OrdemDeServico | None
    violacao: ViolacaoContratual | None


class AvaliarTrecho:
    def __init__(self, caminho_dos_dados: Path) -> None:
        self._caminho_dos_dados = caminho_dos_dados

    def executar(self, trecho_id: str, hoje: date) -> ResultadoDaAvaliacao:  # noqa: C901
        dados = ArmazenamentoEmArquivo(self._caminho_dos_dados)
        trecho = dados.buscar_trecho(trecho_id)
        if trecho is None:
            raise TrechoNaoEncontrado(trecho_id)
        medicoes = trecho.medicoes
        if not medicoes:
            raise TrechoSemMedicao(trecho_id)
        ultima = medicoes[-1]
        altura = ultima.altura.centimetros

        taxa = None
        if len(medicoes) >= 2:
            anterior = medicoes[-2]
            dias = (ultima.data - anterior.data).days
            taxa = (altura - anterior.altura.centimetros) / dias

        dias_ate_limite = None
        if altura >= 30:
            dias_ate_limite = 0
        elif taxa is not None and taxa > 0:
            dias_ate_limite = math.floor((30 - altura) / taxa)

        if altura >= 30 or (dias_ate_limite is not None and dias_ate_limite <= 2):
            nivel = NivelDeRisco.CRITICO
        elif dias_ate_limite is not None and dias_ate_limite <= 7:
            nivel = NivelDeRisco.ATENCAO
        else:
            nivel = NivelDeRisco.CONFORME

        avaliacao = AvaliacaoDeRisco(
            trecho_id, hoje, ultima.data, ultima.altura, taxa, dias_ate_limite, nivel
        )

        ordem = None
        if nivel != NivelDeRisco.CONFORME:
            if altura >= 30:
                prioridade = Prioridade.URGENTE
                prazo = PrazoLegal(ultima.data + timedelta(days=2), "Contrato ARTESP — 48 h")
            else:
                prioridade = Prioridade.ALTA if nivel == NivelDeRisco.CRITICO else Prioridade.NORMAL
                prazo = PrazoLegal(
                    ultima.data + timedelta(days=dias_ate_limite), "Projeção de crescimento"
                )
            ordem = dados.ordem_aberta_do_trecho(trecho_id)
            if ordem is None:
                ordem = OrdemDeServico.emitir(
                    dados.proximo_numero_de_ordem(), trecho_id, altura, prioridade, prazo
                )
            else:
                ordem.reavaliar(prioridade, prazo)
            dados.salvar_ordem(ordem)

        violacao = None
        if altura >= 30:
            violacao = dados.violacao_ativa_do_trecho(trecho_id)
            if violacao is None:
                violacao = ViolacaoContratual(
                    trecho_id,
                    "ARTESP",
                    altura,
                    PrazoLegal(ultima.data + timedelta(days=2), "Contrato ARTESP — 48 h"),
                )
            violacao.apurar(hoje)
            dados.salvar_violacao(violacao)

        dados.persistir()
        return ResultadoDaAvaliacao(avaliacao, ordem, violacao)
