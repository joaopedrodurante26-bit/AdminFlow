from pathlib import Path
from datetime import datetime


def validar_data(data):
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def validar_valor(valor):
    valor = valor.strip().replace(".", "").replace(",", ".")

    try:
        numero = float(valor)
        return numero > 0
    except ValueError:
        return False


def validar_dados_comprovante(dados, caminho_comprovante):
    campos_obrigatorios = [
        "Data do comprovante",
        "Descrição",
        "Favorecido/Pagador",
        "Valor",
        "Tipo de comprovante",
        "Categoria"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    if dados["Tipo de comprovante"] == "Selecione":
        return False, "Selecione o tipo de comprovante."

    if dados["Categoria"] == "Selecione":
        return False, "Selecione a categoria do comprovante."

    if not validar_data(dados["Data do comprovante"]):
        return False, "Data inválida. Use o formato DD/MM/AAAA."

    if not validar_valor(dados["Valor"]):
        return False, "Valor inválido. Informe um valor maior que zero."

    if not caminho_comprovante:
        return False, "Selecione um arquivo de comprovante."

    caminho = Path(caminho_comprovante)

    if not caminho.exists():
        return False, "O arquivo selecionado não foi encontrado."

    if caminho.is_dir():
        return False, "O item selecionado não é um arquivo."

    return True, ""