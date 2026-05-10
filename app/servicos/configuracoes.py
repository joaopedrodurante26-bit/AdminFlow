from pathlib import Path
import json


CAMINHO_CONFIG = Path("config.json")


CONFIG_PADRAO = {
    "nome_empresa": "EMPRESA_AGUA_MINERAL",
    "pasta_base": "",
    "versao_config": "1.0"
}


def criar_config_padrao():
    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as arquivo:
        json.dump(CONFIG_PADRAO, arquivo, indent=4, ensure_ascii=False)

def carregar_configuracoes():
    if not CAMINHO_CONFIG.exists():
        criar_config_padrao()

    with open(CAMINHO_CONFIG, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)

def obter_pasta_base():
    config = carregar_configuracoes()

    pasta_base = config.get("pasta_base", "").strip()
    nome_empresa = config.get("nome_empresa", "EMPRESA_AGUA_MINERAL").strip()

    if pasta_base:
        return Path(pasta_base)

    return Path.home() / "Documents" / nome_empresa

def salvar_configuracoes(novas_configuracoes):
    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as arquivo:
        json.dump(novas_configuracoes, arquivo, indent=4, ensure_ascii=False)