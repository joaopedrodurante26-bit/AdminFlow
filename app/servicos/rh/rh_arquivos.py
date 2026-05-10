from pathlib import Path
from datetime import datetime
import shutil

from app.servicos.logs import registrar_log
from app.servicos.configuracoes import obter_pasta_base
from app.servicos.utils import normalizar_nome


def gerar_nome_documento(data_cadastro, nome_funcionario, tipo_documento, caminho_origem, contador):
    extensao = caminho_origem.suffix.lower()

    tipo = normalizar_nome(tipo_documento)

    return f"{data_cadastro}_{tipo}_{nome_funcionario}_{contador:02d}{extensao}"

def criar_pasta_funcionario(dados, documentos):
    PASTA_BASE = obter_pasta_base()
    
    nome_funcionario = normalizar_nome(dados["Nome completo"])
    data_cadastro = datetime.now().strftime("%Y-%m-%d")
    data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    pasta_rh = PASTA_BASE / "03_RH" / "Funcionarios_Ativos"
    pasta_final = pasta_rh / f"{data_cadastro}_{nome_funcionario}"

    pasta_temp = PASTA_BASE / "99_TEMPORARIO" / f"TEMP_CADASTRO_{data_hora}_{nome_funcionario}"

    if pasta_final.exists():
        raise FileExistsError("Já existe uma pasta para este funcionário.")

    try:
        subpastas = [
            "01_Documentos_Pessoais",
            "02_Contrato",
            "03_Exames",
            "04_Ponto",
            "05_Ferias",
            "06_Advertencias"
        ]

        pasta_temp.mkdir(parents=True)

        for subpasta in subpastas:
            (pasta_temp / subpasta).mkdir()

        caminho_cadastro = pasta_temp / "cadastro_funcionario.txt"

        with open(caminho_cadastro, "w", encoding="utf-8") as arquivo:
            arquivo.write("CADASTRO DE FUNCIONÁRIO\n")
            arquivo.write("=" * 40 + "\n\n")

            for campo, valor in dados.items():
                arquivo.write(f"{campo}: {valor}\n")

            arquivo.write(f"\nData de criação do cadastro: {data_cadastro}\n")

        for contador, documento in enumerate(documentos, start=1):
            origem = Path(documento["caminho"])

            if not origem.exists():
                raise FileNotFoundError(f"Documento não encontrado: {origem}")

            pasta_destino = pasta_temp / documento["destino"]

            novo_nome = gerar_nome_documento(
                data_cadastro=data_cadastro,
                nome_funcionario=nome_funcionario,
                tipo_documento=documento["tipo"],
                caminho_origem=origem,
                contador=contador
            )

            destino = pasta_destino / novo_nome

            shutil.copy2(origem, destino)
            registrar_log(f"Documento arquivado: {destino.name} | Destino: {pasta_destino}")

        pasta_rh.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pasta_temp), str(pasta_final))
        registrar_log(f"Funcionário cadastrado: {nome_funcionario} | Pasta criada: {pasta_final}")

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)
        registrar_log(f"ERRO no cadastro de funcionário: {erro}")
        raise

def verificar_ou_criar_estrutura():
    pasta_base = obter_pasta_base()
    estrutura = obter_estrutura_padrao()

    pastas_criadas = []

    pasta_base.mkdir(parents=True, exist_ok=True)

    for pasta_principal, subpastas in estrutura.items():
        caminho_principal = pasta_base / pasta_principal

        if not caminho_principal.exists():
            caminho_principal.mkdir()
            pastas_criadas.append(str(caminho_principal))

        for subpasta in subpastas:
            caminho_subpasta = caminho_principal / subpasta

            if not caminho_subpasta.exists():
                caminho_subpasta.mkdir()
                pastas_criadas.append(str(caminho_subpasta))

    return pastas_criadas

def estrutura_existe():
    pasta_base = obter_pasta_base()

    pastas_obrigatorias = [
        "01_ADMINISTRATIVO",
        "02_FINANCEIRO",
        "03_RH",
        "04_FISCAL_CONTABIL",
        "05_COMERCIAL",
        "06_LOGISTICA",
        "07_QUALIDADE",
        "08_CONTRATOS",
        "09_RELATORIOS",
        "10_MODELOS",
        "11_DIGITALIZADOS",
        "12_BACKUP_LOCAL",
        "99_TEMPORARIO"
    ]

    if not pasta_base.exists():
        return False

    for pasta in pastas_obrigatorias:
        if not (pasta_base / pasta).exists():
            return False

    return True

def obter_ano_mes_competencia(competencia):
    meses = [
        "01_Janeiro",
        "02_Fevereiro",
        "03_Marco",
        "04_Abril",
        "05_Maio",
        "06_Junho",
        "07_Julho",
        "08_Agosto",
        "09_Setembro",
        "10_Outubro",
        "11_Novembro",
        "12_Dezembro"
    ]

    mes, ano = competencia.split("/")

    return ano, meses[int(mes) - 1]

def gerar_nome_folha_ponto(dados, caminho_origem):
    competencia = dados["Competência"].replace("/", "-")
    setor = normalizar_nome(dados["Setor"])
    tipo = normalizar_nome(dados["Tipo de folha"])
    extensao = caminho_origem.suffix.lower()

    nome_funcionario = dados.get("Nome do funcionário", "").strip()

    if nome_funcionario:
        nome_funcionario = normalizar_nome(nome_funcionario)
    else:
        nome_funcionario = "GERAL"

    return f"{competencia}_FOLHA_PONTO_{tipo}_{setor}_{nome_funcionario}{extensao}"

def gerar_registro_folha_ponto(dados, nome_arquivo):
    linhas = []

    linhas.append("REGISTRO DE FOLHA DE PONTO")
    linhas.append("=" * 40)
    linhas.append("")

    for campo, valor in dados.items():
        linhas.append(f"{campo}: {valor}")

    linhas.append("")
    linhas.append(f"Arquivo arquivado: {nome_arquivo}")
    linhas.append(f"Data do arquivamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    return "\n".join(linhas)

def arquivar_folha_ponto(dados, caminho_arquivo):
    pasta_base = obter_pasta_base()
    origem = Path(caminho_arquivo)

    ano, mes = obter_ano_mes_competencia(dados["Competência"])

    pasta_final = (
        pasta_base
        / "03_RH"
        / "Controle_Ponto"
        / ano
        / mes
    )

    pasta_temp = (
        pasta_base
        / "99_TEMPORARIO"
        / f"TEMP_FOLHA_PONTO_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        pasta_temp.mkdir(parents=True, exist_ok=False)

        novo_nome = gerar_nome_folha_ponto(dados, origem)
        destino_temp = pasta_temp / novo_nome

        shutil.copy2(origem, destino_temp)

        registro = gerar_registro_folha_ponto(dados, novo_nome)
        registro_temp = pasta_temp / f"{destino_temp.stem}_registro.txt"

        with open(registro_temp, "w", encoding="utf-8") as arquivo:
            arquivo.write(registro)

        pasta_final.mkdir(parents=True, exist_ok=True)

        destino_final = pasta_final / novo_nome

        if destino_final.exists():
            raise FileExistsError("Já existe uma folha de ponto com esse nome.")

        shutil.move(str(destino_temp), str(destino_final))
        shutil.move(str(registro_temp), str(pasta_final / registro_temp.name))

        shutil.rmtree(pasta_temp)

        registrar_log(
            f"Folha de ponto arquivada: {destino_final.name} | Destino: {pasta_final}"
        )

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        registrar_log(
            f"ERRO ao arquivar folha de ponto: {erro}"
        )

        raise

def converter_data_para_iso(data):
    return datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")

def gerar_nome_registro_ferias(dados):
    inicio_iso = converter_data_para_iso(dados["Início das férias"])
    fim_iso = converter_data_para_iso(dados["Fim das férias"])

    funcionario = normalizar_nome(dados["Nome do funcionário"])
    status = normalizar_nome(dados["Status"])

    return f"{inicio_iso}_A_{fim_iso}_FERIAS_{funcionario}_{status}.txt"

def gerar_nome_anexo_ferias(dados, caminho_origem):
    inicio_iso = converter_data_para_iso(dados["Início das férias"])
    fim_iso = converter_data_para_iso(dados["Fim das férias"])

    funcionario = normalizar_nome(dados["Nome do funcionário"])
    extensao = caminho_origem.suffix.lower()

    return f"{inicio_iso}_A_{fim_iso}_ANEXO_FERIAS_{funcionario}{extensao}"

def gerar_registro_ferias(dados, nome_anexo=None):
    linhas = []

    linhas.append("REGISTRO DE FÉRIAS")
    linhas.append("=" * 40)
    linhas.append("")

    for campo, valor in dados.items():
        linhas.append(f"{campo}: {valor}")

    linhas.append("")
    linhas.append(f"Data do registro: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    if nome_anexo:
        linhas.append(f"Documento anexado: {nome_anexo}")
    else:
        linhas.append("Documento anexado: Nenhum")

    return "\n".join(linhas)

def registrar_ferias(dados, caminho_documento=""):
    pasta_base = obter_pasta_base()

    funcionario = normalizar_nome(dados["Nome do funcionário"])
    ano_inicio = datetime.strptime(dados["Início das férias"], "%d/%m/%Y").strftime("%Y")

    pasta_final = (
        pasta_base
        / "03_RH"
        / "Ferias"
        / ano_inicio
        / funcionario
    )

    pasta_temp = (
        pasta_base
        / "99_TEMPORARIO"
        / f"TEMP_FERIAS_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        pasta_temp.mkdir(parents=True, exist_ok=False)

        nome_anexo = None

        if caminho_documento:
            origem = Path(caminho_documento)

            if not origem.exists():
                raise FileNotFoundError("Documento anexado não encontrado.")

            nome_anexo = gerar_nome_anexo_ferias(dados, origem)
            destino_anexo_temp = pasta_temp / nome_anexo

            shutil.copy2(origem, destino_anexo_temp)

        nome_registro = gerar_nome_registro_ferias(dados)
        registro_temp = pasta_temp / nome_registro

        registro = gerar_registro_ferias(dados, nome_anexo)

        with open(registro_temp, "w", encoding="utf-8") as arquivo:
            arquivo.write(registro)

        pasta_final.mkdir(parents=True, exist_ok=True)

        destino_registro_final = pasta_final / nome_registro

        if destino_registro_final.exists():
            raise FileExistsError("Já existe registro de férias com esse nome.")

        shutil.move(str(registro_temp), str(destino_registro_final))

        if nome_anexo:
            shutil.move(
                str(pasta_temp / nome_anexo),
                str(pasta_final / nome_anexo)
            )

        shutil.rmtree(pasta_temp)

        registrar_log(
            f"Férias registradas: {nome_registro} | Destino: {pasta_final}"
        )

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        registrar_log(
            f"ERRO ao registrar férias: {erro}"
        )

        raise

def gerar_nome_registro_advertencia(dados):
    data_iso = converter_data_para_iso(dados["Data da ocorrência"])
    funcionario = normalizar_nome(dados["Nome do funcionário"])
    tipo = normalizar_nome(dados["Tipo de advertência"])
    gravidade = normalizar_nome(dados["Gravidade"])

    return f"{data_iso}_ADVERTENCIA_{tipo}_{funcionario}_{gravidade}.txt"

def gerar_nome_anexo_advertencia(dados, caminho_origem):
    data_iso = converter_data_para_iso(dados["Data da ocorrência"])
    funcionario = normalizar_nome(dados["Nome do funcionário"])
    tipo = normalizar_nome(dados["Tipo de advertência"])
    extensao = caminho_origem.suffix.lower()

    return f"{data_iso}_ANEXO_ADVERTENCIA_{tipo}_{funcionario}{extensao}"

def gerar_registro_advertencia(dados, nome_anexo=None):
    linhas = []

    linhas.append("REGISTRO DE ADVERTÊNCIA")
    linhas.append("=" * 40)
    linhas.append("")

    for campo, valor in dados.items():
        linhas.append(f"{campo}: {valor}")

    linhas.append("")
    linhas.append(f"Data do registro: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    if nome_anexo:
        linhas.append(f"Documento anexado: {nome_anexo}")
    else:
        linhas.append("Documento anexado: Nenhum")

    return "\n".join(linhas)

def registrar_advertencia(dados, caminho_documento=""):
    pasta_base = obter_pasta_base()

    funcionario = normalizar_nome(dados["Nome do funcionário"])
    ano = datetime.strptime(dados["Data da ocorrência"], "%d/%m/%Y").strftime("%Y")

    pasta_final = (
        pasta_base
        / "03_RH"
        / "Advertencias"
        / ano
        / funcionario
    )

    pasta_temp = (
        pasta_base
        / "99_TEMPORARIO"
        / f"TEMP_ADVERTENCIA_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        pasta_temp.mkdir(parents=True, exist_ok=False)

        nome_anexo = None

        if caminho_documento:
            origem = Path(caminho_documento)

            if not origem.exists():
                raise FileNotFoundError("Documento anexado não encontrado.")

            nome_anexo = gerar_nome_anexo_advertencia(dados, origem)
            destino_anexo_temp = pasta_temp / nome_anexo
            shutil.copy2(origem, destino_anexo_temp)

        nome_registro = gerar_nome_registro_advertencia(dados)
        registro_temp = pasta_temp / nome_registro

        registro = gerar_registro_advertencia(dados, nome_anexo)

        with open(registro_temp, "w", encoding="utf-8") as arquivo:
            arquivo.write(registro)

        pasta_final.mkdir(parents=True, exist_ok=True)

        destino_registro_final = pasta_final / nome_registro

        if destino_registro_final.exists():
            raise FileExistsError("Já existe registro de advertência com esse nome.")

        shutil.move(str(registro_temp), str(destino_registro_final))

        if nome_anexo:
            shutil.move(
                str(pasta_temp / nome_anexo),
                str(pasta_final / nome_anexo)
            )

        shutil.rmtree(pasta_temp)

        registrar_log(
            f"Advertência registrada: {nome_registro} | Destino: {pasta_final}"
        )

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        registrar_log(
            f"ERRO ao registrar advertência: {erro}"
        )

        raise