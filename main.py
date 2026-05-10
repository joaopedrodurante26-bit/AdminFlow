import tkinter as tk
from tkinter import messagebox


from app.setores.configuracoes import (
    abrir_configurar_pasta_base,
    abrir_verificar_estrutura
)

from app.servicos.rh.rh_arquivos import (
    estrutura_existe,
    verificar_ou_criar_estrutura
)

from app.setores.financeiro import (
    abrir_arquivar_comprovante,
    abrir_registrar_conta_a_pagar,
    abrir_registrar_conta_a_receber,
    abrir_arquivar_extrato_bancario
)

from app.setores.rh import (
    abrir_cadastro_funcionario,
    abrir_arquivar_folha_ponto,
    abrir_registrar_ferias,
    abrir_registrar_advertencia,
    abrir_mover_funcionario_desligados
)

from app.setores.fiscal import (
    abrir_arquivar_nf_emitida,
    abrir_arquivar_nf_recebida,
    abrir_arquivar_guia_imposto
)

from app.setores.qualidade import (
    abrir_arquivar_analise_agua
)


APP_NAME = "AdminFlow"
APP_VERSION = "0.1.0"


class AdminFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - Sistema Administrativo")
        self.root.geometry("800x500")
        self.root.minsize(700, 450)

        self.verificar_estrutura_inicial()
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
            ("Arquivar folha de ponto", lambda: abrir_arquivar_folha_ponto(self.root)),
            ("Registrar férias", lambda: abrir_registrar_ferias(self.root)),
            ("Registrar advertência", lambda: abrir_registrar_advertencia(self.root)),
            ("Mover funcionário para desligados", lambda: abrir_mover_funcionario_desligados(self.root)),
        ]
        self.criar_tela_setor("Recursos Humanos", acoes)

    def abrir_financeiro(self):
        acoes = [
            ("Arquivar comprovante", lambda: abrir_arquivar_comprovante(self.root)),
            ("Registrar conta a pagar", lambda: abrir_registrar_conta_a_pagar(self.root)),
            ("Registrar conta a receber", lambda: abrir_registrar_conta_a_receber(self.root)),
            ("Arquivar extrato bancário", lambda: abrir_arquivar_extrato_bancario(self.root)),
        ]
        self.criar_tela_setor("Financeiro", acoes)

    def abrir_fiscal(self):
        acoes = [
            ("Arquivar NF emitida", lambda: abrir_arquivar_nf_emitida(self.root)),
            ("Arquivar NF recebida", lambda: abrir_arquivar_nf_recebida(self.root)),
            ("Arquivar guia de imposto", lambda: abrir_arquivar_guia_imposto(self.root))
        ]
        self.criar_tela_setor("Fiscal / Contábil", acoes)

    def abrir_logistica(self):
        acoes = [
            ("Arquivar romaneio", self.acao_em_desenvolvimento),
            ("Registrar manutenção de veículo", self.acao_em_desenvolvimento),
            ("Arquivar comprovante de entrega", self.acao_em_desenvolvimento)
        ]
        self.criar_tela_setor("Logística", acoes)

    def abrir_qualidade(self):
        acoes = [
            ("Arquivar análise da água", lambda: abrir_arquivar_analise_agua(self.root)),
            ("Registrar controle de lote", self.acao_em_desenvolvimento),
            ("Arquivar auditoria", self.acao_em_desenvolvimento),
            ("Arquivar licença", self.acao_em_desenvolvimento)
        ]
        self.criar_tela_setor("Qualidade", acoes)

    def abrir_contratos(self):
        acoes = [
            ("Arquivar contrato de cliente", self.acao_em_desenvolvimento),
            ("Arquivar contrato de fornecedor", self.acao_em_desenvolvimento),
            ("Arquivar contrato de prestador", self.acao_em_desenvolvimento)
        ]
        self.criar_tela_setor("Contratos", acoes)

    def abrir_relatorios(self):
        acoes = [
            ("Gerar relatório de arquivos", self.acao_em_desenvolvimento),
            ("Gerar relatório de pendências", self.acao_em_desenvolvimento)
        ]
        self.criar_tela_setor("Relatórios", acoes)

    def abrir_configuracoes(self):
        acoes = [
            ("Configurar pasta base", lambda: abrir_configurar_pasta_base(self.root)),
            ("Verificar estrutura de pastas", lambda: abrir_verificar_estrutura(self.root))
        ]
        self.criar_tela_setor("Configurações", acoes)

    def acao_em_desenvolvimento(self):
        messagebox.showinfo(
            "Em desenvolvimento",
            "Esta função ainda será implementada."
        )

    def verificar_estrutura_inicial(self):
        if estrutura_existe():
            return

        resposta = messagebox.askyesno(
            "Estrutura não encontrada",
            "A estrutura principal de pastas da empresa ainda não foi encontrada.\n\n"
            "Deseja criar a estrutura padrão agora?"
        )

        if resposta:
            try:
                pastas_criadas = verificar_ou_criar_estrutura()

                messagebox.showinfo(
                    "Estrutura criada",
                    f"Estrutura criada com sucesso.\n\nTotal de pastas criadas: {len(pastas_criadas)}"
                )

            except Exception as erro:
                messagebox.showerror(
                    "Erro ao criar estrutura",
                    f"Não foi possível criar a estrutura de pastas:\n\n{erro}"
                )


def main():
    root = tk.Tk()
    app = AdminFlowApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()