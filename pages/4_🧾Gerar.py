import streamlit as st
from fpdf import FPDF
from datetime import datetime

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

st.set_page_config(
    page_title="Gerador de Documentos",
    page_icon="🧾"
)

# Função para gerar um PDF de recibo com papel timbrado
def gerar_recibo(nome, valor, data):
    pdf = FPDF()
    pdf.add_page()
    
    # Adiciona a imagem de fundo (papel timbrado)
    pdf.image("timbrado.jpg", x=0, y=0, w=210, h=297)
   
    # Conteúdo do recibo
    pdf.set_font("Arial", size=12)
    pdf.ln(20)
    pdf.cell(200, 30, txt="Recibo de Pagamento", ln=True, align='C')
    pdf.ln(20)
    pdf.cell(200, 20, txt=f"Recebi de {nome}", ln=True)
    pdf.cell(200, 20, txt=f"A quantia de: R$ {valor}", ln=True)
    pdf.cell(200, 20, txt=f"Em: {data}", ln=True)
    
    return pdf.output(dest='S').encode('latin1')

# Função para gerar um PDF de contrato de serviço com papel timbrado
def gerar_contrato(nome, servico, valor, data):
    pdf = FPDF()
    pdf.add_page()
    
    # Adiciona a imagem de fundo (papel timbrado)
    pdf.image("timbrado.jpg", x=0, y=0, w=210, h=297)

    # Conteúdo do contrato
    pdf.set_font("Arial", size=14)
    pdf.ln(20)
    pdf.cell(200, 30, txt="Contrato de Prestação de Serviços", ln=True, align='C')
    pdf.ln(12)
    pdf.cell(200, 12, txt=f"Contratante: {nome}", ln=True)
    
    # Use multi_cell para o campo 'Serviço' para que o texto quebre de acordo com a largura
    pdf.multi_cell(200, 12, txt=f"Serviço: {servico}", align='L')
    
    pdf.cell(200, 12, txt=f"Valor: R$ {valor}", ln=True)
    pdf.cell(200, 12, txt=f"Data: {data}", ln=True)
    pdf.cell(200, 50, txt="Assinatura", ln=True, align='C')

    return pdf.output(dest='S').encode('latin1')

# Verifica se o usuário está logado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    # Interface do usuário para gerar documentos
    st.title("Gerar Documentos 🧾")

    nome = st.text_input("Nome")
    valor = st.number_input("Valor")
    data = st.date_input("Data", format='DD/MM/YYYY')
    servico = st.text_input("Serviço", value="Descrição do serviço")

    data_formatada = data.strftime("%d/%m/%Y")

# Botão para gerar o recibo com papel timbrado
if st.button("Gerar Recibo"):
    pdf_bytes = gerar_recibo(nome, valor, data_formatada)
    st.download_button(
        label="Baixar Recibo",
        data=pdf_bytes,
        file_name=f"recibo_{nome}.pdf",  # Nome personalizado com o nome do cliente
        mime="application/pdf"
    )

# Botão para gerar o contrato de serviço com papel timbrado
if st.button("Gerar Contrato de Serviço"):
    pdf_bytes = gerar_contrato(nome, servico, valor, data_formatada)
    st.download_button(
        label="Baixar Contrato de Serviço",
        data=pdf_bytes,
        file_name=f"contrato_servico_{nome}.pdf",  # Nome personalizado com o nome do cliente
        mime="application/pdf"
    )


