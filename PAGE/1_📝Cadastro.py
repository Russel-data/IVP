
import streamlit as st
from datetime import date

# Dados de login: usuários e senhas
users = {
    "admin": "admin123",
    "user1": "mypassword",
    "user2": "streamlit"
}

# Função de autenticação
def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False

# Interface de login
def login():
    st.title("Área Restrita - Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")

    if login_button:
        if authenticate(username, password):
            st.session_state['authenticated'] = True
            st.success("Login bem-sucedido!")
        else:
            st.error("Usuário ou senha incorretos!")

# Verifica se o usuário está autenticado
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Função para validar e formatar datas no formato DD/MM/YYYY
def formatar_data(data):
    if isinstance(data, date):
        return data.strftime('%d/%m/%Y')
    return ""

if not st.session_state['authenticated']:
    login()
else:
    # Função para gravar os dados
    def gravar_dados(nome, telefone, cpf, cnpj, dt_contrato, tipo, orgao, auto, processo_nb, pagamento, valor, dt_entrada_ct, dt_efeito_sup):
        if nome and dt_contrato:
            # Gravando no arquivo CSV com datas formatadas
            with open("clientes.csv", "a", encoding="utf-8") as file:
                file.write(f"{nome},{telefone},{cpf},{cnpj},{formatar_data(dt_contrato)},{tipo},{orgao},{auto},{processo_nb},{pagamento},{valor},{formatar_data(dt_entrada_ct)},{formatar_data(dt_efeito_sup)}")
            st.session_state["Sucesso"] = True
        else:
            st.session_state["Sucesso"] = False

    # Configuração da página
    st.set_page_config(
        page_title="Cadastro de Clientes",
        page_icon="🧾"
    )

    st.title("Cadastro de Cliente")
    st.divider()

    # Formulário de cadastro
    nome = st.text_input("Digite o nome do cliente", key="nome_cliente")
    telefone = st.text_input("Telefone:", key="telefone")
    cpf = st.text_input("Digite o CPF:", key="cpf")
    cnpj = st.text_input("Digite o CNPJ:", key="cnpj")
    
    # Permitir que o usuário selecione a data desejada
    dt_contrato = st.date_input("Data do contrato", value=date.today(), format="DD/MM/YYYY")
    
    tipo = st.selectbox("Tipo de Processo", ["JARI", "CETRAN", "DEFESA PRÉVIA"])
    orgao = st.selectbox("Orgão", ["DNIT", "GOINFRA", "SMM", "DETRAN", "PRF"])
    auto = st.text_input("Digite a auto infração:", key="auto_infracao")
    processo_nb = st.text_input("Número do Processo:", key="numero_processo")
    pagamento = st.selectbox("Tipo de pagamento", ["DINHEIRO", "CARTAO", "PIX"])
    valor = st.number_input("Valor", key="valor_do_serviço")
    dt_entrada_ct = st.date_input("Data da entrada do processo", value=date.today(), format="DD/MM/YYYY")
    dt_efeito_sup = st.date_input("Data do efeito suspensivo", value=date.today(), format="DD/MM/YYYY")

    # Botão de cadastro
    btn_cadastrar = st.button("Cadastrar", on_click=gravar_dados, args=[nome, telefone, cpf, cnpj, dt_contrato, tipo, orgao, auto, processo_nb, pagamento, valor, dt_entrada_ct, dt_efeito_sup])

    if btn_cadastrar:
        if st.session_state["Sucesso"]:
            st.success("Cliente cadastrado com sucesso", icon="✅")
        else:
            st.error("Houve algum problema no cadastro", icon="❌")

    # Botão de logout
    if st.button("Sair"):
        st.session_state['authenticated'] = False
        st.experimental_rerun()
