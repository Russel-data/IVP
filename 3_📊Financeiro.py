import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Dados de login: usuários e senhas
USER_CREDENTIALS = {
    "admin": "admin123",
    "user1": "mypassword",
    "user2": "streamlit"
}

# Função para verificar o login
def check_login(username, password):
    return USER_CREDENTIALS.get(username) == password

# Carregar os dados CSV
def load_data(file):
    data = pd.read_csv(file, on_bad_lines='skip', sep=',')  # Usa ',' como separador padrão
    if 'DT_contrato' in data.columns:
        # Converte 'DT_contrato' para datetime no formato DD/MM/YYYY
        data['DT_contrato'] = pd.to_datetime(data['DT_contrato'], errors='coerce', format='%d/%m/%Y')  
    if 'Valor' in data.columns:
        data['Valor'] = pd.to_numeric(data['Valor'], errors='coerce')  # Garante que 'Valor' seja numérico
    return data

# Função de login
def login():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")

    if login_button:
        if check_login(username, password):
            st.session_state['logged_in'] = True
            st.success("Login bem-sucedido!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos!")

# Verifica se o usuário está logado
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    # Usar o caminho correto do arquivo no seu sistema
    data_file = 'clientes.csv'  # Caminho correto do arquivo enviado
    data = load_data(data_file)

    # Título e descrição
    st.title("Dashboard Financeiro 📊")
    st.write("Este dashboard exibe uma análise financeira baseada nos dados de faturamento.")

    # Verificar se as colunas necessárias existem
    if 'Valor' in data.columns and 'Pagamento' in data.columns and 'DT_contrato' in data.columns:
        
        # **Seleção de Período**
        st.subheader("Selecione o período de análise")
        
        # Garantir que as datas estejam no formato DD/MM/YYYY
        min_date = data['DT_contrato'].min().strftime('%d/%m/%Y')
        max_date = datetime.now().strftime('%d/%m/%Y')
        
        # Selecionar a data inicial e final
        start_date = st.date_input("Data de início (DD/MM/YYYY)", value=data['DT_contrato'].min(), 
                                   min_value=data['DT_contrato'].min(), max_value=datetime.now(), 
                                   format="DD/MM/YYYY")
        
        end_date = st.date_input("Data de término (DD/MM/YYYY)", value=datetime.now(), 
                                 min_value=start_date, max_value=datetime.now(), format="DD/MM/YYYY")

        # Filtrar os dados pelo intervalo de datas selecionado
        filtered_data = data[(data['DT_contrato'] >= pd.to_datetime(start_date)) & (data['DT_contrato'] <= pd.to_datetime(end_date))]

        if filtered_data.empty:
            st.warning("Não há dados para o período selecionado.")
        else:
            # Adicionar uma coluna 'Mes_Ano' para facilitar o agrupamento por mês
            filtered_data['Mes_Ano'] = filtered_data['DT_contrato'].dt.to_period('M')

            # Agrupamento por forma de pagamento e mês
            pagamentos_dinheiro = filtered_data[filtered_data['Pagamento'] == 'DINHEIRO'].groupby('Mes_Ano')['Valor'].sum().reset_index()
            pagamentos_pix = filtered_data[filtered_data['Pagamento'] == 'PIX'].groupby('Mes_Ano')['Valor'].sum().reset_index()
            pagamentos_cartao = filtered_data[filtered_data['Pagamento'] == 'CARTAO'].groupby('Mes_Ano')['Valor'].sum().reset_index()

            # Total de pagamentos (independente da forma de pagamento)
            total_pagamentos = filtered_data.groupby('Mes_Ano')['Valor'].sum().reset_index()

        # Menu de navegação
        section = st.sidebar.selectbox("Selecione a Seção", ["Faturamento", "Análise de Dados", "Relatórios Financeiros"])

        # Seção de Faturamento
        if section == "Faturamento":
            st.header("Faturamento")
            st.write("Visualize e analise os dados de todos os clientes cadastrados.")
            
            # Exibição da Tabela de Dados
            st.dataframe(filtered_data)

            # Gráfico de Faturamento ao longo do tempo com 3 linhas
            if 'DT_contrato' in data.columns and 'Valor' in data.columns:
                fig = px.line()

                # Adicionar os três tipos de pagamentos no gráfico
                fig.add_scatter(x=pagamentos_dinheiro['Mes_Ano'].astype(str), y=pagamentos_dinheiro['Valor'], mode='lines', name='Dinheiro')
                fig.add_scatter(x=pagamentos_pix['Mes_Ano'].astype(str), y=pagamentos_pix['Valor'], mode='lines', name='Pix')
                fig.add_scatter(x=pagamentos_cartao['Mes_Ano'].astype(str), y=pagamentos_cartao['Valor'], mode='lines', name='Cartão')

                # Adicionar o total de todos os pagamentos
                fig.add_scatter(x=total_pagamentos['Mes_Ano'].astype(str), y=total_pagamentos['Valor'], mode='lines', name='Total')

                # Personalizar layout em português com as datas no formato DD/MM/YYYY
                fig.update_layout(
                    title=f'Faturamento de {start_date.strftime("%d/%m/%Y")} até {end_date.strftime("%d/%m/%Y")} (Por Tipo de Pagamento)',
                    xaxis_title='Mês/Ano',
                    yaxis_title='Valor (R$)',
                    legend_title_text='Forma de Pagamento'
                )

                # Formatar as datas no eixo X como DD/MM/YYYY
                fig.update_xaxes(tickformat="%d/%m/%Y")

                # Exibir o gráfico
                st.plotly_chart(fig)
            else:
                st.error("Colunas 'DT_contrato' ou 'Valor' estão ausentes.")

        # Seção de Análise de Dados
        elif section == "Análise de Dados" and 'Valor' in filtered_data.columns:
            st.header("Análise de Dados")
            st.write("KPIs e análises detalhadas dos dados financeiros.")
            
            # Verifique se a coluna 'Status' está presente
            if 'Status' in filtered_data.columns:
                # Separar os valores com status 'Negado' e 'Deferido'
                prejuizo = filtered_data[filtered_data['Status'] == 'NEGADO']['Valor'].sum()
                receita_deferido = filtered_data[filtered_data['Status'] == 'DEFERIDO']['Valor'].sum()
                
                # Subtrair o prejuízo do total
                receita_total = filtered_data['Valor'].sum() - prejuizo
                receita_media = filtered_data['Valor'].mean()
                
                if filtered_data['Valor'].iloc[0] != 0:  # Evitar divisão por zero
                    crescimento = (filtered_data['Valor'].iloc[-1] - filtered_data['Valor'].iloc[0]) / filtered_data['Valor'].iloc[0] * 100
                else:
                    crescimento = 0

                st.metric(label="Receita Total", value=f"R$ {receita_total:,.2f}")
                st.metric(label="Receita Média por Transação", value=f"R$ {receita_media:,.2f}")
                st.metric(label="Crescimento", value=f"{crescimento:.2f}%")
                st.metric(label="Prejuízo Total (Negado)", value=f"R$ {prejuizo:,.2f}")

                # Gráfico de Status (DEFERIDO vs NEGADO)
                status_data = filtered_data[filtered_data['Status'].isin(['DEFERIDO', 'NEGADO'])]  # Filtra os status relevantes
                
                # Definir as cores para cada status
                fig_status = px.bar(
                    status_data, 
                    x='Status', 
                    y='Valor', 
                    color='Status', 
                    title='Valores por Status (DEFERIDO e NEGADO)',
                    color_discrete_map={
                        'DEFERIDO': 'green',  # Deferido será verde
                        'NEGADO': 'red'       # Negado será vermelho
                    }
                )

                st.plotly_chart(fig_status)

            else:
                st.error("A coluna 'Status' está ausente no arquivo CSV.")

        # Seção de Relatórios Financeiros
        elif section == "Relatórios Financeiros" and 'Valor' in filtered_data.columns:
            st.header("Relatórios Financeiros")
            st.write("Gere e exporte relatórios financeiros resumidos.")
            
            # Distribuição de Receita por Tipo de Processo
            resumo = filtered_data.groupby('Tipo_de_Processo').agg({'Valor': 'sum'}).reset_index()
            
            # Definindo cores personalizadas para cada tipo de processo
            fig_bar = px.bar(
                resumo, 
                x='Tipo_de_Processo', 
                y='Valor', 
                title='Distribuição de Receita por Tipo de Processo',
                color='Tipo_de_Processo',  # Colorir de acordo com o tipo de processo
                color_discrete_map={
                    'JARI': 'black',    # JARI será azul
                    'CETRAN': 'yellow',
                    'DEFESA PRÉVIA': 'green'    # CETRAN será vermelho
                }
            )
            
            st.plotly_chart(fig_bar)

            # Exportação de Relatórios
            if st.button('Exportar para Excel'):
                resumo.to_excel('relatorio_financeiro.xlsx', index=False)
                st.success('Relatório exportado com sucesso!')
    else:
        st.error("As colunas 'Valor', 'Pagamento' ou 'DT_contrato' estão ausentes no arquivo CSV.")





















