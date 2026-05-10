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

def validar_dados_conta_a_pagar(dados, caminho_documento):
    campos_obrigatorios = [
        "Data de emissão",
        "Data de vencimento",
        "Fornecedor/Favorecido",
        "Descrição",
        "Valor",
        "Categoria",
        "Forma de pagamento",
        "Status"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    if dados["Categoria"] == "Selecione":
        return False, "Selecione a categoria da conta."

    if dados["Forma de pagamento"] == "Selecione":
        return False, "Selecione a forma de pagamento."

    if not validar_data(dados["Data de emissão"]):
        return False, "Data de emissão inválida. Use o formato DD/MM/AAAA."

    if not validar_data(dados["Data de vencimento"]):
        return False, "Data de vencimento inválida. Use o formato DD/MM/AAAA."

    if not validar_valor(dados["Valor"]):
        return False, "Valor inválido. Informe um valor maior que zero."

    if caminho_documento:
        caminho = Path(caminho_documento)

        if not caminho.exists():
            return False, "O documento anexado não foi encontrado."

        if caminho.is_dir():
            return False, "O item anexado não é um arquivo."

    return True, ""

def validar_dados_conta_a_receber(dados, caminho_documento):
    campos_obrigatorios = [
        "Data de emissão",
        "Data prevista de recebimento",
        "Cliente/Pagador",
        "Descrição",
        "Valor",
        "Categoria",
        "Forma de recebimento",
        "Status"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    if dados["Categoria"] == "Selecione":
        return False, "Selecione a categoria da conta."

    if dados["Forma de recebimento"] == "Selecione":
        return False, "Selecione a forma de recebimento."

    if not validar_data(dados["Data de emissão"]):
        return False, "Data de emissão inválida. Use o formato DD/MM/AAAA."

    if not validar_data(dados["Data prevista de recebimento"]):
        return False, "Data prevista de recebimento inválida. Use o formato DD/MM/AAAA."

    if not validar_valor(dados["Valor"]):
        return False, "Valor inválido. Informe um valor maior que zero."

    if caminho_documento:
        caminho = Path(caminho_documento)

        if not caminho.exists():
            return False, "O documento anexado não foi encontrado."

        if caminho.is_dir():
            return False, "O item anexado não é um arquivo."

    return True, ""

def validar_competencia(competencia):
    partes = competencia.split("/")

    if len(partes) != 2:
        return False

    mes, ano = partes

    if not (mes.isdigit() and ano.isdigit()):
        return False

    mes = int(mes)

    return 1 <= mes <= 12 and len(ano) == 4

def validar_dados_extrato_bancario(dados, caminho_extrato):
    campos_obrigatorios = [
        "Competência",
        "Banco",
        "Tipo de conta",
        "Agência",
        "Conta"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    if dados["Banco"] == "Selecione":
        return False, "Selecione o banco."

    if dados["Tipo de conta"] == "Selecione":
        return False, "Selecione o tipo de conta."

    if not validar_competencia(dados["Competência"]):
        return False, "Competência inválida. Use MM/AAAA."

    if not caminho_extrato:
        return False, "Selecione um arquivo de extrato."

    caminho = Path(caminho_extrato)

    if not caminho.exists():
        return False, "O extrato selecionado não foi encontrado."

    if caminho.is_dir():
        return False, "O item selecionado não é um arquivo."

    return True, ""