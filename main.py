import tkinter as tk
from tkinter import messagebox
from app.setores.rh import abrir_cadastro_funcionario


APP_NAME = "AdminFlow"
APP_VERSION = "0.1.0"


class AdminFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - Sistema Administrativo")
        self.root.geometry("800x500")
        self.root.minsize(700, 450)

        self.criar_tela_principal()

    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def criar_tela_principal(self):
        self.limpar_tela()

        titulo = tk.Label(
            self.root,
            text="AdminFlow",
            font=("Arial", 24, "bold")
        )
        titulo.pack(pady=20)

        subtitulo = tk.Label(
            self.root,
            text="Sistema local de organização documental e rotinas administrativas",
            font=("Arial", 11)
        )
        subtitulo.pack(pady=5)

        frame_botoes = tk.Frame(self.root)
        frame_botoes.pack(pady=30)

        setores = [
            ("RH", self.abrir_rh),
            ("Financeiro", self.abrir_financeiro),
            ("Fiscal / Contábil", self.abrir_fiscal),
            ("Logística", self.abrir_logistica),
            ("Qualidade", self.abrir_qualidade),
            ("Contratos", self.abrir_contratos),
            ("Relatórios", self.abrir_relatorios),
            ("Configurações", self.abrir_configuracoes),
        ]

        for index, (nome, comando) in enumerate(setores):
            linha = index // 2
            coluna = index % 2

            botao = tk.Button(
                frame_botoes,
                text=nome,
                width=25,
                height=2,
                command=comando
            )
            botao.grid(row=linha, column=coluna, padx=15, pady=10)

        rodape = tk.Label(
            self.root,
            text=f"Versão {APP_VERSION}",
            font=("Arial", 9)
        )
        rodape.pack(side="bottom", pady=10)

    def criar_tela_setor(self, nome_setor, acoes):
        self.limpar_tela()

        titulo = tk.Label(
            self.root,
            text=nome_setor,
            font=("Arial", 22, "bold")
        )
        titulo.pack(pady=20)

        frame_acoes = tk.Frame(self.root)
        frame_acoes.pack(pady=20)

        for index, (nome_acao, comando) in enumerate(acoes):
            botao = tk.Button(
                frame_acoes,
                text=nome_acao,
                width=35,
                height=2,
                command=comando
            )
            botao.pack(pady=8)

        botao_voltar = tk.Button(
            self.root,
            text="Voltar",
            width=20,
            command=self.criar_tela_principal
        )
        botao_voltar.pack(pady=20)

    def abrir_rh(self):
        acoes = [
            ("Cadastrar funcionário", lambda: abrir_cadastro_funcionario(self.root)),
            ("Arquivar folha de ponto", self.acao_em_desenvolvimento),
            ("Registrar férias", self.acao_em_desenvolvimento),
            ("Registrar advertência", self.acao_em_desenvolvimento),
            ("Mover funcionário para desligados", self.acao_em_desenvolvimento),
        ]
        self.criar_tela_setor("Recursos Humanos", acoes)

    def abrir_financeiro(self):
        acoes = [
            ("Arquivar comprovante", self.acao_em_desenvolvimento),
            ("Registrar conta a pagar", self.acao_em_desenvolvimento),
            ("Registrar conta a receber", self.acao_em_desenvolvimento),
            ("Arquivar extrato bancário", self.acao_em_desenvolvimento),
        ]
        self.criar_tela_setor("Financeiro", acoes)

    def abrir_fiscal(self):
        acoes = [
            ("Arquivar NF emitida", self.acao_em_desenvolvimento),
            ("Arquivar NF recebida", self.acao_em_desenvolvimento),
            ("Arquivar guia de imposto", self.acao_em_desenvolvimento),
        ]
        self.criar_tela_setor("Fiscal / Contábil", acoes)

    def abrir_logistica(self):
        acoes = [
            ("Arquivar romaneio", self.acao_em_desenvolvimento),
            ("Registrar manutenção de veículo", self.acao_em_desenvolvimento),
            ("Arquivar comprovante de entrega", self.acao_em_desenvolvimento),
        ]
        self.criar_tela_setor("Logística", acoes)

    def abrir_qualidade(self):
        acoes = [
            ("Arquivar análise da água", self.acao_em_desenvolvimento),
            ("Registrar controle de lote", self.acao_em_desenvolvimento),
            ("Arquivar auditoria", self.acao_em_desenvolvimento),
            ("Arquivar licença", self.acao_em_desenvolvimento),
        ]
        self.criar_tela_setor("Qualidade", acoes)

    def abrir_contratos(self):
        acoes = [
            ("Arquivar contrato de cliente", self.acao_em_desenvolvimento),
            ("Arquivar contrato de fornecedor", self.acao_em_desenvolvimento),
            ("Arquivar contrato de prestador", self.acao_em_desenvolvimento),
        ]
        self.criar_tela_setor("Contratos", acoes)

    def abrir_relatorios(self):
        acoes = [
            ("Gerar relatório de arquivos", self.acao_em_desenvolvimento),
            ("Gerar relatório de pendências", self.acao_em_desenvolvimento),
        ]
        self.criar_tela_setor("Relatórios", acoes)

    def abrir_configuracoes(self):
        acoes = [
            ("Configurar pasta base", self.acao_em_desenvolvimento),
            ("Verificar estrutura de pastas", self.acao_em_desenvolvimento),
        ]
        self.criar_tela_setor("Configurações", acoes)

    def acao_em_desenvolvimento(self):
        messagebox.showinfo(
            "Em desenvolvimento",
            "Esta função ainda será implementada."
        )


def main():
    root = tk.Tk()
    app = AdminFlowApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()