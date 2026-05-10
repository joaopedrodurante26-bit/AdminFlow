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

def validar_dados_nf_emitida(dados, caminho_nf):
    campos_obrigatorios = [
        "Data de emissão",
        "Número da NF",
        "Cliente",
        "CNPJ/CPF do cliente",
        "Valor total",
        "Descrição",
        "Responsável pelo arquivamento",
        "Tipo de NF"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    if dados["Tipo de NF"] == "Selecione":
        return False, "Selecione o tipo de NF."

    if not validar_data(dados["Data de emissão"]):
        return False, "Data de emissão inválida. Use DD/MM/AAAA."

    if not validar_valor(dados["Valor total"]):
        return False, "Valor total inválido. Informe um valor maior que zero."

    if not caminho_nf:
        return False, "Selecione o arquivo da NF emitida."

    caminho = Path(caminho_nf)

    if not caminho.exists():
        return False, "O arquivo da NF selecionado não foi encontrado."

    if caminho.is_dir():
        return False, "O item selecionado não é um arquivo."

    return True, ""

def validar_dados_nf_recebida(dados, caminho_nf):
    campos_obrigatorios = [
        "Data de emissão",
        "Número da NF",
        "Fornecedor",
        "CNPJ/CPF do fornecedor",
        "Valor total",
        "Descrição",
        "Responsável pelo arquivamento",
        "Tipo de NF"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    if dados["Tipo de NF"] == "Selecione":
        return False, "Selecione o tipo de NF."

    if not validar_data(dados["Data de emissão"]):
        return False, "Data de emissão inválida. Use DD/MM/AAAA."

    if not validar_valor(dados["Valor total"]):
        return False, "Valor total inválido. Informe um valor maior que zero."

    if not caminho_nf:
        return False, "Selecione o arquivo da NF recebida."

    caminho = Path(caminho_nf)

    if not caminho.exists():
        return False, "O arquivo da NF selecionado não foi encontrado."

    if caminho.is_dir():
        return False, "O item selecionado não é um arquivo."

    return True, ""