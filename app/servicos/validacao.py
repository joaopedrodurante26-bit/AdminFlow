from pathlib import Path
from datetime import datetime


def apenas_digitos(texto):
    return "".join(caractere for caractere in texto if caractere.isdigit())


def validar_cpf(cpf):
    cpf = apenas_digitos(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)

    digito_1 = (soma * 10) % 11
    if digito_1 == 10:
        digito_1 = 0

    if digito_1 != int(cpf[9]):
        return False

    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)

    digito_2 = (soma * 10) % 11
    if digito_2 == 10:
        digito_2 = 0

    return digito_2 == int(cpf[10])


def validar_data(data):
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def validar_documentos(documentos):
    if not documentos:
        return False, "É necessário anexar pelo menos um documento."

    for documento in documentos:
        caminho = Path(documento)

        if not caminho.exists():
            return False, f"Documento não encontrado: {caminho.name}"

        if caminho.is_dir():
            return False, f"O item selecionado não é um arquivo: {caminho.name}"

    return True, ""


def validar_dados_funcionario(dados, documentos):
    campos_obrigatorios = [
        "Nome completo",
        "CPF",
        "Cargo",
        "Setor",
        "Data de admissão",
        "Jornada de trabalho"
    ]

    for campo in campos_obrigatorios:
        valor = dados.get(campo, "").strip()

        if not valor:
            return False, f"O campo '{campo}' é obrigatório."

    nome = dados["Nome completo"].strip()

    if len(nome.split()) < 2:
        return False, "Informe o nome completo do funcionário."

    if not validar_cpf(dados["CPF"]):
        return False, "CPF inválido. Verifique o número informado."

    if not validar_data(dados["Data de admissão"]):
        return False, "Data de admissão inválida. Use o formato DD/MM/AAAA."

    documentos_validos, mensagem = validar_documentos(documentos)

    if not documentos_validos:
        return False, mensagem

    return True, ""