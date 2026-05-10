import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from app.servicos.qualidade.qualidade_arquivos import (
    arquivar_analise_agua,
    registrar_controle_lote
)

from app.servicos.qualidade.qualidade_validacao import (
    validar_dados_analise_agua,
    validar_dados_controle_lote
)


def abrir_arquivar_analise_agua(root):
    janela = tk.Toplevel(root)
    janela.title("Arquivar Análise da Água")
    janela.geometry("800x680")
    janela.minsize(740, 600)

    campos = {}
    arquivo_analise = {"caminho": ""}

    TIPOS_ANALISE = [
        "Microbiológica",
        "Físico-química",
        "Mineral",
        "Controle interno",
        "Laboratorial externa",
        "Potabilidade",
        "Outros"
    ]

    RESULTADOS = [
        "Conforme",
        "Não conforme",
        "Em análise",
        "Inconclusivo"
    ]

    def existe_progresso():
        for campo in campos.values():
            if campo.get().strip():
                return True
        return bool(arquivo_analise["caminho"])

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
        text="Arquivar Análise da Água",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    frame_form = tk.Frame(janela)
    frame_form.pack(pady=10)

    campos_texto = [
        "Data da análise",
        "Ponto de coleta",
        "Lote",
        "Laboratório",
        "Responsável técnico",
        "Descrição",
        "Responsável pelo arquivamento",
        "Observações"
    ]

    for i, label in enumerate(campos_texto):
        tk.Label(frame_form, text=label + ":").grid(
            row=i,
            column=0,
            sticky="e",
            padx=10,
            pady=5
        )

        entrada = tk.Entry(frame_form, width=52)
        entrada.grid(row=i, column=1, padx=10, pady=5)
        campos[label] = entrada

    linha = len(campos_texto)

    tk.Label(frame_form, text="Tipo de análise:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=5
    )

    tipo_analise = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, tipo_analise, *TIPOS_ANALISE).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=5
    )
    campos["Tipo de análise"] = tipo_analise

    linha += 1

    tk.Label(frame_form, text="Resultado:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=5
    )

    resultado = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, resultado, *RESULTADOS).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=5
    )
    campos["Resultado"] = resultado

    def aplicar_mascara_data(evento):
        texto = campos["Data da análise"].get()
        numeros = "".join(c for c in texto if c.isdigit())[:8]

        formatado = ""

        if len(numeros) >= 1:
            formatado += numeros[:2]

        if len(numeros) >= 3:
            formatado += "/" + numeros[2:4]

        if len(numeros) >= 5:
            formatado += "/" + numeros[4:8]

        campos["Data da análise"].delete(0, tk.END)
        campos["Data da análise"].insert(0, formatado)

    campos["Data da análise"].bind("<KeyRelease>", aplicar_mascara_data)

    frame_arquivo = tk.Frame(janela)
    frame_arquivo.pack(pady=12)

    label_arquivo = tk.Label(
        frame_arquivo,
        text="Nenhum laudo/análise selecionado.",
        width=90,
        anchor="w"
    )
    label_arquivo.pack(pady=5)

    def selecionar_arquivo():
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo da análise da água",
            filetypes=[
                ("PDF e imagens", "*.pdf *.png *.jpg *.jpeg"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if arquivo:
            arquivo_analise["caminho"] = arquivo
            label_arquivo.config(text=f"Selecionado: {Path(arquivo).name}")

    def remover_arquivo():
        arquivo_analise["caminho"] = ""
        label_arquivo.config(text="Nenhum laudo/análise selecionado.")

    def coletar_dados():
        dados = {}

        for nome_campo, campo in campos.items():
            dados[nome_campo] = campo.get().strip()

        return dados

    def exibir_resumo_confirmacao(dados):
        janela_resumo = tk.Toplevel(janela)
        janela_resumo.title("Confirmar Análise da Água")
        janela_resumo.geometry("720x520")
        janela_resumo.minsize(660, 470)

        tk.Label(
            janela_resumo,
            text="Resumo da Análise da Água",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        caixa_texto = tk.Text(
            janela_resumo,
            width=84,
            height=19,
            wrap="word"
        )
        caixa_texto.pack(padx=15, pady=10)

        caixa_texto.insert(tk.END, "DADOS DA ANÁLISE\n")
        caixa_texto.insert(tk.END, "=" * 45 + "\n\n")

        for campo, valor in dados.items():
            caixa_texto.insert(tk.END, f"{campo}: {valor}\n")

        caixa_texto.insert(tk.END, "\nARQUIVO SELECIONADO\n")
        caixa_texto.insert(tk.END, "=" * 45 + "\n\n")
        caixa_texto.insert(tk.END, Path(arquivo_analise["caminho"]).name)

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
            arquivar_analise_agua(dados, arquivo_analise["caminho"])

            messagebox.showinfo(
                "Arquivamento concluído",
                "Análise da água arquivada com sucesso."
            )

            janela.destroy()

        except Exception as erro:
            messagebox.showerror(
                "Erro inesperado",
                f"Ocorreu um erro ao arquivar a análise da água:\n\n{erro}"
            )

    def finalizar():
        dados = coletar_dados()

        valido, mensagem = validar_dados_analise_agua(
            dados,
            arquivo_analise["caminho"]
        )

        if not valido:
            messagebox.showerror("Erro de validação", mensagem)
            return

        exibir_resumo_confirmacao(dados)

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=15)

    tk.Button(
        frame_botoes,
        text="Selecionar análise",
        width=22,
        command=selecionar_arquivo
    ).grid(row=0, column=0, padx=8)

    tk.Button(
        frame_botoes,
        text="Remover análise",
        width=22,
        command=remover_arquivo
    ).grid(row=0, column=1, padx=8)

    tk.Button(
        janela,
        text="Finalizar arquivamento",
        width=25,
        height=2,
        command=finalizar
    ).pack(pady=20)

def abrir_registrar_controle_lote(root):
    janela = tk.Toplevel(root)
    janela.title("Registrar Controle de Lote")
    janela.geometry("800x700")
    janela.minsize(740, 620)

    campos = {}
    documento_anexado = {"caminho": ""}

    PRODUTOS = [
        "Galão 20L",
        "Garrafa 500ml",
        "Garrafa 1,5L",
        "Copo 200ml",
        "Outro"
    ]

    STATUS_LOTE = [
        "Liberado",
        "Em análise",
        "Retido",
        "Reprovado",
        "Cancelado"
    ]

    def existe_progresso():
        for campo in campos.values():
            if campo.get().strip():
                return True

        return bool(documento_anexado["caminho"])

    def ao_fechar_janela():
        if not existe_progresso():
            janela.destroy()
            return

        resposta = messagebox.askyesno(
            "Cancelar registro",
            "Há informações preenchidas ou documento anexado.\n\n"
            "Deseja realmente cancelar?"
        )

        if resposta:
            janela.destroy()

    janela.protocol("WM_DELETE_WINDOW", ao_fechar_janela)

    tk.Label(
        janela,
        text="Registrar Controle de Lote",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    frame_form = tk.Frame(janela)
    frame_form.pack(pady=10)

    campos_texto = [
        "Número do lote",
        "Data de envase",
        "Data de validade",
        "Quantidade produzida",
        "Linha de produção",
        "Responsável pela produção",
        "Responsável pela qualidade",
        "Observações"
    ]

    for i, label in enumerate(campos_texto):
        tk.Label(frame_form, text=label + ":").grid(
            row=i,
            column=0,
            sticky="e",
            padx=10,
            pady=5
        )

        entrada = tk.Entry(frame_form, width=52)
        entrada.grid(row=i, column=1, padx=10, pady=5)
        campos[label] = entrada

    linha = len(campos_texto)

    tk.Label(frame_form, text="Produto:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=5
    )

    produto = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, produto, *PRODUTOS).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=5
    )
    campos["Produto"] = produto

    linha += 1

    tk.Label(frame_form, text="Status do lote:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=5
    )

    status_lote = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, status_lote, *STATUS_LOTE).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=5
    )
    campos["Status do lote"] = status_lote

    def aplicar_mascara_data(campo_nome):
        texto = campos[campo_nome].get()
        numeros = "".join(c for c in texto if c.isdigit())[:8]

        formatado = ""

        if len(numeros) >= 1:
            formatado += numeros[:2]

        if len(numeros) >= 3:
            formatado += "/" + numeros[2:4]

        if len(numeros) >= 5:
            formatado += "/" + numeros[4:8]

        campos[campo_nome].delete(0, tk.END)
        campos[campo_nome].insert(0, formatado)

    campos["Data de envase"].bind(
        "<KeyRelease>",
        lambda evento: aplicar_mascara_data("Data de envase")
    )

    campos["Data de validade"].bind(
        "<KeyRelease>",
        lambda evento: aplicar_mascara_data("Data de validade")
    )

    frame_arquivo = tk.Frame(janela)
    frame_arquivo.pack(pady=12)

    label_arquivo = tk.Label(
        frame_arquivo,
        text="Nenhum documento anexado.",
        width=90,
        anchor="w"
    )
    label_arquivo.pack(pady=5)

    def selecionar_documento():
        arquivo = filedialog.askopenfilename(
            title="Selecione documento do lote",
            filetypes=[
                ("PDF e imagens", "*.pdf *.png *.jpg *.jpeg"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if arquivo:
            documento_anexado["caminho"] = arquivo
            label_arquivo.config(text=f"Anexado: {Path(arquivo).name}")

    def remover_documento():
        documento_anexado["caminho"] = ""
        label_arquivo.config(text="Nenhum documento anexado.")

    def coletar_dados():
        dados = {}

        for nome_campo, campo in campos.items():
            dados[nome_campo] = campo.get().strip()

        return dados

    def exibir_resumo_confirmacao(dados):
        janela_resumo = tk.Toplevel(janela)
        janela_resumo.title("Confirmar Controle de Lote")
        janela_resumo.geometry("720x520")
        janela_resumo.minsize(660, 470)

        tk.Label(
            janela_resumo,
            text="Resumo do Controle de Lote",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        caixa_texto = tk.Text(
            janela_resumo,
            width=84,
            height=19,
            wrap="word"
        )
        caixa_texto.pack(padx=15, pady=10)

        caixa_texto.insert(tk.END, "DADOS DO LOTE\n")
        caixa_texto.insert(tk.END, "=" * 45 + "\n\n")

        for campo, valor in dados.items():
            caixa_texto.insert(tk.END, f"{campo}: {valor}\n")

        caixa_texto.insert(tk.END, "\nDOCUMENTO ANEXADO\n")
        caixa_texto.insert(tk.END, "=" * 45 + "\n\n")

        if documento_anexado["caminho"]:
            caixa_texto.insert(tk.END, Path(documento_anexado["caminho"]).name)
        else:
            caixa_texto.insert(tk.END, "Nenhum documento anexado.")

        caixa_texto.config(state="disabled")

        def confirmar():
            janela_resumo.destroy()
            executar_registro(dados)

        frame_botoes = tk.Frame(janela_resumo)
        frame_botoes.pack(pady=10)

        tk.Button(
            frame_botoes,
            text="Confirmar e registrar",
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

    def executar_registro(dados):
        try:
            registrar_controle_lote(dados, documento_anexado["caminho"])

            messagebox.showinfo(
                "Registro concluído",
                "Controle de lote registrado com sucesso."
            )

            janela.destroy()

        except Exception as erro:
            messagebox.showerror(
                "Erro inesperado",
                f"Ocorreu um erro ao registrar o controle de lote:\n\n{erro}"
            )

    def finalizar():
        dados = coletar_dados()

        valido, mensagem = validar_dados_controle_lote(
            dados,
            documento_anexado["caminho"]
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
            "Deseja apagar os dados preenchidos e remover o documento anexado?"
        )

        if not resposta:
            return

        for campo in campos.values():
            if hasattr(campo, "delete"):
                campo.delete(0, tk.END)
            else:
                campo.set("Selecione")

        remover_documento()

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=15)

    tk.Button(
        frame_botoes,
        text="Anexar documento",
        width=22,
        command=selecionar_documento
    ).grid(row=0, column=0, padx=8)

    tk.Button(
        frame_botoes,
        text="Remover documento",
        width=22,
        command=remover_documento
    ).grid(row=0, column=1, padx=8)

    tk.Button(
        frame_botoes,
        text="Limpar formulário",
        width=22,
        command=limpar_formulario
    ).grid(row=0, column=2, padx=8)

    tk.Button(
        janela,
        text="Finalizar registro",
        width=25,
        height=2,
        command=finalizar
    ).pack(pady=20)