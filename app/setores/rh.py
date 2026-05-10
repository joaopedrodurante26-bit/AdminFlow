import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from app.servicos.rh.rh_arquivos import criar_pasta_funcionario, arquivar_folha_ponto
from app.servicos.rh.rh_validacao import validar_dados_funcionario, validar_dados_folha_ponto


TIPOS_DOCUMENTO = {
    "Documento pessoal": "01_Documentos_Pessoais",
    "Contrato": "02_Contrato",
    "Exame / ASO": "03_Exames",
    "Ponto": "04_Ponto",
    "Férias": "05_Ferias",
    "Advertência": "06_Advertencias",
}


def abrir_cadastro_funcionario(root):
    janela = tk.Toplevel(root)
    janela.title("Cadastrar Funcionário")
    janela.geometry("750x650")
    janela.minsize(700, 550)
    
    def aplicar_mascara_cpf(evento):
        texto = campos["CPF"].get()

        numeros = "".join(c for c in texto if c.isdigit())

        numeros = numeros[:11]

        formatado = ""

        if len(numeros) >= 1:
            formatado += numeros[:3]

        if len(numeros) >= 4:
            formatado += "." + numeros[3:6]

        if len(numeros) >= 7:
            formatado += "." + numeros[6:9]

        if len(numeros) >= 10:
            formatado += "-" + numeros[9:11]

        campos["CPF"].delete(0, tk.END)
        campos["CPF"].insert(0, formatado)

    def aplicar_mascara_data(evento):
        texto = campos["Data de admissão"].get()

        numeros = "".join(c for c in texto if c.isdigit())

        numeros = numeros[:8]

        formatado = ""

        if len(numeros) >= 1:
            formatado += numeros[:2]

        if len(numeros) >= 3:
            formatado += "/" + numeros[2:4]

        if len(numeros) >= 5:
            formatado += "/" + numeros[4:8]

        campos["Data de admissão"].delete(0, tk.END)
        campos["Data de admissão"].insert(0, formatado)

    def existe_progresso():
        for entrada in campos.values():
            if entrada.get().strip():
                return True

        if documentos_selecionados:
            return True

        return False

    def ao_fechar_janela():
        if not existe_progresso():
            janela.destroy()
            return

        resposta = messagebox.askyesno(
            "Cancelar cadastro",
            "Há informações preenchidas ou documentos anexados.\n\n"
            "Se você fechar esta janela, o cadastro será cancelado.\n\n"
            "Deseja realmente sair?"
        )

        if resposta:
            janela.destroy()
    
    janela.protocol("WM_DELETE_WINDOW", ao_fechar_janela)

    documentos_selecionados = []
    campos = {}

    titulo = tk.Label(
        janela,
        text="Cadastro de Funcionário",
        font=("Arial", 18, "bold")
    )
    titulo.pack(pady=15)

    frame_form = tk.Frame(janela)
    frame_form.pack(pady=10)

    labels = [
        "Nome completo",
        "CPF",
        "Cargo",
        "Setor",
        "Data de admissão",
        "Jornada de trabalho"
    ]

    for i, label in enumerate(labels):
        tk.Label(frame_form, text=label + ":").grid(
            row=i,
            column=0,
            sticky="e",
            padx=10,
            pady=6
        )

    if label == "Setor":
        valor_setor = tk.StringVar(value="Selecione")

        entrada = tk.OptionMenu(
            frame_form,
            valor_setor,
            "Produção",
            "Logística",
            "Administrativo",
            "Financeiro",
            "Fiscal",
            "Qualidade",
            "Comercial",
            "RH"
        )
        entrada.grid(row=i, column=1, sticky="w", padx=10, pady=6)

        campos[label] = valor_setor

    elif label == "Jornada de trabalho":
        valor_jornada = tk.StringVar(value="Selecione")

        entrada = tk.OptionMenu(
            frame_form,
            valor_jornada,
            "07:00 às 17:00",
            "08:00 às 17:00",
            "08:00 às 18:00",
            "12x36",
            "Turno da manhã",
            "Turno da tarde",
            "Turno da noite"
        )
        entrada.grid(row=i, column=1, sticky="w", padx=10, pady=6)

        campos[label] = valor_jornada

    else:
        entrada = tk.Entry(frame_form, width=45)
        entrada.grid(row=i, column=1, padx=10, pady=6)

        if label == "CPF":
            entrada.bind("<KeyRelease>", aplicar_mascara_cpf)

        if label == "Data de admissão":
            entrada.bind("<KeyRelease>", aplicar_mascara_data)

        campos[label] = entrada

    frame_docs = tk.Frame(janela)
    frame_docs.pack(pady=15)

    tk.Label(
        frame_docs,
        text="Documentos anexados:",
        font=("Arial", 11, "bold")
    ).pack(anchor="w")

    lista_docs = tk.Listbox(frame_docs, width=90, height=8)
    lista_docs.pack(pady=5)

    tipo_documento = tk.StringVar(value="Documento pessoal")

    frame_tipo = tk.Frame(janela)
    frame_tipo.pack(pady=5)

    tk.Label(frame_tipo, text="Tipo do próximo documento:").grid(
        row=0,
        column=0,
        padx=5
    )

    menu_tipo = tk.OptionMenu(
        frame_tipo,
        tipo_documento,
        *TIPOS_DOCUMENTO.keys()
    )
    menu_tipo.grid(row=0, column=1, padx=5)

    def atualizar_lista_documentos():
        lista_docs.delete(0, tk.END)

        for item in documentos_selecionados:
            nome_arquivo = Path(item["caminho"]).name
            tipo = item["tipo"]
            lista_docs.insert(tk.END, f"{tipo} | {nome_arquivo}")

    def selecionar_documentos():
        arquivos = filedialog.askopenfilenames(
            title="Selecione os documentos do funcionário",
            filetypes=[
                ("Arquivos PDF", "*.pdf"),
                ("Imagens", "*.png *.jpg *.jpeg"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not arquivos:
            return

        tipo = tipo_documento.get()
        destino = TIPOS_DOCUMENTO[tipo]

        for arquivo in arquivos:
            ja_existe = any(item["caminho"] == arquivo for item in documentos_selecionados)

            if not ja_existe:
                documentos_selecionados.append({
                    "caminho": arquivo,
                    "tipo": tipo,
                    "destino": destino
                })

        atualizar_lista_documentos()

    def remover_documento():
        indice = lista_docs.curselection()

        if not indice:
            messagebox.showwarning(
                "Nenhum documento selecionado",
                "Selecione um documento da lista para remover."
            )
            return

        documentos_selecionados.pop(indice[0])
        atualizar_lista_documentos()

    def validar_campos():
        dados = {}

        for nome_campo, campo in campos.items():
            dados[nome_campo] = campo.get().strip()

        caminhos_documentos = [
            item["caminho"] for item in documentos_selecionados
        ]

        valido, mensagem = validar_dados_funcionario(dados, caminhos_documentos)

        if not valido:
            messagebox.showerror("Erro de validação", mensagem)
            return None

        return dados

    def executar_cadastro(dados):
        try:
            criar_pasta_funcionario(dados, documentos_selecionados)

            messagebox.showinfo(
                "Cadastro concluído",
                "Funcionário cadastrado com sucesso."
            )

            janela.destroy()

        except FileExistsError:
            messagebox.showerror(
                "Funcionário já cadastrado",
                "Já existe uma pasta para este funcionário."
            )

        except Exception as erro:
            messagebox.showerror(
                "Erro inesperado",
                f"Ocorreu um erro ao cadastrar o funcionário:\n\n{erro}"
            )

    def exibir_resumo_confirmacao(dados):
        janela_resumo = tk.Toplevel(janela)
        janela_resumo.title("Confirmar Cadastro")
        janela_resumo.geometry("650x500")
        janela_resumo.minsize(600, 450)

        titulo = tk.Label(
            janela_resumo,
            text="Resumo do Cadastro",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=15)

        caixa_texto = tk.Text(
            janela_resumo,
            width=75,
            height=20,
            wrap="word"
        )
        caixa_texto.pack(padx=15, pady=10)

        caixa_texto.insert(tk.END, "DADOS DO FUNCIONÁRIO\n")
        caixa_texto.insert(tk.END, "=" * 40 + "\n\n")

        for campo, valor in dados.items():
            caixa_texto.insert(tk.END, f"{campo}: {valor}\n")

        caixa_texto.insert(tk.END, "\nDOCUMENTOS ANEXADOS\n")
        caixa_texto.insert(tk.END, "=" * 40 + "\n\n")

        for documento in documentos_selecionados:
            nome_arquivo = Path(documento["caminho"]).name
            tipo = documento["tipo"]
            destino = documento["destino"]

            caixa_texto.insert(
                tk.END,
                f"- {tipo}: {nome_arquivo} → {destino}\n"
            )

        caixa_texto.config(state="disabled")

        def confirmar():
            janela_resumo.destroy()
            executar_cadastro(dados)

        def cancelar():
            janela_resumo.destroy()

        frame_botoes = tk.Frame(janela_resumo)
        frame_botoes.pack(pady=10)

        botao_confirmar = tk.Button(
            frame_botoes,
            text="Confirmar e cadastrar",
            width=25,
            height=2,
            command=confirmar
        )
        botao_confirmar.grid(row=0, column=0, padx=10)

        botao_cancelar = tk.Button(
            frame_botoes,
            text="Voltar e corrigir",
            width=25,
            height=2,
            command=cancelar
        )
        botao_cancelar.grid(row=0, column=1, padx=10)

    def finalizar_cadastro():
        dados = validar_campos()

        if dados is None:
            return

        exibir_resumo_confirmacao(dados)

    def limpar_formulario():
        if not existe_progresso():
            return

        resposta = messagebox.askyesno(
            "Limpar formulário",
            "Deseja apagar todos os dados preenchidos e remover os documentos anexados?"
        )

        if not resposta:
            return

        for entrada in campos.values():
            entrada.delete(0, tk.END)

        documentos_selecionados.clear()
        atualizar_lista_documentos()

    frame_botoes_docs = tk.Frame(janela)
    frame_botoes_docs.pack(pady=10)

    botao_docs = tk.Button(
        frame_botoes_docs,
        text="Selecionar documentos",
        width=25,
        command=selecionar_documentos
    )
    botao_docs.grid(row=0, column=0, padx=10)

    botao_remover = tk.Button(
        frame_botoes_docs,
        text="Remover documento",
        width=25,
        command=remover_documento
    )
    botao_remover.grid(row=0, column=1, padx=10)

    botao_limpar = tk.Button(
        frame_botoes_docs,
        text="Limpar formulário",
        width=25,
        command=limpar_formulario
    )
    botao_limpar.grid(row=0, column=2, padx=10)

    botao_finalizar = tk.Button(
        janela,
        text="Finalizar cadastro",
        width=25,
        height=2,
        command=finalizar_cadastro
    )
    botao_finalizar.pack(pady=20)

def abrir_arquivar_folha_ponto(root):
    janela = tk.Toplevel(root)
    janela.title("Arquivar Folha de Ponto")
    janela.geometry("740x560")
    janela.minsize(680, 520)

    campos = {}
    arquivo_ponto = {"caminho": ""}

    SETORES = [
        "Produção",
        "Logística",
        "Administrativo",
        "Financeiro",
        "Fiscal",
        "Qualidade",
        "Comercial",
        "RH"
    ]

    TIPOS_PONTO = [
        "Individual",
        "Setorial",
        "Geral"
    ]

    def existe_progresso():
        for campo in campos.values():
            if campo.get().strip():
                return True

        return bool(arquivo_ponto["caminho"])

    def ao_fechar_janela():
        if not existe_progresso():
            janela.destroy()
            return

        resposta = messagebox.askyesno(
            "Cancelar arquivamento",
            "Há informações preenchidas ou arquivo anexado.\n\n"
            "Deseja realmente cancelar?"
        )

        if resposta:
            janela.destroy()

    janela.protocol("WM_DELETE_WINDOW", ao_fechar_janela)

    tk.Label(
        janela,
        text="Arquivar Folha de Ponto",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    frame_form = tk.Frame(janela)
    frame_form.pack(pady=10)

    campos_texto = [
        "Competência",
        "Nome do funcionário",
        "Responsável pelo arquivamento",
        "Observações"
    ]

    for i, label in enumerate(campos_texto):
        tk.Label(frame_form, text=label + ":").grid(
            row=i,
            column=0,
            sticky="e",
            padx=10,
            pady=6
        )

        entrada = tk.Entry(frame_form, width=45)
        entrada.grid(row=i, column=1, padx=10, pady=6)
        campos[label] = entrada

    linha = len(campos_texto)

    tk.Label(frame_form, text="Setor:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    setor = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, setor, *SETORES).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=6
    )
    campos["Setor"] = setor

    linha += 1

    tk.Label(frame_form, text="Tipo de folha:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    tipo_ponto = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, tipo_ponto, *TIPOS_PONTO).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=6
    )
    campos["Tipo de folha"] = tipo_ponto

    frame_arquivo = tk.Frame(janela)
    frame_arquivo.pack(pady=15)

    label_arquivo = tk.Label(
        frame_arquivo,
        text="Nenhuma folha de ponto selecionada.",
        width=80,
        anchor="w"
    )
    label_arquivo.pack(pady=5)

    def aplicar_mascara_competencia(evento):
        texto = campos["Competência"].get()
        numeros = "".join(c for c in texto if c.isdigit())[:6]

        formatado = ""

        if len(numeros) >= 1:
            formatado += numeros[:2]

        if len(numeros) >= 3:
            formatado += "/" + numeros[2:6]

        campos["Competência"].delete(0, tk.END)
        campos["Competência"].insert(0, formatado)

    campos["Competência"].bind("<KeyRelease>", aplicar_mascara_competencia)

    def selecionar_arquivo():
        arquivo = filedialog.askopenfilename(
            title="Selecione a folha de ponto",
            filetypes=[
                ("PDF e imagens", "*.pdf *.png *.jpg *.jpeg"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if arquivo:
            arquivo_ponto["caminho"] = arquivo
            label_arquivo.config(text=f"Selecionado: {Path(arquivo).name}")

    def remover_arquivo():
        arquivo_ponto["caminho"] = ""
        label_arquivo.config(text="Nenhuma folha de ponto selecionada.")

    def coletar_dados():
        dados = {}

        for nome_campo, campo in campos.items():
            dados[nome_campo] = campo.get().strip()

        return dados

    def exibir_resumo_confirmacao(dados):
        janela_resumo = tk.Toplevel(janela)
        janela_resumo.title("Confirmar Arquivamento")
        janela_resumo.geometry("650x450")
        janela_resumo.minsize(600, 400)

        tk.Label(
            janela_resumo,
            text="Resumo do Arquivamento",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        caixa_texto = tk.Text(
            janela_resumo,
            width=75,
            height=16,
            wrap="word"
        )
        caixa_texto.pack(padx=15, pady=10)

        caixa_texto.insert(tk.END, "DADOS DA FOLHA DE PONTO\n")
        caixa_texto.insert(tk.END, "=" * 45 + "\n\n")

        for campo, valor in dados.items():
            caixa_texto.insert(tk.END, f"{campo}: {valor}\n")

        caixa_texto.insert(tk.END, "\nARQUIVO SELECIONADO\n")
        caixa_texto.insert(tk.END, "=" * 45 + "\n\n")
        caixa_texto.insert(tk.END, Path(arquivo_ponto["caminho"]).name)

        caixa_texto.config(state="disabled")

        def confirmar():
            janela_resumo.destroy()
            executar_arquivamento(dados)

        frame_botoes = tk.Frame(janela_resumo)
        frame_botoes.pack(pady=10)

        tk.Button(
            frame_botoes,
            text="Confirmar e arquivar",
            width=25,
            height=2,
            command=confirmar
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            frame_botoes,
            text="Voltar e corrigir",
            width=25,
            height=2,
            command=janela_resumo.destroy
        ).grid(row=0, column=1, padx=10)

    def executar_arquivamento(dados):
        try:
            arquivar_folha_ponto(dados, arquivo_ponto["caminho"])

            messagebox.showinfo(
                "Arquivamento concluído",
                "Folha de ponto arquivada com sucesso."
            )

            janela.destroy()

        except Exception as erro:
            messagebox.showerror(
                "Erro inesperado",
                f"Ocorreu um erro ao arquivar a folha de ponto:\n\n{erro}"
            )

    def finalizar():
        dados = coletar_dados()

        valido, mensagem = validar_dados_folha_ponto(
            dados,
            arquivo_ponto["caminho"]
        )

        if not valido:
            messagebox.showerror("Erro de validação", mensagem)
            return

        exibir_resumo_confirmacao(dados)

    def limpar_formulario():
        if not existe_progresso():
            return

        resposta = messagebox.askyesno(
            "Limpar formulário",
            "Deseja apagar os dados preenchidos e remover o arquivo anexado?"
        )

        if not resposta:
            return

        for campo in campos.values():
            if hasattr(campo, "delete"):
                campo.delete(0, tk.END)
            else:
                campo.set("Selecione")

        remover_arquivo()

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=15)

    tk.Button(
        frame_botoes,
        text="Selecionar folha",
        width=22,
        command=selecionar_arquivo
    ).grid(row=0, column=0, padx=8)

    tk.Button(
        frame_botoes,
        text="Remover folha",
        width=22,
        command=remover_arquivo
    ).grid(row=0, column=1, padx=8)

    tk.Button(
        frame_botoes,
        text="Limpar formulário",
        width=22,
        command=limpar_formulario
    ).grid(row=0, column=2, padx=8)

    tk.Button(
        janela,
        text="Finalizar arquivamento",
        width=25,
        height=2,
        command=finalizar
    ).pack(pady=20)