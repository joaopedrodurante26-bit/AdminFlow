import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from AdminFlow.app.servicos.financeiro.financeiro_arquivos import arquivar_comprovante
from AdminFlow.app.servicos.financeiro.financeiro_validacao import validar_dados_comprovante
from app.servicos.financeiro.financeiro_arquivos import arquivar_comprovante, registrar_conta_a_pagar, registrar_conta_a_receber
from app.servicos.financeiro.financeiro_validacao import validar_dados_comprovante, validar_dados_conta_a_pagar, validar_dados_conta_a_receber


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

def abrir_registrar_conta_a_pagar(root):
    janela = tk.Toplevel(root)
    janela.title("Registrar Conta a Pagar")
    janela.geometry("780x650")
    janela.minsize(720, 580)

    campos = {}
    documento_anexado = {"caminho": ""}

    STATUS_OPCOES = [
        "Pendente",
        "Pago",
        "Vencido",
        "Cancelado"
    ]

    FORMAS_PAGAMENTO = [
        "PIX",
        "Boleto",
        "Transferência",
        "Dinheiro",
        "Cartão",
        "Débito automático",
        "Outros"
    ]

    CATEGORIAS = [
        "Fornecedor",
        "Funcionário",
        "Imposto",
        "Aluguel",
        "Energia",
        "Água",
        "Internet",
        "Manutenção",
        "Combustível",
        "Compra de insumos",
        "Serviço terceirizado",
        "Outros"
    ]

    def existe_progresso():
        for campo in campos.values():
            if campo.get().strip():
                return True

        if documento_anexado["caminho"]:
            return True

        return False

    def ao_fechar_janela():
        if not existe_progresso():
            janela.destroy()
            return

        resposta = messagebox.askyesno(
            "Cancelar registro",
            "Há informações preenchidas ou documento anexado.\n\n"
            "Se você fechar esta janela, o registro será cancelado.\n\n"
            "Deseja realmente sair?"
        )

        if resposta:
            janela.destroy()

    janela.protocol("WM_DELETE_WINDOW", ao_fechar_janela)

    titulo = tk.Label(
        janela,
        text="Registrar Conta a Pagar",
        font=("Arial", 18, "bold")
    )
    titulo.pack(pady=15)

    frame_form = tk.Frame(janela)
    frame_form.pack(pady=10)

    campos_texto = [
        "Data de emissão",
        "Data de vencimento",
        "Fornecedor/Favorecido",
        "Descrição",
        "Valor",
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

        entrada = tk.Entry(frame_form, width=50)
        entrada.grid(row=i, column=1, padx=10, pady=6)

        campos[label] = entrada

    linha = len(campos_texto)

    tk.Label(frame_form, text="Categoria:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    categoria = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, categoria, *CATEGORIAS).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=6
    )
    campos["Categoria"] = categoria

    linha += 1

    tk.Label(frame_form, text="Forma de pagamento:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    forma_pagamento = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, forma_pagamento, *FORMAS_PAGAMENTO).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=6
    )
    campos["Forma de pagamento"] = forma_pagamento

    linha += 1

    tk.Label(frame_form, text="Status:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    status = tk.StringVar(value="Pendente")
    tk.OptionMenu(frame_form, status, *STATUS_OPCOES).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=6
    )
    campos["Status"] = status

    frame_arquivo = tk.Frame(janela)
    frame_arquivo.pack(pady=12)

    label_arquivo = tk.Label(
        frame_arquivo,
        text="Nenhum documento anexado.",
        width=85,
        anchor="w"
    )
    label_arquivo.pack(pady=5)

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

    campos["Data de emissão"].bind(
        "<KeyRelease>",
        lambda evento: aplicar_mascara_data("Data de emissão")
    )

    campos["Data de vencimento"].bind(
        "<KeyRelease>",
        lambda evento: aplicar_mascara_data("Data de vencimento")
    )

    def selecionar_documento():
        arquivo = filedialog.askopenfilename(
            title="Selecione documento da conta",
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
        janela_resumo.title("Confirmar Conta a Pagar")
        janela_resumo.geometry("680x500")
        janela_resumo.minsize(620, 450)

        tk.Label(
            janela_resumo,
            text="Resumo da Conta a Pagar",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        caixa_texto = tk.Text(
            janela_resumo,
            width=78,
            height=18,
            wrap="word"
        )
        caixa_texto.pack(padx=15, pady=10)

        caixa_texto.insert(tk.END, "DADOS DA CONTA\n")
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

        def cancelar():
            janela_resumo.destroy()

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
            command=cancelar
        ).grid(row=0, column=1, padx=10)

    def executar_registro(dados):
        try:
            registrar_conta_a_pagar(dados, documento_anexado["caminho"])

            messagebox.showinfo(
                "Registro concluído",
                "Conta a pagar registrada com sucesso."
            )

            janela.destroy()

        except Exception as erro:
            messagebox.showerror(
                "Erro inesperado",
                f"Ocorreu um erro ao registrar a conta a pagar:\n\n{erro}"
            )

    def finalizar():
        dados = coletar_dados()

        valido, mensagem = validar_dados_conta_a_pagar(
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
            "Deseja apagar todos os dados preenchidos e remover o documento anexado?"
        )

        if not resposta:
            return

        for campo in campos.values():
            if hasattr(campo, "delete"):
                campo.delete(0, tk.END)
            else:
                campo.set("Selecione")

        status.set("Pendente")
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

def abrir_registrar_conta_a_receber(root):
    janela = tk.Toplevel(root)
    janela.title("Registrar Conta a Receber")
    janela.geometry("780x650")
    janela.minsize(720, 580)

    campos = {}
    documento_anexado = {"caminho": ""}

    STATUS_OPCOES = [
        "A receber",
        "Recebido",
        "Atrasado",
        "Cancelado"
    ]

    FORMAS_RECEBIMENTO = [
        "PIX",
        "Boleto",
        "Transferência",
        "Dinheiro",
        "Cartão",
        "Depósito",
        "Outros"
    ]

    CATEGORIAS = [
        "Cliente",
        "Distribuidor",
        "Mercado",
        "Venda direta",
        "Contrato",
        "Reembolso",
        "Outros"
    ]

    def existe_progresso():
        for campo in campos.values():
            if campo.get().strip():
                return True

        if documento_anexado["caminho"]:
            return True

        return False

    def ao_fechar_janela():
        if not existe_progresso():
            janela.destroy()
            return

        resposta = messagebox.askyesno(
            "Cancelar registro",
            "Há informações preenchidas ou documento anexado.\n\n"
            "Se você fechar esta janela, o registro será cancelado.\n\n"
            "Deseja realmente sair?"
        )

        if resposta:
            janela.destroy()

    janela.protocol("WM_DELETE_WINDOW", ao_fechar_janela)

    titulo = tk.Label(
        janela,
        text="Registrar Conta a Receber",
        font=("Arial", 18, "bold")
    )
    titulo.pack(pady=15)

    frame_form = tk.Frame(janela)
    frame_form.pack(pady=10)

    campos_texto = [
        "Data de emissão",
        "Data prevista de recebimento",
        "Cliente/Pagador",
        "Descrição",
        "Valor",
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

        entrada = tk.Entry(frame_form, width=50)
        entrada.grid(row=i, column=1, padx=10, pady=6)

        campos[label] = entrada

    linha = len(campos_texto)

    tk.Label(frame_form, text="Categoria:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    categoria = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, categoria, *CATEGORIAS).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=6
    )
    campos["Categoria"] = categoria

    linha += 1

    tk.Label(frame_form, text="Forma de recebimento:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    forma_recebimento = tk.StringVar(value="Selecione")
    tk.OptionMenu(frame_form, forma_recebimento, *FORMAS_RECEBIMENTO).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=6
    )
    campos["Forma de recebimento"] = forma_recebimento

    linha += 1

    tk.Label(frame_form, text="Status:").grid(
        row=linha,
        column=0,
        sticky="e",
        padx=10,
        pady=6
    )

    status = tk.StringVar(value="A receber")
    tk.OptionMenu(frame_form, status, *STATUS_OPCOES).grid(
        row=linha,
        column=1,
        sticky="w",
        padx=10,
        pady=6
    )
    campos["Status"] = status

    frame_arquivo = tk.Frame(janela)
    frame_arquivo.pack(pady=12)

    label_arquivo = tk.Label(
        frame_arquivo,
        text="Nenhum documento anexado.",
        width=85,
        anchor="w"
    )
    label_arquivo.pack(pady=5)

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

    campos["Data de emissão"].bind(
        "<KeyRelease>",
        lambda evento: aplicar_mascara_data("Data de emissão")
    )

    campos["Data prevista de recebimento"].bind(
        "<KeyRelease>",
        lambda evento: aplicar_mascara_data("Data prevista de recebimento")
    )

    def selecionar_documento():
        arquivo = filedialog.askopenfilename(
            title="Selecione documento da conta a receber",
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
        janela_resumo.title("Confirmar Conta a Receber")
        janela_resumo.geometry("680x500")
        janela_resumo.minsize(620, 450)

        tk.Label(
            janela_resumo,
            text="Resumo da Conta a Receber",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        caixa_texto = tk.Text(
            janela_resumo,
            width=78,
            height=18,
            wrap="word"
        )
        caixa_texto.pack(padx=15, pady=10)

        caixa_texto.insert(tk.END, "DADOS DA CONTA\n")
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

        def cancelar():
            janela_resumo.destroy()

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
            command=cancelar
        ).grid(row=0, column=1, padx=10)

    def executar_registro(dados):
        try:
            registrar_conta_a_receber(dados, documento_anexado["caminho"])

            messagebox.showinfo(
                "Registro concluído",
                "Conta a receber registrada com sucesso."
            )

            janela.destroy()

        except Exception as erro:
            messagebox.showerror(
                "Erro inesperado",
                f"Ocorreu um erro ao registrar a conta a receber:\n\n{erro}"
            )

    def finalizar():
        dados = coletar_dados()

        valido, mensagem = validar_dados_conta_a_receber(
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
            "Deseja apagar todos os dados preenchidos e remover o documento anexado?"
        )

        if not resposta:
            return

        for campo in campos.values():
            if hasattr(campo, "delete"):
                campo.delete(0, tk.END)
            else:
                campo.set("Selecione")

        status.set("A receber")
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