import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from AdminFlow.app.servicos.financeiro.financeiro_arquivos import arquivar_comprovante
from AdminFlow.app.servicos.financeiro.financeiro_validacao import validar_dados_comprovante


TIPOS_COMPROVANTE = [
    "Pagamento",
    "Recebimento",
    "Transferência",
    "PIX",
    "Boleto",
    "Depósito",
    "Outros"
]


CATEGORIAS_DESTINO = {
    "Contas a pagar": "Contas_a_Pagar",
    "Contas a receber": "Contas_a_Receber",
    "Comprovantes gerais": "Comprovantes"
}


def abrir_arquivar_comprovante(root):
    janela = tk.Toplevel(root)
    janela.title("Arquivar Comprovante")
    janela.geometry("750x600")
    janela.minsize(700, 550)

    campos = {}
    comprovante_selecionado = {"caminho": ""}

    def existe_progresso():
        for campo in campos.values():
            if campo.get().strip():
                return True

        if comprovante_selecionado["caminho"]:
            return True

        return False

    def ao_fechar_janela():
        if not existe_progresso():
            janela.destroy()
            return

        resposta = messagebox.askyesno(
            "Cancelar arquivamento",
            "Há informações preenchidas ou comprovante anexado.\n\n"
            "Se você fechar esta janela, o processo será cancelado.\n\n"
            "Deseja realmente sair?"
        )

        if resposta:
            janela.destroy()

    janela.protocol("WM_DELETE_WINDOW", ao_fechar_janela)

    titulo = tk.Label(
        janela,
        text="Arquivar Comprovante Financeiro",
        font=("Arial", 18, "bold")
    )
    titulo.pack(pady=15)

    frame_form = tk.Frame(janela)
    frame_form.pack(pady=10)

    labels_texto = [
        "Data do comprovante",
        "Descrição",
        "Favorecido/Pagador",
        "Valor"
    ]

    for i, label in enumerate(labels_texto):
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

    linha = len(labels_texto)

    tk.Label(frame_form, text="Tipo de comprovante:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    tipo_comprovante = tk.StringVar(value="Selecione")
    menu_tipo = tk.OptionMenu(frame_form, tipo_comprovante, *TIPOS_COMPROVANTE)
    menu_tipo.grid(row=linha, column=1, sticky="w", padx=10, pady=6)
    campos["Tipo de comprovante"] = tipo_comprovante

    linha += 1

    tk.Label(frame_form, text="Categoria:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    categoria = tk.StringVar(value="Selecione")
    menu_categoria = tk.OptionMenu(frame_form, categoria, *CATEGORIAS_DESTINO.keys())
    menu_categoria.grid(row=linha, column=1, sticky="w", padx=10, pady=6)
    campos["Categoria"] = categoria

    frame_arquivo = tk.Frame(janela)
    frame_arquivo.pack(pady=15)

    label_arquivo = tk.Label(
        frame_arquivo,
        text="Nenhum comprovante selecionado.",
        width=80,
        anchor="w"
    )
    label_arquivo.pack(pady=5)

    def selecionar_comprovante():
        arquivo = filedialog.askopenfilename(
            title="Selecione o comprovante",
            filetypes=[
                ("Arquivos PDF e imagens", "*.pdf *.png *.jpg *.jpeg"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if arquivo:
            comprovante_selecionado["caminho"] = arquivo
            label_arquivo.config(text=f"Selecionado: {Path(arquivo).name}")

    def aplicar_mascara_data(evento):
        texto = campos["Data do comprovante"].get()
        numeros = "".join(c for c in texto if c.isdigit())[:8]

        formatado = ""

        if len(numeros) >= 1:
            formatado += numeros[:2]

        if len(numeros) >= 3:
            formatado += "/" + numeros[2:4]

        if len(numeros) >= 5:
            formatado += "/" + numeros[4:8]

        campos["Data do comprovante"].delete(0, tk.END)
        campos["Data do comprovante"].insert(0, formatado)

    campos["Data do comprovante"].bind("<KeyRelease>", aplicar_mascara_data)

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

        titulo_resumo = tk.Label(
            janela_resumo,
            text="Resumo do Arquivamento",
            font=("Arial", 16, "bold")
        )
        titulo_resumo.pack(pady=15)

        caixa_texto = tk.Text(
            janela_resumo,
            width=75,
            height=16,
            wrap="word"
        )
        caixa_texto.pack(padx=15, pady=10)

        caixa_texto.insert(tk.END, "DADOS DO COMPROVANTE\n")
        caixa_texto.insert(tk.END, "=" * 40 + "\n\n")

        for campo, valor in dados.items():
            caixa_texto.insert(tk.END, f"{campo}: {valor}\n")

        caixa_texto.insert(tk.END, "\nARQUIVO SELECIONADO\n")
        caixa_texto.insert(tk.END, "=" * 40 + "\n\n")
        caixa_texto.insert(
            tk.END,
            f"{Path(comprovante_selecionado['caminho']).name}\n"
        )

        caixa_texto.config(state="disabled")

        def confirmar():
            janela_resumo.destroy()
            executar_arquivamento(dados)

        def cancelar():
            janela_resumo.destroy()

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
            command=cancelar
        ).grid(row=0, column=1, padx=10)

    def executar_arquivamento(dados):
        try:
            arquivar_comprovante(dados, comprovante_selecionado["caminho"])

            messagebox.showinfo(
                "Arquivamento concluído",
                "Comprovante arquivado com sucesso."
            )

            janela.destroy()

        except Exception as erro:
            messagebox.showerror(
                "Erro inesperado",
                f"Ocorreu um erro ao arquivar o comprovante:\n\n{erro}"
            )

    def finalizar():
        dados = coletar_dados()

        valido, mensagem = validar_dados_comprovante(
            dados,
            comprovante_selecionado["caminho"]
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
            "Deseja apagar todos os dados preenchidos e remover o comprovante anexado?"
        )

        if not resposta:
            return

        for campo in campos.values():
            if hasattr(campo, "delete"):
                campo.delete(0, tk.END)
            else:
                campo.set("Selecione")

        comprovante_selecionado["caminho"] = ""
        label_arquivo.config(text="Nenhum comprovante selecionado.")

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=15)

    tk.Button(
        frame_botoes,
        text="Selecionar comprovante",
        width=25,
        command=selecionar_comprovante
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        frame_botoes,
        text="Limpar formulário",
        width=25,
        command=limpar_formulario
    ).grid(row=0, column=1, padx=10)

    tk.Button(
        janela,
        text="Finalizar arquivamento",
        width=25,
        height=2,
        command=finalizar
    ).pack(pady=20)