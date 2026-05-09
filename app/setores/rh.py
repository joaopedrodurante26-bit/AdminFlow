import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from app.servicos.arquivos import criar_pasta_funcionario
from app.servicos.validacao import validar_dados_funcionario


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

        entrada = tk.Entry(frame_form, width=45)
        entrada.grid(row=i, column=1, padx=10, pady=6)

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

        for nome_campo, entrada in campos.items():
            dados[nome_campo] = entrada.get().strip()

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

    botao_finalizar = tk.Button(
        janela,
        text="Finalizar cadastro",
        width=25,
        height=2,
        command=finalizar_cadastro
    )
    botao_finalizar.pack(pady=20)