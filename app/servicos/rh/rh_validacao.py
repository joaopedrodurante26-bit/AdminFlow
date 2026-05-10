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

    if dados["Setor"] == "Selecione":
        return False, "Selecione o setor do funcionário."

    if dados["Jornada de trabalho"] == "Selecione":
        return False, "Selecione a jornada de trabalho do funcionário."

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

def validar_competencia(competencia):
    partes = competencia.split("/")

    if len(partes) != 2:
        return False

    mes, ano = partes

    if not (mes.isdigit() and ano.isdigit()):
        return False

    if len(ano) != 4:
        return False

    mes = int(mes)

    return 1 <= mes <= 12

def validar_dados_folha_ponto(dados, caminho_arquivo):
    campos_obrigatorios = [
        "Competência",
        "Setor",
        "Tipo de folha",
        "Responsável pelo arquivamento"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    if dados["Setor"] == "Selecione":
        return False, "Selecione o setor."

    if dados["Tipo de folha"] == "Selecione":
        return False, "Selecione o tipo de folha."

    if not validar_competencia(dados["Competência"]):
        return False, "Competência inválida. Use MM/AAAA."

    if dados["Tipo de folha"] == "Individual":
        if not dados.get("Nome do funcionário", "").strip():
            return False, "Informe o nome do funcionário para folha individual."

    if not caminho_arquivo:
        return False, "Selecione o arquivo da folha de ponto."

    caminho = Path(caminho_arquivo)

    if not caminho.exists():
        return False, "O arquivo selecionado não foi encontrado."

    if caminho.is_dir():
        return False, "O item selecionado não é um arquivo."

    return True, ""

def validar_data(data):
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def converter_data(data):
    return datetime.strptime(data, "%d/%m/%Y")

def validar_dados_ferias(dados, caminho_documento):
    campos_obrigatorios = [
        "Nome do funcionário",
        "Setor",
        "Período aquisitivo início",
        "Período aquisitivo fim",
        "Início das férias",
        "Fim das férias",
        "Responsável pelo registro",
        "Status"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo, "").strip():
            return False, f"O campo '{campo}' é obrigatório."

    datas = [
        "Período aquisitivo início",
        "Período aquisitivo fim",
        "Início das férias",
        "Fim das férias"
    ]

    for campo in datas:
        if not validar_data(dados[campo]):
            return False, f"Data inválida no campo '{campo}'. Use DD/MM/AAAA."

    aquisitivo_inicio = converter_data(dados["Período aquisitivo início"])
    aquisitivo_fim = converter_data(dados["Período aquisitivo fim"])
    ferias_inicio = converter_data(dados["Início das férias"])
    ferias_fim = converter_data(dados["Fim das férias"])

    if aquisitivo_fim < aquisitivo_inicio:
        return False, "O fim do período aquisitivo não pode ser anterior ao início."

    if ferias_fim < ferias_inicio:
        return False, "O fim das férias não pode ser anterior ao início das férias."

    if caminho_documento:
        caminho = Path(caminho_documento)

        if not caminho.exists():
            return False, "O documento anexado não foi encontrado."

        if caminho.is_dir():
            return False, "O item anexado não é um arquivo."

    return True, ""