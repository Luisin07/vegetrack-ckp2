"""
ordem_de_servico.py
Raiz do agregado de manutenção: a autorização de roçada de um trecho, do emissão à conclusão.
Regras: RN-04 (só conclui com medição abaixo do limite) e RN-06 (uma ordem aberta por trecho).
"""

from dataclasses import dataclass, field
from enum import Enum, IntEnum

from vegetrack.manutencao.dominio.prazo_legal import PrazoLegal

LIMITE_CONTRATUAL_CM = 30.0


class Prioridade(IntEnum):
    NORMAL = 1
    ALTA = 2
    URGENTE = 3


class SituacaoDaOrdem(Enum):
    ABERTA = "Aberta"
    EM_EXECUCAO = "Em execução"
    CONCLUIDA = "Concluída"


class OperacaoNaoPermitida(ValueError):
    """Transição de estado proibida pelas regras da ordem de serviço."""


@dataclass
class OrdemDeServico:
    numero: str
    trecho_id: str
    altura_que_originou_cm: float
    prioridade: Prioridade
    prazo: PrazoLegal
    metodo_de_rocada: str
    equipes_necessarias: int
    epi_obrigatorio: tuple[str, ...]
    situacao: SituacaoDaOrdem = SituacaoDaOrdem.ABERTA
    altura_comprovada_cm: float | None = field(default=None)

    @classmethod
    def emitir(
        cls,
        numero: str,
        trecho_id: str,
        altura_cm: float,
        prioridade: Prioridade,
        prazo: PrazoLegal,
    ) -> "OrdemDeServico":
        epi_basico = ("capacete", "protetor auricular", "óculos de proteção", "perneira", "luvas")
        if altura_cm <= 50:
            metodo = "Roçada manual com roçadeira costal"
            equipes = 1
            epi = epi_basico
        elif altura_cm <= 100:
            metodo = "Roçada mecanizada com trator e roçadeira acoplada"
            equipes = 2
            epi = epi_basico + ("colete refletivo",)
        else:
            metodo = "Roçada mecanizada pesada com trator e apoio manual"
            equipes = 3
            epi = epi_basico + ("colete refletivo", "máscara contra poeira")
        return cls(numero, trecho_id, altura_cm, prioridade, prazo, metodo, equipes, epi)

    @property
    def em_aberto(self) -> bool:
        return self.situacao is not SituacaoDaOrdem.CONCLUIDA

    def reavaliar(self, prioridade: Prioridade, prazo: PrazoLegal) -> None:
        # RN-06: nova avaliação do trecho atualiza a ordem existente em vez de duplicá-la
        if not self.em_aberto:
            raise OperacaoNaoPermitida(
                f"{self.numero} já está concluída e não pode ser reavaliada."
            )
        self.prioridade = prioridade
        self.prazo = prazo

    def iniciar_execucao(self) -> None:
        if self.situacao is not SituacaoDaOrdem.ABERTA:
            raise OperacaoNaoPermitida(f"{self.numero} não está aberta.")
        self.situacao = SituacaoDaOrdem.EM_EXECUCAO

    def concluir(self, altura_comprovada_cm: float) -> None:
        # ===== BLOCO 1: guarda_de_estado =====
        if not self.em_aberto:
            raise OperacaoNaoPermitida(f"{self.numero} já foi concluída.")

        # ===== BLOCO 2: comprovacao_rn04 =====
        # RN-04: só sai de crítico com medição pós-roçada abaixo do limite, nunca por edição
        if altura_comprovada_cm >= LIMITE_CONTRATUAL_CM:
            raise OperacaoNaoPermitida(
                f"Medição de comprovação de {altura_comprovada_cm:g} cm ainda está acima "
                f"do limite de {LIMITE_CONTRATUAL_CM:g} cm; a ordem continua aberta."
            )
        self.altura_comprovada_cm = altura_comprovada_cm
        self.situacao = SituacaoDaOrdem.CONCLUIDA
