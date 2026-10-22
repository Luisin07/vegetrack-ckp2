"""
trecho.py
Raiz do agregado de monitoramento: o segmento da rodovia e o seu histórico de medições.
Medicao só entra no sistema através de Trecho.registrar_medicao (RN-03).
"""

from vegetrack.monitoramento.dominio.marco_quilometrico import MarcoQuilometrico
from vegetrack.monitoramento.dominio.medicao import Medicao


class TrechoInvalido(ValueError):
    """Trecho com delimitação incoerente."""


class Trecho:
    def __init__(
        self,
        identificacao: str,
        marco_inicial: MarcoQuilometrico,
        marco_final: MarcoQuilometrico,
        sentido: str,
    ) -> None:
        # ===== BLOCO 1: validacao_da_delimitacao =====
        if not identificacao.strip():
            raise TrechoInvalido("O trecho precisa de identificação.")
        if marco_final <= marco_inicial:
            raise TrechoInvalido(
                f"Marco final ({marco_final}) deve ser posterior ao inicial ({marco_inicial})."
            )

        # ===== BLOCO 2: estado_do_agregado =====
        self.identificacao = identificacao
        self.marco_inicial = marco_inicial
        self.marco_final = marco_final
        self.sentido = sentido
        self._medicoes_por_data: dict = {}

    def registrar_medicao(self, medicao: Medicao) -> None:
        # RN-03: duas medições na mesma data -> prevalece a mais recente
        self._medicoes_por_data[medicao.data] = medicao

    @property
    def medicoes(self) -> list[Medicao]:
        return [self._medicoes_por_data[data] for data in sorted(self._medicoes_por_data)]

    @property
    def ultima_medicao(self) -> Medicao | None:
        medicoes = self.medicoes
        return medicoes[-1] if medicoes else None

    def taxa_de_crescimento(self) -> float | None:
        # RN-03: taxa só existe com duas medições em datas distintas; usa as duas mais recentes
        medicoes = self.medicoes
        if len(medicoes) < 2:
            return None
        anterior, ultima = medicoes[-2], medicoes[-1]
        variacao_cm = ultima.altura.centimetros - anterior.altura.centimetros
        return variacao_cm / (ultima.data - anterior.data).days

    def contem_km(self, km_inicial: float | None, km_final: float | None) -> bool:
        inicio_em_km = self.marco_inicial.em_metros / 1000
        if km_inicial is not None and inicio_em_km < km_inicial:
            return False
        return km_final is None or inicio_em_km <= km_final

    def __eq__(self, outro: object) -> bool:
        return isinstance(outro, Trecho) and outro.identificacao == self.identificacao

    def __hash__(self) -> int:
        return hash(self.identificacao)

    def __repr__(self) -> str:
        return f"Trecho({self.identificacao}, {self.marco_inicial} a {self.marco_final})"
