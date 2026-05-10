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