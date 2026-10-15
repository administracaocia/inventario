import flet as ft
import sqlite3
import os
import pandas as pd

def main(page: ft.Page):
    page.title = "Inventário Físico - 1ª Cia"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    db_name = "inventario_criado_do_zero.db"

    # Inicializa o banco e a tabela
    def inicializar_banco():
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_inventariados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patrimonio TEXT,
                serie TEXT,
                nome_material TEXT,
                status_plaqueta TEXT,
                observacao TEXT,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    inicializar_banco()

    def obter_total_catalogados():
        if not os.path.exists(db_name):
            return 0
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM itens_inventariados")
        total = cursor.fetchone()[0]
        conn.close()
        return total

    # Componentes da Interface
    txt_contador = ft.Text(f"📊 Itens catalogados: {obter_total_catalogados()}", size=15, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_800)
    
    txt_nome = ft.TextField(label="Nome do Material (Ex: Rádio APX, Mesa, Colete)", width=320)
    txt_patrimonio = ft.TextField(label="Número do Patrimônio (se houver)", width=320)
    txt_serie = ft.TextField(label="Número de Série / Chassi", width=320)
    
    status_plaqueta_dropdown = ft.Dropdown(
        label="Situação da Plaqueta Física",
        width=320,
        options=[
            ft.dropdown.Option("COM_PLAQUETA", "Com Plaqueta Visível"),
            ft.dropdown.Option("SEM_PLAQUETA", "Sem Plaqueta (Cadastrando agora)"),
        ],
    )
    
    txt_obs = ft.TextField(label="Observações (opcional)", width=320, multiline=True, max_lines=2)

    def salvar_item(e):
        pat = txt_patrimonio.value.strip()
        ser = txt_serie.value.strip()
        nome = txt_nome.value.strip()
        status = status_plaqueta_dropdown.value

        if not nome:
            page.snack_bar = ft.SnackBar(ft.Text("O campo 'Nome do Material' é obrigatório!"))
            page.snack_bar.open = True
            page.update()
            return

        if not status:
            page.snack_bar = ft.SnackBar(ft.Text("Selecione a situação da plaqueta!"))
            page.snack_bar.open = True
            page.update()
            return

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO itens_inventariados (patrimonio, serie, nome_material, status_plaqueta, observacao)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            pat if pat else "N/D",
            ser if ser else "N/D",
            nome,
            status,
            txt_obs.value
        ))
        conn.commit()
        conn.close()

        # Limpa os campos para o próximo item
        txt_patrimonio.value = ""
        txt_serie.value = ""
        txt_nome.value = ""
        status_plaqueta_dropdown.value = None
        txt_obs.value = ""
        
        # Atualiza o contador na tela
        txt_contador.value = f"📊 Itens catalogados: {obter_total_catalogados()}"
        page.update()

        page.snack_bar = ft.SnackBar(ft.Text("Item catalogado com sucesso!"))
        page.snack_bar.open = True
        page.update()

    def exportar_para_excel(e):
        if not os.path.exists(db_name) or obter_total_catalogados() == 0:
            page.snack_bar = ft.SnackBar(ft.Text("Nenhum item cadastrado para exportar!"))
            page.snack_bar.open = True
            page.update()
            return

        conn = sqlite3.connect(db_name)
        df = pd.read_sql("SELECT * FROM itens_inventariados", conn)
        conn.close()

        nome_arquivo = "Relatorio_Inventario_In_Loco.xlsx"
        df.to_excel(nome_arquivo, index=False)
        
        page.snack_bar = ft.SnackBar(ft.Text(f"Relatório salvo como '{nome_arquivo}' na pasta!"))
        page.snack_bar.open = True
        page.update()

    btn_salvar = ft.ElevatedButton("Salvar Item na Cia", on_click=salvar_item, icon=ft.icons.SAVE, color=ft.colors.WHITE, bgcolor=ft.colors.BLUE_700)
    btn_exportar = ft.ElevatedButton("Exportar para Excel (.xlsx)", on_click=exportar_para_excel, icon=ft.icons.DOWNLOAD, color=ft.colors.WHITE, bgcolor=ft.colors.GREEN_700)

    page.add(
        ft.Text("Inventário Físico - 1ª Cia", size=18, weight=ft.FontWeight.BOLD),
        txt_contador,
        ft.Divider(),
        txt_nome,
        txt_patrimonio,
        txt_serie,
        status_plaqueta_dropdown,
        txt_obs,
        ft.Divider(),
        btn_salvar,
        ft.Divider(),  # Substituído VerticalDivider com erro por Divider limpo
        btn_exportar
    )

ft.app(target=main)