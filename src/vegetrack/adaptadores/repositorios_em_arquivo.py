"""
repositorios_em_arquivo.py
Adaptadores de saída que gravam cada repositório num arquivo JSON da pasta de dados.
Herdam o comportamento em memória e só acrescentam a carga e a gravação (DT-05 no DEBT.md).
"""

import json
from pathlib import Path

from vegetrack.adaptadores.mapeamento_json import (
    ordem_de_dict,
    ordem_para_dict,
    trecho_de_dict,
    trecho_para_dict,
    violacao_de_dict,
    violacao_para_dict,
)
from vegetrack.adaptadores.repositorios_em_memoria import (
    RepositorioDeOrdensEmMemoria,
    RepositorioDeTrechosEmMemoria,
    RepositorioDeViolacoesEmMemoria,
)
from vegetrack.manutencao.dominio.ordem_de_servico import OrdemDeServico
from vegetrack.manutencao.dominio.violacao_contratual import ViolacaoContratual
from vegetrack.monitoramento.dominio.trecho import Trecho


def _ler(caminho: Path) -> list[dict]:
    return json.loads(caminho.read_text("utf-8")) if caminho.exists() else []


def _gravar(caminho: Path, registros: list[dict]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(registros, ensure_ascii=False, indent=2), "utf-8")


class RepositorioDeTrechosEmArquivo(RepositorioDeTrechosEmMemoria):
    def __init__(self, pasta: Path) -> None:
        super().__init__()
        self._caminho = Path(pasta) / "trechos.json"
        for dados in _ler(self._caminho):
            super().salvar(trecho_de_dict(dados))

    def salvar(self, trecho: Trecho) -> None:
        super().salvar(trecho)
        _gravar(self._caminho, [trecho_para_dict(t) for t in self.listar()])


class RepositorioDeOrdensEmArquivo(RepositorioDeOrdensEmMemoria):
    def __init__(self, pasta: Path) -> None:
        super().__init__()
        self._caminho = Path(pasta) / "ordens.json"
        for dados in _ler(self._caminho):
            super().salvar(ordem_de_dict(dados))

    def salvar(self, ordem: OrdemDeServico) -> None:
        super().salvar(ordem)
        _gravar(self._caminho, [ordem_para_dict(o) for o in self.listar()])


class RepositorioDeViolacoesEmArquivo(RepositorioDeViolacoesEmMemoria):
    def __init__(self, pasta: Path) -> None:
        super().__init__()
        self._caminho = Path(pasta) / "violacoes.json"
        for dados in _ler(self._caminho):
            super().salvar(violacao_de_dict(dados))

    def salvar(self, violacao: ViolacaoContratual) -> None:
        super().salvar(violacao)
        _gravar(self._caminho, [violacao_para_dict(v) for v in self.listar()])
