"""
armazenamento_em_arquivo.py
Persistência de trechos, ordens e violações num único arquivo JSON -- usada pelos casos de uso.
Persistência em arquivo basta no CKP2; banco real fica para o Checkpoint 3.
"""

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

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


class ArmazenamentoEmArquivo:
    def __init__(self, caminho: Path) -> None:
        self._caminho = Path(caminho)
        self.trechos: dict[str, Trecho] = {}
        self.ordens: dict[str, OrdemDeServico] = {}
        self.violacoes: list[ViolacaoContratual] = []
        if self._caminho.exists():
            self._carregar()

    # ===== BLOCO 1: consultas =====
    def buscar_trecho(self, identificacao: str) -> Trecho | None:
        return self.trechos.get(identificacao)

    def ordem_aberta_do_trecho(self, trecho_id: str) -> OrdemDeServico | None:
        abertas = [o for o in self.ordens.values() if o.trecho_id == trecho_id and o.em_aberto]
        return abertas[0] if abertas else None

    def violacao_ativa_do_trecho(self, trecho_id: str) -> ViolacaoContratual | None:
        ativas = [v for v in self.violacoes if v.trecho_id == trecho_id and v.ativa]
        return ativas[0] if ativas else None

    def proximo_numero_de_ordem(self) -> str:
        return f"OS-{len(self.ordens) + 1:04d}"

    # ===== BLOCO 2: alteracoes =====
    def salvar_trecho(self, trecho: Trecho) -> None:
        self.trechos[trecho.identificacao] = trecho

    def salvar_ordem(self, ordem: OrdemDeServico) -> None:
        self.ordens[ordem.numero] = ordem

    def salvar_violacao(self, violacao: ViolacaoContratual) -> None:
        if violacao not in self.violacoes:
            self.violacoes.append(violacao)

    def persistir(self) -> None:
        self._caminho.parent.mkdir(parents=True, exist_ok=True)
        documento = {
            "trechos": [_trecho_para_dict(t) for t in self.trechos.values()],
            "ordens": [_ordem_para_dict(o) for o in self.ordens.values()],
            "violacoes": [_violacao_para_dict(v) for v in self.violacoes],
        }
        self._caminho.write_text(json.dumps(documento, ensure_ascii=False, indent=2), "utf-8")

    # ===== BLOCO 3: carga_do_arquivo =====
    def _carregar(self) -> None:
        documento = json.loads(self._caminho.read_text("utf-8"))
        for dados in documento.get("trechos", []):
            trecho = _trecho_de_dict(dados)
            self.trechos[trecho.identificacao] = trecho
        for dados in documento.get("ordens", []):
            ordem = _ordem_de_dict(dados)
            self.ordens[ordem.numero] = ordem
        self.violacoes = [_violacao_de_dict(d) for d in documento.get("violacoes", [])]


# ===== BLOCO 4: mapeamento_dominio_json =====
def _trecho_para_dict(trecho: Trecho) -> dict:
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


def _trecho_de_dict(dados: dict) -> Trecho:
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


def _prazo_para_dict(prazo: PrazoLegal) -> dict:
    return {"data_limite": prazo.data_limite.isoformat(), "origem": prazo.origem}


def _prazo_de_dict(dados: dict) -> PrazoLegal:
    return PrazoLegal(date.fromisoformat(dados["data_limite"]), dados["origem"])


def _ordem_para_dict(ordem: OrdemDeServico) -> dict:
    dados = asdict(ordem)
    dados.update(
        prioridade=ordem.prioridade.name,
        situacao=ordem.situacao.name,
        prazo=_prazo_para_dict(ordem.prazo),
        epi_obrigatorio=list(ordem.epi_obrigatorio),
    )
    return dados


def _ordem_de_dict(dados: dict) -> OrdemDeServico:
    return OrdemDeServico(
        **{
            **dados,
            "prioridade": Prioridade[dados["prioridade"]],
            "situacao": SituacaoDaOrdem[dados["situacao"]],
            "prazo": _prazo_de_dict(dados["prazo"]),
            "epi_obrigatorio": tuple(dados["epi_obrigatorio"]),
        }
    )


def _violacao_para_dict(violacao: ViolacaoContratual) -> dict:
    return {
        "trecho_id": violacao.trecho_id,
        "orgao_regulador": violacao.orgao_regulador,
        "altura_apurada_cm": violacao.altura_apurada_cm,
        "prazo_de_regularizacao": _prazo_para_dict(violacao.prazo_de_regularizacao),
        "situacao": violacao.situacao.name,
    }


def _violacao_de_dict(dados: dict) -> ViolacaoContratual:
    return ViolacaoContratual(
        dados["trecho_id"],
        dados["orgao_regulador"],
        dados["altura_apurada_cm"],
        _prazo_de_dict(dados["prazo_de_regularizacao"]),
        SituacaoDaViolacao[dados["situacao"]],
    )
