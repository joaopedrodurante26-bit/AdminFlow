from pathlib import Path
from datetime import datetime
import shutil


PASTA_BASE = Path.home() / "Documents" / "EMPRESA_AGUA_MINERAL"


def normalizar_nome(nome):
    nome = nome.strip().upper()

    substituicoes = {
        "Á": "A", "À": "A", "Â": "A", "Ã": "A",
        "É": "E", "Ê": "E",
        "Í": "I",
        "Ó": "O", "Ô": "O", "Õ": "O",
        "Ú": "U",
        "Ç": "C"
    }

    for original, novo in substituicoes.items():
        nome = nome.replace(original, novo)

    nome = nome.replace(" ", "_")

    return nome


def criar_pasta_funcionario(dados, documentos):
    nome_funcionario = normalizar_nome(dados["Nome completo"])
    data_cadastro = datetime.now().strftime("%Y-%m-%d")

    pasta_funcionario = (
        PASTA_BASE
        / "03_RH"
        / "Funcionarios_Ativos"
        / f"{data_cadastro}_{nome_funcionario}"
    )

    if pasta_funcionario.exists():
        raise FileExistsError("Pasta do funcionário já existe.")

    subpastas = [
        "01_Documentos_Pessoais",
        "02_Contrato",
        "03_Exames",
        "04_Ponto",
        "05_Ferias",
        "06_Advertencias"
    ]

    pasta_funcionario.mkdir(parents=True)

    for subpasta in subpastas:
        (pasta_funcionario / subpasta).mkdir()

    caminho_cadastro = pasta_funcionario / "cadastro_funcionario.txt"

    with open(caminho_cadastro, "w", encoding="utf-8") as arquivo:
        arquivo.write("CADASTRO DE FUNCIONÁRIO\n")
        arquivo.write("=" * 40 + "\n\n")

        for campo, valor in dados.items():
            arquivo.write(f"{campo}: {valor}\n")

        arquivo.write(f"\nData de criação do cadastro: {data_cadastro}\n")

    pasta_documentos = pasta_funcionario / "01_Documentos_Pessoais"

    for documento in documentos:
        origem = Path(documento)
        destino = pasta_documentos / origem.name

        shutil.copy2(origem, destino)