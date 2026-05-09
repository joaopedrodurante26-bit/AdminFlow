from pathlib import Path
from datetime import datetime


PASTA_LOGS = Path("logs")


def registrar_log(mensagem):
    PASTA_LOGS.mkdir(exist_ok=True)

    data_atual = datetime.now().strftime("%Y-%m-%d")
    horario = datetime.now().strftime("%H:%M:%S")

    arquivo_log = PASTA_LOGS / f"{data_atual}.log"

    with open(arquivo_log, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{horario}] {mensagem}\n")