import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime

from app.servicos.arquivos import criar_pasta_funcionario
from app.servicos.validacao import validar_dados_funcionario


def abrir_cadastro_funcionario(root):
    janela = tk.Toplevel(root)
    janela.title("Cadastrar Funcionário")
    janela.geometry("650x600")
    janela.minsize(600, 500)

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

        entrada = tk.Entry(frame_form, width=40)
        entrada.grid(row=i, column=1, padx=10, pady=6)

        campos[label] = entrada

    frame_docs = tk.Frame(janela)
    frame_docs.pack(pady=15)

    lista_docs = tk.Listbox(frame_docs, width=70, height=8)
    lista_docs.pack()

    def selecionar_documentos():
        arquivos = filedialog.askopenfilenames(
            title="Selecione os documentos do funcionário",
            filetypes=[
                ("Arquivos PDF", "*.pdf"),
                ("Imagens", "*.png *.jpg *.jpeg"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if arquivos:
            for arquivo in arquivos:
                if arquivo not in documentos_selecionados:
                    documentos_selecionados.append(arquivo)
                    lista_docs.insert(tk.END, Path(arquivo).name)

    def validar_campos():
        dados = {}

        for nome_campo, entrada in campos.items():
            dados[nome_campo] = entrada.get().strip()

        valido, mensagem = validar_dados_funcionario(dados, documentos_selecionados)

        if not valido:
            messagebox.showerror("Erro de validação", mensagem)
            return None

        return dados

    def finalizar_cadastro():
        dados = validar_campos()

        if dados is None:
            return

        confirmar = messagebox.askyesno(
            "Confirmar cadastro",
            "Todos os dados foram preenchidos.\n\nDeseja criar a pasta do funcionário?"
        )

        if not confirmar:
            return

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

    botao_docs = tk.Button(
        janela,
        text="Selecionar documentos",
        width=25,
        command=selecionar_documentos
    )
    botao_docs.pack(pady=10)

    botao_finalizar = tk.Button(
        janela,
        text="Finalizar cadastro",
        width=25,
        height=2,
        command=finalizar_cadastro
    )
    botao_finalizar.pack(pady=20)