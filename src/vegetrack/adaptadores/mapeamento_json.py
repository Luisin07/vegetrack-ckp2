"""
mapeamento_json.py
Tradução entre os objetos de domínio e dicionários JSON -- usada pelos repositórios em arquivo.
"""

from dataclasses import asdict
from datetime import date

from vegetrack.manutencao.dominio.ordem_de_servico import (
    OrdemDeServico,
    Prioridade,
    SituacaoDaOrdem,
)
from vegetrack.manutencao.dominio.prazo_legal import PrazoLegal
from vegetrack.manutencao.dominio.violacao_contratual import (
    SituacaoDaViolacao,
    ViolacaoContratual,
)
from vegetrack.monitoramento.dominio.altura_vegetacao import AlturaVegetacao
from vegetrack.monitoramento.dominio.marco_quilometrico import MarcoQuilometrico
from vegetrack.monitoramento.dominio.medicao import Medicao
from vegetrack.monitoramento.dominio.trecho import Trecho


def trecho_para_dict(trecho: Trecho) -> dict:
    return {
        "identificacao": trecho.identificacao,
        "marco_inicial": [trecho.marco_inicial.km, trecho.marco_inicial.metro],
        "marco_final": [trecho.marco_final.km, trecho.marco_final.metro],
        "sentido": trecho.sentido,
        "medicoes": [
            {
                "data": m.data.isoformat(),
                "altura_cm": m.altura.centimetros,
                "responsavel": m.responsavel,
            }
            for m in trecho.medicoes
        ],
    }


def trecho_de_dict(dados: dict) -> Trecho:
    trecho = Trecho(
        dados["identificacao"],
        MarcoQuilometrico(*dados["marco_inicial"]),
        MarcoQuilometrico(*dados["marco_final"]),
        dados["sentido"],
    )
    for m in dados["medicoes"]:
        trecho.registrar_medicao(
            Medicao(
                date.fromisoformat(m["data"]), AlturaVegetacao(m["altura_cm"]), m["responsavel"]
            )
        )
    return trecho


def prazo_para_dict(prazo: PrazoLegal) -> dict:
    return {"data_limite": prazo.data_limite.isoformat(), "origem": prazo.origem}


def prazo_de_dict(dados: dict) -> PrazoLegal:
    return PrazoLegal(date.fromisoformat(dados["data_limite"]), dados["origem"])


def ordem_para_dict(ordem: OrdemDeServico) -> dict:
    dados = asdict(ordem)
    dados.update(
        prioridade=ordem.prioridade.name,
        situacao=ordem.situacao.name,
        prazo=prazo_para_dict(ordem.prazo),
        epi_obrigatorio=list(ordem.epi_obrigatorio),
    )
    return dados


def ordem_de_dict(dados: dict) -> OrdemDeServico:
    return OrdemDeServico(
        **{
            **dados,
            "prioridade": Prioridade[dados["prioridade"]],
            "situacao": SituacaoDaOrdem[dados["situacao"]],
            "prazo": prazo_de_dict(dados["prazo"]),
            "epi_obrigatorio": tuple(dados["epi_obrigatorio"]),
        }
    )


def violacao_para_dict(violacao: ViolacaoContratual) -> dict:
    return {
        "trecho_id": violacao.trecho_id,
        "orgao_regulador": violacao.orgao_regulador,
        "altura_apurada_cm": violacao.altura_apurada_cm,
        "prazo_de_regularizacao": prazo_para_dict(violacao.prazo_de_regularizacao),
        "situacao": violacao.situacao.name,
    }


def violacao_de_dict(dados: dict) -> ViolacaoContratual:
    return ViolacaoContratual(
        dados["trecho_id"],
        dados["orgao_regulador"],
        dados["altura_apurada_cm"],
        prazo_de_dict(dados["prazo_de_regularizacao"]),
        SituacaoDaViolacao[dados["situacao"]],
    )
