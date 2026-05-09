import tkinter as tk
from tkinter import filedialog, messagebox

from AdminFlow.app.servicos.configuracoes.configuracoes import (
    carregar_configuracoes,
    salvar_configuracoes,
    obter_pasta_base
)
from AdminFlow.app.servicos.rh.rh_arquivos import verificar_ou_criar_estrutura


def abrir_configurar_pasta_base(root):
    janela = tk.Toplevel(root)
    janela.title("Configurar Pasta Base")
    janela.geometry("650x250")
    janela.minsize(600, 220)

    config = carregar_configuracoes()

    pasta_atual = tk.StringVar(value=str(obter_pasta_base()))

    titulo = tk.Label(
        janela,
        text="Configurar Pasta Base",
        font=("Arial", 18, "bold")
    )
    titulo.pack(pady=15)

    explicacao = tk.Label(
        janela,
        text="Selecione a pasta principal onde os documentos da empresa serão organizados.",
        font=("Arial", 10)
    )
    explicacao.pack(pady=5)

    frame_pasta = tk.Frame(janela)
    frame_pasta.pack(pady=15)

    entrada_pasta = tk.Entry(
        frame_pasta,
        textvariable=pasta_atual,
        width=70
    )
    entrada_pasta.grid(row=0, column=0, padx=5)

    def selecionar_pasta():
        pasta = filedialog.askdirectory(
            title="Selecione a pasta base da empresa"
        )

        if pasta:
            pasta_atual.set(pasta)

    botao_selecionar = tk.Button(
        frame_pasta,
        text="Selecionar",
        command=selecionar_pasta
    )
    botao_selecionar.grid(row=0, column=1, padx=5)

    def salvar():
        caminho = pasta_atual.get().strip()

        if not caminho:
            messagebox.showerror(
                "Erro",
                "A pasta base não pode ficar vazia."
            )
            return

        config["pasta_base"] = caminho

        salvar_configuracoes(config)

        messagebox.showinfo(
            "Configuração salva",
            "Pasta base configurada com sucesso."
        )

        janela.destroy()

    botao_salvar = tk.Button(
        janela,
        text="Salvar configuração",
        width=25,
        height=2,
        command=salvar
    )
    botao_salvar.pack(pady=10)

def abrir_verificar_estrutura(root):
    try:
        pastas_criadas = verificar_ou_criar_estrutura()

        if pastas_criadas:
            mensagem = "Estrutura verificada.\n\nPastas criadas:\n\n"
            mensagem += "\n".join(pastas_criadas[:15])

            if len(pastas_criadas) > 15:
                mensagem += f"\n\n... e mais {len(pastas_criadas) - 15} pastas."
        else:
            mensagem = "Estrutura verificada.\n\nNenhuma pasta precisou ser criada."

        messagebox.showinfo(
            "Verificação concluída",
            mensagem
        )

    except Exception as erro:
        messagebox.showerror(
            "Erro",
            f"Ocorreu um erro ao verificar a estrutura:\n\n{erro}"
        )