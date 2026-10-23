"""Padrão Observer — publicador avisa os observadores; um novo entra sem mudar o caso de uso."""

from datetime import date

from vegetrack.adaptadores.repositorios_em_memoria import (
    RepositorioDeOrdensEmMemoria,
    RepositorioDeTrechosEmMemoria,
    RepositorioDeViolacoesEmMemoria,
)
from vegetrack.aplicacao.avaliar_trecho import AvaliarTrecho
from vegetrack.aplicacao.publicador_de_avaliacoes import (
    ObservadorDeAvaliacao,
    PublicadorDeAvaliacoes,
)
from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.marco_quilometrico import MarcoQuilometrico
from vegetrack.monitoramento.dominio.medicao import Medicao
from vegetrack.monitoramento.dominio.trecho import Trecho


class ObservadorEspiao(ObservadorDeAvaliacao):
    def __init__(self) -> None:
        self.eventos = []

    def ao_avaliar(self, evento) -> None:
        self.eventos.append(evento)


def _avaliar_com(observador, altura_cm: float):
    trechos = RepositorioDeTrechosEmMemoria()
    trecho = Trecho("RD-001", MarcoQuilometrico(1, 0), MarcoQuilometrico(1, 500), "Norte")
    trecho.registrar_medicao(Medicao(date(2026, 9, 9), AlturaVegetacao(altura_cm), "Ana"))
    trechos.salvar(trecho)
    caso_de_uso = AvaliarTrecho(
        trechos, RepositorioDeOrdensEmMemoria(), RepositorioDeViolacoesEmMemoria()
    )
    caso_de_uso.publicador.inscrever(observador)
    return caso_de_uso.executar("RD-001", date(2026, 9, 9))


def test_novo_observador_recebe_o_evento_sem_alterar_o_caso_de_uso():
    espiao = ObservadorEspiao()

    resultado = _avaliar_com(espiao, 34.0)

    assert len(espiao.eventos) == 1
    assert espiao.eventos[0].trecho_id == "RD-001"
    assert espiao.eventos[0].violou_limite
    assert resultado.ordem is not None


def test_evento_e_publicado_mesmo_para_trecho_conforme():
    espiao = ObservadorEspiao()

    resultado = _avaliar_com(espiao, 5.0)

    assert not espiao.eventos[0].exige_ordem_de_servico
    assert resultado.ordem is None and resultado.violacao is None


def test_publicador_avisa_todos_os_observadores_na_ordem_de_inscricao():
    chamadas = []

    class Registrador(ObservadorDeAvaliacao):
        def __init__(self, nome):
            self.nome = nome

        def ao_avaliar(self, evento):
            chamadas.append(self.nome)

    publicador = PublicadorDeAvaliacoes([Registrador("primeiro")])
    publicador.inscrever(Registrador("segundo"))

    publicador.publicar(evento=object())

    assert chamadas == ["primeiro", "segundo"]
