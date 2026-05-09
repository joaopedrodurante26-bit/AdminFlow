from pathlib import Path
from datetime import datetime
import shutil

from AdminFlow.app.servicos.configuracoes.configuracoes import obter_pasta_base
from AdminFlow.app.servicos.rh.rh_arquivos import normalizar_nome
from app.servicos.logs import registrar_log


CATEGORIAS_DESTINO = {
    "Contas a pagar": "Contas_a_Pagar",
    "Contas a receber": "Contas_a_Receber",
    "Comprovantes gerais": "Comprovantes"
}


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

    ano = str(data_obj.year)
    mes = meses[data_obj.month - 1]

    return ano, mes


def gerar_nome_comprovante(dados, caminho_origem):
    data_iso = converter_data_para_iso(dados["Data do comprovante"])
    tipo = normalizar_nome(dados["Tipo de comprovante"])
    pessoa = normalizar_nome(dados["Favorecido/Pagador"])
    descricao = normalizar_nome(dados["Descrição"])
    extensao = caminho_origem.suffix.lower()

    return f"{data_iso}_{tipo}_{pessoa}_{descricao}{extensao}"


def gerar_resumo_comprovante(dados, destino_arquivo):
    conteudo = []

    conteudo.append("REGISTRO DE COMPROVANTE FINANCEIRO")
    conteudo.append("=" * 45)
    conteudo.append("")

    for campo, valor in dados.items():
        conteudo.append(f"{campo}: {valor}")

    conteudo.append("")
    conteudo.append(f"Arquivo arquivado: {destino_arquivo.name}")
    conteudo.append(f"Data do arquivamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    return "\n".join(conteudo)


def arquivar_comprovante(dados, caminho_comprovante):
    pasta_base = obter_pasta_base()

    origem = Path(caminho_comprovante)

    if not origem.exists():
        raise FileNotFoundError("Comprovante não encontrado.")

    categoria = dados["Categoria"]
    pasta_categoria = CATEGORIAS_DESTINO[categoria]

    ano, mes = obter_ano_mes(dados["Data do comprovante"])

    pasta_final = (
        pasta_base
        / "02_FINANCEIRO"
        / pasta_categoria
        / ano
        / mes
    )

    pasta_temp = (
        pasta_base
        / "99_TEMPORARIO"
        / f"TEMP_COMPROVANTE_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        pasta_temp.mkdir(parents=True, exist_ok=False)

        novo_nome = gerar_nome_comprovante(dados, origem)
        destino_temp = pasta_temp / novo_nome

        shutil.copy2(origem, destino_temp)

        resumo = gerar_resumo_comprovante(dados, destino_temp)

        caminho_resumo = pasta_temp / f"{destino_temp.stem}_registro.txt"

        with open(caminho_resumo, "w", encoding="utf-8") as arquivo:
            arquivo.write(resumo)

        pasta_final.mkdir(parents=True, exist_ok=True)

        destino_final = pasta_final / novo_nome
        resumo_final = pasta_final / caminho_resumo.name

        if destino_final.exists():
            raise FileExistsError("Já existe um comprovante com o mesmo nome no destino.")

        shutil.move(str(destino_temp), str(destino_final))
        shutil.move(str(caminho_resumo), str(resumo_final))

        shutil.rmtree(pasta_temp)

        registrar_log(
            f"Comprovante financeiro arquivado: {destino_final.name} | Destino: {pasta_final}"
        )

    except Exception as erro:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        registrar_log(
            f"ERRO ao arquivar comprovante financeiro: {erro}"
        )

        raise