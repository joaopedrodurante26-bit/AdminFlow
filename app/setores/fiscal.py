import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from app.servicos.fiscal.fiscal_arquivos import arquivar_nf_emitida
from app.servicos.fiscal.fiscal_validacao import validar_dados_nf_emitida


def abrir_arquivar_nf_emitida(root):
    janela = tk.Toplevel(root)
    janela.title("Arquivar NF Emitida")
    janela.geometry("780x640")
    janela.minsize(720, 580)

    campos = {}
    arquivo_nf = {"caminho": ""}

    TIPOS_NF = [
        "Venda",
        "Serviço",
        "Remessa",
        "Devolução",
        "Bonificação",
        "Outros"
    ]

    def existe_progresso():
        for campo in campos.values():
            if campo.get().strip():
                return True
        return bool(arquivo_nf["caminho"])

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
        text="Arquivar NF Emitida",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    frame_form = tk.Frame(janela)
    frame_form.pack(pady=10)

    campos_texto = [
        "Data de emissão",
        "Número da NF",
        "Cliente",
        "CNPJ/CPF do cliente",
        "Valor total",
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

        entrada = tk.Entry(frame_form, width=50)
        entrada.grid(row=i, column=1, padx=10, pady=5)
        campos[label] = entrada

    linha = len(campos_texto)

    tk.Label(frame_form, text="Tipo de NF:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=5
    )

    tipo_nf = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, tipo_nf, *TIPOS_NF).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=5
    )
    campos["Tipo de NF"] = tipo_nf

    def aplicar_mascara_data(evento):
        texto = campos["Data de emissão"].get()
        numeros = "".join(c for c in texto if c.isdigit())[:8]

        formatado = ""

        if len(numeros) >= 1:
            formatado += numeros[:2]

        if len(numeros) >= 3:
            formatado += "/" + numeros[2:4]

        if len(numeros) >= 5:
            formatado += "/" + numeros[4:8]

        campos["Data de emissão"].delete(0, tk.END)
        campos["Data de emissão"].insert(0, formatado)

    campos["Data de emissão"].bind("<KeyRelease>", aplicar_mascara_data)

    frame_arquivo = tk.Frame(janela)
    frame_arquivo.pack(pady=12)

    label_arquivo = tk.Label(
        frame_arquivo,
        text="Nenhuma NF selecionada.",
        width=85,
        anchor="w"
    )
    label_arquivo.pack(pady=5)

    def selecionar_nf():
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo da NF emitida",
            filetypes=[
                ("PDF e XML", "*.pdf *.xml"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if arquivo:
            arquivo_nf["caminho"] = arquivo
            label_arquivo.config(text=f"Selecionado: {Path(arquivo).name}")

    def remover_nf():
        arquivo_nf["caminho"] = ""
        label_arquivo.config(text="Nenhuma NF selecionada.")

    def coletar_dados():
        dados = {}

        for nome_campo, campo in campos.items():
            dados[nome_campo] = campo.get().strip()

        return dados

    def exibir_resumo_confirmacao(dados):
        janela_resumo = tk.Toplevel(janela)
        janela_resumo.title("Confirmar NF Emitida")
        janela_resumo.geometry("700x500")
        janela_resumo.minsize(640, 450)

        tk.Label(
            janela_resumo,
            text="Resumo da NF Emitida",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        caixa_texto = tk.Text(
            janela_resumo,
            width=82,
            height=18,
            wrap="word"
        )
        caixa_texto.pack(padx=15, pady=10)

        caixa_texto.insert(tk.END, "DADOS DA NF EMITIDA\n")
        caixa_texto.insert(tk.END, "=" * 45 + "\n\n")

        for campo, valor in dados.items():
            caixa_texto.insert(tk.END, f"{campo}: {valor}\n")

        caixa_texto.insert(tk.END, "\nARQUIVO SELECIONADO\n")
        caixa_texto.insert(tk.END, "=" * 45 + "\n\n")
        caixa_texto.insert(tk.END, Path(arquivo_nf["caminho"]).name)

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
            arquivar_nf_emitida(dados, arquivo_nf["caminho"])

            messagebox.showinfo(
                "Arquivamento concluído",
                "NF emitida arquivada com sucesso."
            )

            janela.destroy()

        except Exception as erro:
            messagebox.showerror(
                "Erro inesperado",
                f"Ocorreu um erro ao arquivar a NF emitida:\n\n{erro}"
            )

    def finalizar():
        dados = coletar_dados()

        valido, mensagem = validar_dados_nf_emitida(
            dados,
            arquivo_nf["caminho"]
        )

        if not valido:
            messagebox.showerror("Erro de validação", mensagem)
            return

        exibir_resumo_confirmacao(dados)

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=15)

    tk.Button(
        frame_botoes,
        text="Selecionar NF",
        width=22,
        command=selecionar_nf
    ).grid(row=0, column=0, padx=8)

    tk.Button(
        frame_botoes,
        text="Remover NF",
        width=22,
        command=remover_nf
    ).grid(row=0, column=1, padx=8)

    tk.Button(
        janela,
        text="Finalizar arquivamento",
        width=25,
        height=2,
        command=finalizar
    ).pack(pady=20)