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

def gerar_nome_analise_agua(dados, caminho_origem):
    data_iso = converter_data_para_iso(dados["Data da análise"])
    tipo = normalizar_nome(dados["Tipo de análise"])
    ponto = normalizar_nome(dados["Ponto de coleta"])
    resultado = normalizar_nome(dados["Resultado"])
    lote = normalizar_nome(dados.get("Lote", "SEM_LOTE") or "SEM_LOTE")
    extensao = caminho_origem.suffix.lower()

    return f"{data_iso}_ANALISE_AGUA_{tipo}_{ponto}_{lote}_{resultado}{extensao}"

def gerar_registro_analise_agua(dados, nome_arquivo):
    linhas = []

    linhas.append("REGISTRO DE ANÁLISE DA ÁGUA")
    linhas.append("=" * 45)
    linhas.append("")

    for campo, valor in dados.items():
        linhas.append(f"{campo}: {valor}")

    linhas.append("")
    linhas.append(f"Arquivo arquivado: {nome_arquivo}")
    linhas.append(f"Data do arquivamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    return "\n".join(linhas)

def arquivar_analise_agua(dados, caminho_arquivo):
    pasta_base = obter_pasta_base()
    origem = Path(caminho_arquivo)

    if not origem.exists():
        raise FileNotFoundError("Arquivo da análise não encontrado.")

    ano, mes = obter_ano_mes(dados["Data da análise"])

    tipo = normalizar_nome(dados["Tipo de análise"])

    pasta_final = (
        pasta_base
        / "07_QUALIDADE"
        / "Analises_Agua"
        / tipo
        / ano
        / mes
    )

    pasta_temp = (
        pasta_base
        / "99_TEMPORARIO"
        / f"TEMP_ANALISE_AGUA_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        pasta_temp.mkdir(parents=True, exist_ok=False)

        novo_nome = gerar_nome_analise_agua(dados, origem)
        destino_temp = pasta_temp / novo_nome

        shutil.copy2(origem, destino_temp)

        registro = gerar_registro_analise_agua(dados, novo_nome)
        registro_temp = pasta_temp / f"{destino_temp.stem}_registro.txt"

        with open(registro_temp, "w", encoding="utf-8") as arquivo:
            arquivo.write(registro)

        pasta_final.mkdir(parents=True, exist_ok=True)

        destino_final = pasta_final / novo_nome

        if destino_final.exists():
            raise FileExistsError("Já existe uma análise da água com esse nome no destino.")

        shutil.move(str(destino_temp), str(destino_final))
        shutil.move(str(registro_temp), str(pasta_final / registro_temp.name))

        shutil.rmtree(pasta_temp)

        registrar_log(
            f"Análise da água arquivada: {destino_final.name} | Destino: {pasta_final}"
        )

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        registrar_log(
            f"ERRO ao arquivar análise da água: {erro}"
        )

        raise

def gerar_nome_registro_controle_lote(dados):
    data_iso = converter_data_para_iso(dados["Data de envase"])
    lote = normalizar_nome(dados["Número do lote"])
    produto = normalizar_nome(dados["Produto"])
    status = normalizar_nome(dados["Status do lote"])

    return f"{data_iso}_CONTROLE_LOTE_{lote}_{produto}_{status}.txt"

def gerar_nome_anexo_controle_lote(dados, caminho_origem):
    data_iso = converter_data_para_iso(dados["Data de envase"])
    lote = normalizar_nome(dados["Número do lote"])
    produto = normalizar_nome(dados["Produto"])
    extensao = caminho_origem.suffix.lower()

    return f"{data_iso}_ANEXO_CONTROLE_LOTE_{lote}_{produto}{extensao}"

def gerar_registro_controle_lote(dados, nome_anexo=None):
    linhas = []

    linhas.append("REGISTRO DE CONTROLE DE LOTE")
    linhas.append("=" * 45)
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

def registrar_controle_lote(dados, caminho_documento=""):
    pasta_base = obter_pasta_base()

    ano, mes = obter_ano_mes(dados["Data de envase"])
    lote = normalizar_nome(dados["Número do lote"])
    produto = normalizar_nome(dados["Produto"])

    pasta_final = (
        pasta_base
        / "07_QUALIDADE"
        / "Controle_Lotes"
        / ano
        / mes
        / produto
        / lote
    )

    pasta_temp = (
        pasta_base
        / "99_TEMPORARIO"
        / f"TEMP_CONTROLE_LOTE_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{lote}"
    )

    try:
        pasta_temp.mkdir(parents=True, exist_ok=False)

        nome_anexo = None

        if caminho_documento:
            origem = Path(caminho_documento)

            if not origem.exists():
                raise FileNotFoundError("Documento anexado não encontrado.")

            nome_anexo = gerar_nome_anexo_controle_lote(dados, origem)
            destino_anexo_temp = pasta_temp / nome_anexo

            shutil.copy2(origem, destino_anexo_temp)

        nome_registro = gerar_nome_registro_controle_lote(dados)
        registro_temp = pasta_temp / nome_registro

        registro = gerar_registro_controle_lote(dados, nome_anexo)

        with open(registro_temp, "w", encoding="utf-8") as arquivo:
            arquivo.write(registro)

        pasta_final.mkdir(parents=True, exist_ok=True)

        destino_registro_final = pasta_final / nome_registro

        if destino_registro_final.exists():
            raise FileExistsError("Já existe registro de controle para este lote.")

        shutil.move(str(registro_temp), str(destino_registro_final))

        if nome_anexo:
            shutil.move(
                str(pasta_temp / nome_anexo),
                str(pasta_final / nome_anexo)
            )

        shutil.rmtree(pasta_temp)

        registrar_log(
            f"Controle de lote registrado: {nome_registro} | Destino: {pasta_final}"
        )

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        registrar_log(
            f"ERRO ao registrar controle de lote: {erro}"
        )

        raise