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

    return nome.replace(" ", "_")

def gerar_nome_documento(data_cadastro, nome_funcionario, tipo_documento, caminho_origem, contador):
    extensao = caminho_origem.suffix.lower()

    tipo = normalizar_nome(tipo_documento)

    return f"{data_cadastro}_{tipo}_{nome_funcionario}_{contador:02d}{extensao}"

def criar_pasta_funcionario(dados, documentos):
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

        pasta_rh.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pasta_temp), str(pasta_final))

    except Exception:
        if pasta_temp.exists():
            shutil.rmtree(pasta_temp)

        raise