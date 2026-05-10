from pathlib import Path
from datetime import datetime


def validar_data(data):
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_dados_analise_agua(dados, caminho_arquivo):
    campos_obrigatorios = [
        "Data da análise",
        "Ponto de coleta",
        "Laboratório",
        "Responsável técnico",
        "Descrição",
        "Responsável pelo arquivamento",
        "Tipo de análise",
        "Resultado"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    if dados["Tipo de análise"] == "Selecione":
        return False, "Selecione o tipo de análise."

    if dados["Resultado"] == "Selecione":
        return False, "Selecione o resultado."

    if not validar_data(dados["Data da análise"]):
        return False, "Data da análise inválida. Use DD/MM/AAAA."

    if len(dados["Descrição"]) < 5:
        return False, "A descrição está muito curta."

    if not caminho_arquivo:
        return False, "Selecione o arquivo da análise da água."

    caminho = Path(caminho_arquivo)

    if not caminho.exists():
        return False, "O arquivo selecionado não foi encontrado."

    if caminho.is_dir():
        return False, "O item selecionado não é um arquivo."

    return True, ""