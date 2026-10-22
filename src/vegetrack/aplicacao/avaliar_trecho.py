"""
avaliar_trecho.py
Caso de uso principal (US-02 a US-05): avalia o risco do trecho, emite a ordem de serviço
e registra a violação contratual iminente.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from vegetrack.adaptadores.armazenamento_em_arquivo import ArmazenamentoEmArquivo
from vegetrack.aplicacao.erros import TrechoNaoEncontrado
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico, Prioridade
from vegetrack.manutencao.dominio.prazo_legal import (
    ORGAO_REGULADOR,
    ORIGEM_CONTRATUAL,
    ORIGEM_PROJECAO,
    PRAZO_CONTRATUAL_DE_REGULARIZACAO,
    PrazoLegal,
)
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual
from vegetrack.monitoramento.dominio.avaliacao_de_risco import (
    LIMITE_CONTRATUAL_CM,
    AvaliacaoDeRisco,
    NivelDeRisco,
)


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
        avaliacao = trecho.avaliar(hoje)
        ultima = trecho.ultima_medicao
        altura = ultima.altura.centimetros
        nivel = avaliacao.nivel
        dias_ate_limite = avaliacao.dias_ate_o_limite

        ordem = None
        if nivel != NivelDeRisco.CONFORME:
            if altura >= LIMITE_CONTRATUAL_CM:
                prioridade = Prioridade.URGENTE
                prazo = PrazoLegal(
                    ultima.data + PRAZO_CONTRATUAL_DE_REGULARIZACAO, ORIGEM_CONTRATUAL
                )
            else:
                prioridade = Prioridade.ALTA if nivel == NivelDeRisco.CRITICO else Prioridade.NORMAL
                prazo = PrazoLegal(ultima.data + timedelta(days=dias_ate_limite), ORIGEM_PROJECAO)
            ordem = dados.ordem_aberta_do_trecho(trecho_id)
            if ordem is None:
                ordem = OrdemDeServico.emitir(
                    dados.proximo_numero_de_ordem(), trecho_id, altura, prioridade, prazo
                )
            else:
                ordem.reavaliar(prioridade, prazo)
            dados.salvar_ordem(ordem)

        violacao = None
        if altura >= LIMITE_CONTRATUAL_CM:
            violacao = dados.violacao_ativa_do_trecho(trecho_id)
            if violacao is None:
                violacao = ViolacaoContratual(
                    trecho_id,
                    ORGAO_REGULADOR,
                    altura,
                    PrazoLegal(ultima.data + PRAZO_CONTRATUAL_DE_REGULARIZACAO, ORIGEM_CONTRATUAL),
                )
            violacao.apurar(hoje)
            dados.salvar_violacao(violacao)

        dados.persistir()
        return ResultadoDaAvaliacao(avaliacao, ordem, violacao)
