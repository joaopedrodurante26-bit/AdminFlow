from pathlib import Path
from datetime import datetime
import shutil

from app.servicos.logs import registrar_log
from app.servicos.configuracoes.configuracoes import obter_pasta_base
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

def obter_estrutura_padrao():
    return {
        "01_ADMINISTRATIVO": [
            "Comunicados",
            "Memorandos",
            "Planejamentos"
        ],
        "02_FINANCEIRO": [
            "Contas_a_Pagar",
            "Contas_a_Receber",
            "Extratos",
            "Comprovantes",
            "Fluxo_de_Caixa"
        ],
        "03_RH": [
            "Funcionarios_Ativos",
            "Funcionarios_Desligados",
            "Folha_Pagamento",
            "Controle_Ponto",
            "Treinamentos"
        ],
        "04_FISCAL_CONTABIL": [
            "NF_Emitidas",
            "NF_Recebidas",
            "Impostos",
            "SPED",
            "Declaracoes"
        ],
        "05_COMERCIAL": [
            "Clientes",
            "Propostas",
            "Pedidos",
            "Relatorios_Vendas"
        ],
        "06_LOGISTICA": [
            "Entregas",
            "Romaneios",
            "Frota",
            "Rotas"
        ],
        "07_QUALIDADE": [
            "Analises_Agua",
            "Controle_Lotes",
            "Auditorias",
            "Inspecoes",
            "Licencas"
        ],
        "08_CONTRATOS": [
            "Clientes",
            "Fornecedores",
            "Prestadores"
        ],
        "09_RELATORIOS": [
            "Administrativos",
            "Financeiros",
            "Operacionais"
        ],
        "10_MODELOS": [
            "RH",
            "Financeiro",
            "Fiscal",
            "Qualidade"
        ],
        "11_DIGITALIZADOS": [
            "Pendentes",
            "Arquivados"
        ],
        "12_BACKUP_LOCAL": [],
        "99_TEMPORARIO": []
    }

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