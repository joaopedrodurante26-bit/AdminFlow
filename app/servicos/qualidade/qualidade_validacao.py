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

def validar_numero_positivo(valor):
    valor = valor.strip().replace(".", "").replace(",", ".")

    try:
        numero = float(valor)
        return numero > 0
    except ValueError:
        return False

def converter_data(data):
    return datetime.strptime(data, "%d/%m/%Y")

def validar_dados_controle_lote(dados, caminho_documento):
    campos_obrigatorios = [
        "Número do lote",
        "Data de envase",
        "Data de validade",
        "Quantidade produzida",
        "Linha de produção",
        "Responsável pela produção",
        "Responsável pela qualidade",
        "Produto",
        "Status do lote"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    if dados["Produto"] == "Selecione":
        return False, "Selecione o produto."

    if dados["Status do lote"] == "Selecione":
        return False, "Selecione o status do lote."

    if not validar_data(dados["Data de envase"]):
        return False, "Data de envase inválida. Use DD/MM/AAAA."

    if not validar_data(dados["Data de validade"]):
        return False, "Data de validade inválida. Use DD/MM/AAAA."

    data_envase = converter_data(dados["Data de envase"])
    data_validade = converter_data(dados["Data de validade"])

    if data_validade < data_envase:
        return False, "A data de validade não pode ser anterior à data de envase."

    if not validar_numero_positivo(dados["Quantidade produzida"]):
        return False, "Quantidade produzida inválida. Informe número maior que zero."

    if caminho_documento:
        caminho = Path(caminho_documento)

        if not caminho.exists():
            return False, "O documento anexado não foi encontrado."

        if caminho.is_dir():
            return False, "O item anexado não é um arquivo."

    return True, ""