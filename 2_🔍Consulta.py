import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Consulta cadastro", page_icon="🔍")

# Definindo o usuário e senha para a área restrita
USERNAME = "admin"
PASSWORD = "admin123"

# Função para verificar login
def check_login(username, password):
    return username == USERNAME and password == PASSWORD

# Página de login
def login():
    st.title("Área Restrita - Login")
    st.text_input("Usuário", key="username")
    st.text_input("Senha", type="password", key="password")
    if st.button("Entrar"):
        if check_login(st.session_state.username, st.session_state.password):
            st.session_state.logged_in = True
            st.success("Login realizado com sucesso!", icon="✅")
        else:
            st.error("Usuário ou senha incorretos", icon="❌")

# Função para calcular o prazo com base na data atual
def calcular_prazo(row):
    if row['Status'] in ["DEFERIDO", "NEGADO"]:
        return "Não há Prazo"  # Para Deferido e NEGADO, não conta prazo

    try:
        if pd.notnull(row['DT_Efeito_Susp']):
            data_suspensao = pd.to_datetime(row['DT_Efeito_Susp'], dayfirst=True)
            data_atual = datetime.now()
            prazo = (data_suspensao - data_atual).days
            if prazo < 0:
                return f"Vencido há {-prazo} dias"
            else:
                return f"Faltam {prazo} dias"
        return "Datas ausentes"
    except:
        return "Erro no cálculo"

# Funções de formatação
def formatar_telefone(telefone):
    telefone = str(telefone)
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return telefone

def formatar_cpf(cpf):
    cpf = str(cpf).zfill(11)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def formatar_cnpj(cnpj):
    cnpj = str(cnpj).zfill(14)
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

def formatar_valor(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return valor

# Verifica se o usuário está logado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    # Carrega os dados do CSV
    try:
        dados = pd.read_csv("clientes.csv")
    except FileNotFoundError:
        st.error("O arquivo 'clientes.csv' não foi encontrado.")
        dados = pd.DataFrame()

    # Garantir que a coluna Status seja tratada como string
    if 'Status' in dados.columns:
        dados['Status'] = dados['Status'].astype(str)

    # Criar uma cópia para exibir com formatações
    dados_formatados = dados.copy()

    # Aplicar formatação específica
    if 'Telefone' in dados_formatados.columns:
        dados_formatados['Telefone'] = dados_formatados['Telefone'].apply(formatar_telefone)

    if 'CPF' in dados_formatados.columns:
        dados_formatados['CPF'] = dados_formatados['CPF'].apply(formatar_cpf)

    if 'CNPJ' in dados_formatados.columns:
        dados_formatados['CNPJ'] = dados_formatados['CNPJ'].apply(formatar_cnpj)

    if 'Valor' in dados_formatados.columns:
        dados_formatados['Valor'] = dados_formatados['Valor'].apply(formatar_valor)

    campos_para_datas = ['DT_contrato', 'DT_Entrada_CT', 'DT_Efeito_Susp']
    for campo in campos_para_datas:
        if campo in dados_formatados.columns:
            dados_formatados[campo] = pd.to_datetime(dados_formatados[campo], errors='coerce').apply(
                lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else ''
            )

    if 'DT_Efeito_Susp' in dados.columns:
        # Calcular o prazo apenas para os registros que não são Deferido ou Indeferido
        dados_formatados['prazo'] = dados.apply(calcular_prazo, axis=1)

    st.title("Clientes cadastrados")
    st.divider()

    # Quantidade de prazos vencidos
    vencidos = dados_formatados[dados_formatados['prazo'].str.contains("Vencido", na=False)]
    st.subheader("Análise de Prazos Vencidos")
    st.metric(label="Total de Prazos Vencidos", value=len(vencidos))

    # Verificar se há prazos vencidos e exibir alerta
    if len(vencidos) > 0:
        st.warning(f"⚠️ Atenção! Existem {len(vencidos)} prazos vencidos. Verifique os registros.")

    # Permitir a edição da coluna Status e adicionar coluna de seleção para excluir
    if 'Status' in dados.columns:
        # Adiciona uma coluna de seleção para exclusão
        dados_formatados['Excluir'] = False

        # Exibe o DataFrame
        # Adicionei uma vírgula entre 'Tipo_de_Processo' e 'Status'
        dados_editaveis = st.data_editor(
            dados_formatados[['Nome', 'Telefone', 'CPF', 'CNPJ', 'Valor', 'Tipo_de_Processo', 'Status', 'prazo', 'Excluir']],
            num_rows="dynamic"
        )

        # Atualiza os dados de Status
        if st.button("Salvar Alterações"):
            dados['Status'] = dados_editaveis['Status']
            dados.to_csv("clientes.csv", index=False)
            st.success("Alterações salvas com sucesso!")

        # Excluir clientes marcados
        clientes_para_excluir = dados_editaveis[dados_editaveis['Excluir']].index.tolist()
        if clientes_para_excluir:
            dados = dados.drop(clientes_para_excluir)  # Excluir do DataFrame
            dados.to_csv("clientes.csv", index=False)  # Salvar as alterações
            st.success("Clientes excluídos com sucesso!")

    st.title("Localizar clientes cadastrados 🔎")
    st.divider()

    st.session_state.localizar = st.text_input("Digite o nome do cliente para localizar")
    if st.button("Pesquisar"):
        # Filtrar os dados com base na pesquisa
        dados_filtrados = dados[dados['Nome'].str.contains(st.session_state.localizar, case=False, na=False)]
        if not dados_filtrados.empty:
            # Aplicar formatações nos dados filtrados
            if 'Telefone' in dados_filtrados.columns:
                dados_filtrados['Telefone'] = dados_filtrados['Telefone'].apply(formatar_telefone)
            if 'CPF' in dados_filtrados.columns:
                dados_filtrados['CPF'] = dados_filtrados['CPF'].apply(formatar_cpf)
            if 'CNPJ' in dados_filtrados.columns:
                dados_filtrados['CNPJ'] = dados_filtrados['CNPJ'].apply(formatar_cnpj)
            if 'Valor' in dados_filtrados.columns:
                dados_filtrados['Valor'] = dados_filtrados['Valor'].apply(formatar_valor)

            for campo in campos_para_datas:
                if campo in dados_filtrados.columns:
                    dados_filtrados[campo] = pd.to_datetime(dados_filtrados[campo], errors='coerce').apply(
                        lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else ''
                    )

            st.dataframe(dados_filtrados)
        else:
            st.error("Cliente não encontrado", icon="❌")

    # Gráfico de Distribuição de Status
    st.subheader("Análise de Distribuição de Status")
    if 'Status' in dados.columns:
        status_count = dados['Status'].value_counts()
        fig_status = px.pie(status_count, values=status_count, names=status_count.index, title="Distribuição de Status dos Clientes")
        st.plotly_chart(fig_status)
    else:
        st.info("A coluna 'Status' não está disponível para análise.")

    if st.button("Sair"):
        st.session_state['logged_in'] = False
        st.experimental_rerun()












