from pathlib import Path
from datetime import datetime
import shutil

from app.servicos.configuracoes import obter_pasta_base
from app.servicos.logs import registrar_log
from app.servicos.utils import normalizar_nome


def converter_data_para_iso(data):
    return datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")

def obter_ano_mes(data):
    data_obj = datetime.strptime(data, "%d/%m/%Y")

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

    return str(data_obj.year), meses[data_obj.month - 1]

def gerar_nome_nf_emitida(dados, caminho_origem):
    data_iso = converter_data_para_iso(dados["Data de emissão"])
    numero_nf = normalizar_nome(dados["Número da NF"])
    cliente = normalizar_nome(dados["Cliente"])
    tipo_nf = normalizar_nome(dados["Tipo de NF"])
    extensao = caminho_origem.suffix.lower()

    return f"{data_iso}_NF_EMITIDA_{numero_nf}_{tipo_nf}_{cliente}{extensao}"

def gerar_registro_nf_emitida(dados, nome_arquivo):
    linhas = []

    linhas.append("REGISTRO DE NF EMITIDA")
    linhas.append("=" * 40)
    linhas.append("")

    for campo, valor in dados.items():
        linhas.append(f"{campo}: {valor}")

    linhas.append("")
    linhas.append(f"Arquivo arquivado: {nome_arquivo}")
    linhas.append(f"Data do arquivamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    return "\n".join(linhas)

def arquivar_nf_emitida(dados, caminho_nf):
    pasta_base = obter_pasta_base()
    origem = Path(caminho_nf)

    if not origem.exists():
        raise FileNotFoundError("Arquivo da NF não encontrado.")

    ano, mes = obter_ano_mes(dados["Data de emissão"])

    pasta_final = (
        pasta_base
        / "04_FISCAL_CONTABIL"
        / "NF_Emitidas"
        / ano
        / mes
    )

    pasta_temp = (
        pasta_base
        / "99_TEMPORARIO"
        / f"TEMP_NF_EMITIDA_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        pasta_temp.mkdir(parents=True, exist_ok=False)

        novo_nome = gerar_nome_nf_emitida(dados, origem)
        destino_temp = pasta_temp / novo_nome

        shutil.copy2(origem, destino_temp)

        registro = gerar_registro_nf_emitida(dados, novo_nome)
        registro_temp = pasta_temp / f"{destino_temp.stem}_registro.txt"

        with open(registro_temp, "w", encoding="utf-8") as arquivo:
            arquivo.write(registro)

        pasta_final.mkdir(parents=True, exist_ok=True)

        destino_final = pasta_final / novo_nome

        if destino_final.exists():
            raise FileExistsError("Já existe uma NF emitida com esse nome no destino.")

        shutil.move(str(destino_temp), str(destino_final))
        shutil.move(str(registro_temp), str(pasta_final / registro_temp.name))

        shutil.rmtree(pasta_temp)

        registrar_log(
            f"NF emitida arquivada: {destino_final.name} | Destino: {pasta_final}"
        )

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        registrar_log(
            f"ERRO ao arquivar NF emitida: {erro}"
        )

        raise

def gerar_nome_nf_recebida(dados, caminho_origem):
    data_iso = converter_data_para_iso(dados["Data de emissão"])
    numero_nf = normalizar_nome(dados["Número da NF"])
    fornecedor = normalizar_nome(dados["Fornecedor"])
    tipo_nf = normalizar_nome(dados["Tipo de NF"])
    extensao = caminho_origem.suffix.lower()

    return f"{data_iso}_NF_RECEBIDA_{numero_nf}_{tipo_nf}_{fornecedor}{extensao}"

def gerar_registro_nf_recebida(dados, nome_arquivo):
    linhas = []

    linhas.append("REGISTRO DE NF RECEBIDA")
    linhas.append("=" * 40)
    linhas.append("")

    for campo, valor in dados.items():
        linhas.append(f"{campo}: {valor}")

    linhas.append("")
    linhas.append(f"Arquivo arquivado: {nome_arquivo}")
    linhas.append(f"Data do arquivamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    return "\n".join(linhas)

def arquivar_nf_recebida(dados, caminho_nf):
    pasta_base = obter_pasta_base()
    origem = Path(caminho_nf)

    if not origem.exists():
        raise FileNotFoundError("Arquivo da NF não encontrado.")

    ano, mes = obter_ano_mes(dados["Data de emissão"])

    pasta_final = (
        pasta_base
        / "04_FISCAL_CONTABIL"
        / "NF_Recebidas"
        / ano
        / mes
    )

    pasta_temp = (
        pasta_base
        / "99_TEMPORARIO"
        / f"TEMP_NF_RECEBIDA_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        pasta_temp.mkdir(parents=True, exist_ok=False)

        novo_nome = gerar_nome_nf_recebida(dados, origem)
        destino_temp = pasta_temp / novo_nome

        shutil.copy2(origem, destino_temp)

        registro = gerar_registro_nf_recebida(dados, novo_nome)
        registro_temp = pasta_temp / f"{destino_temp.stem}_registro.txt"

        with open(registro_temp, "w", encoding="utf-8") as arquivo:
            arquivo.write(registro)

        pasta_final.mkdir(parents=True, exist_ok=True)

        destino_final = pasta_final / novo_nome

        if destino_final.exists():
            raise FileExistsError("Já existe uma NF recebida com esse nome no destino.")

        shutil.move(str(destino_temp), str(destino_final))
        shutil.move(str(registro_temp), str(pasta_final / registro_temp.name))

        shutil.rmtree(pasta_temp)

        registrar_log(
            f"NF recebida arquivada: {destino_final.name} | Destino: {pasta_final}"
        )

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        registrar_log(
            f"ERRO ao arquivar NF recebida: {erro}"
        )

        raise

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

def gerar_nome_guia_imposto(dados, caminho_origem):
    competencia = dados["Competência"].replace("/", "-")
    vencimento_iso = converter_data_para_iso(dados["Data de vencimento"])
    imposto = normalizar_nome(dados["Tipo de imposto"])
    status = normalizar_nome(dados["Status"])
    descricao = normalizar_nome(dados["Descrição"])
    extensao = caminho_origem.suffix.lower()

    return f"{competencia}_GUIA_{imposto}_{descricao}_VENC_{vencimento_iso}_{status}{extensao}"

def gerar_registro_guia_imposto(dados, nome_arquivo):
    linhas = []

    linhas.append("REGISTRO DE GUIA DE IMPOSTO")
    linhas.append("=" * 40)
    linhas.append("")

    for campo, valor in dados.items():
        linhas.append(f"{campo}: {valor}")

    linhas.append("")
    linhas.append(f"Arquivo arquivado: {nome_arquivo}")
    linhas.append(f"Data do arquivamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    return "\n".join(linhas)

def arquivar_guia_imposto(dados, caminho_guia):
    pasta_base = obter_pasta_base()
    origem = Path(caminho_guia)

    if not origem.exists():
        raise FileNotFoundError("Arquivo da guia não encontrado.")

    ano, mes = obter_ano_mes_competencia(dados["Competência"])
    imposto = normalizar_nome(dados["Tipo de imposto"])

    pasta_final = (
        pasta_base
        / "04_FISCAL_CONTABIL"
        / "Impostos"
        / imposto
        / ano
        / mes
    )

    pasta_temp = (
        pasta_base
        / "99_TEMPORARIO"
        / f"TEMP_GUIA_IMPOSTO_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        pasta_temp.mkdir(parents=True, exist_ok=False)

        novo_nome = gerar_nome_guia_imposto(dados, origem)
        destino_temp = pasta_temp / novo_nome

        shutil.copy2(origem, destino_temp)

        registro = gerar_registro_guia_imposto(dados, novo_nome)
        registro_temp = pasta_temp / f"{destino_temp.stem}_registro.txt"

        with open(registro_temp, "w", encoding="utf-8") as arquivo:
            arquivo.write(registro)

        pasta_final.mkdir(parents=True, exist_ok=True)

        destino_final = pasta_final / novo_nome

        if destino_final.exists():
            raise FileExistsError("Já existe uma guia de imposto com esse nome no destino.")

        shutil.move(str(destino_temp), str(destino_final))
        shutil.move(str(registro_temp), str(pasta_final / registro_temp.name))

        shutil.rmtree(pasta_temp)

        registrar_log(
            f"Guia de imposto arquivada: {destino_final.name} | Destino: {pasta_final}"
        )

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        registrar_log(
            f"ERRO ao arquivar guia de imposto: {erro}"
        )

        raise