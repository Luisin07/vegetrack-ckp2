"""
erros.py
Erros dos casos de uso -- traduzidos em mensagem amigável pela CLI.
"""


class TrechoNaoEncontrado(LookupError):
    def __init__(self, trecho_id: str) -> None:
        super().__init__(f"Trecho '{trecho_id}' não existe na base de monitoramento.")


class TrechoSemMedicao(LookupError):
    def __init__(self, trecho_id: str) -> None:
        super().__init__(f"Trecho '{trecho_id}' ainda não tem medição para ser avaliado.")


class OrdemNaoEncontrada(LookupError):
    def __init__(self, numero: str) -> None:
        super().__init__(f"Ordem de serviço '{numero}' não existe.")
