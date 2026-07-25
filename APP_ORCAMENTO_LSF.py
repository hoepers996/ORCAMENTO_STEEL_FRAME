
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.units import inch
import io

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="GERADOR DE ORÇAMENTOS LSF", page_icon="🏗️", layout="centered")

st.title("🏗️ GERADOR DE ORÇAMENTOS - STEEL FRAME")
st.subheader("SISTEMA DE ESTIMATIVA PARAMÉTRICA AUTOMATIZADA V2.0")

st.markdown("---")

# FORMULÁRIO DE ENTRADA
with st.form("form_orcamento"):
    st.write("### 📝 DADOS DA OBRA E CLIENTE")
    cliente = st.text_input("NOME DO CLIENTE / PROJETO:", value="RESIDENCIAL SILVA")
    local = st.text_input("LOCAL DA OBRA (CIDADE / UF):", value="JOINVILLE / SC")
    area_m2 = st.number_input("ÁREA TOTAL CONSTRUÍDA (M²):", min_value=10.0, max_value=5000.0, value=250.0, step=10.0)
    padrao = st.selectbox("PADRÃO DE ACABAMENTO:", ["BAIXO", "MÉDIO", "ALTO"], index=1)
    bdi = st.slider("PERCENTUAL DE BDI / MARGEM (%):", min_value=10, max_value=35, value=20) / 100.0
    
    submitted = st.form_submit_button("🚀 GERAR PROPOSTA E CALCULAR")

if submitted:
    st.success("✅ PROPOSTA PROCESSADA COM SUCESSO!")
    
    # BASE DE DADOS PARAMÉTRICA
    data = [
        {"SUBSISTEMA": "INFRAESTRUTURA (RADIER E IMPERMEABILIZAÇÃO)", "CONSUMO_M2": 1.00, "CUSTO_UNIT_RS": 300.00},
        {"SUBSISTEMA": "ESTRUTURA LSF (PERFIS GALVANIZADOS)", "CONSUMO_M2": 30.00, "CUSTO_UNIT_RS": 11.00},
        {"SUBSISTEMA": "FECHAMENTO EXTERNO (SISTEMA EIFS)", "CONSUMO_M2": 1.20, "CUSTO_UNIT_RS": 120.00},
        {"SUBSISTEMA": "ISOLAMENTO TERMOACÚSTICO", "CONSUMO_M2": 1.50, "CUSTO_UNIT_RS": 25.00},
        {"SUBSISTEMA": "FECHAMENTO INTERNO (DRYWALL)", "CONSUMO_M2": 2.20, "CUSTO_UNIT_RS": 35.00},
        {"SUBSISTEMA": "COBERTURA (ESTRUTURA E TELHA)", "CONSUMO_M2": 1.10, "CUSTO_UNIT_RS": 150.00},
        {"SUBSISTEMA": "INSTALAÇÕES PREDIAS (PEX/PPR E ELÉTRICA)", "CONSUMO_M2": 1.00, "CUSTO_UNIT_RS": 375.00},
        {"SUBSISTEMA": "ACABAMENTOS (PINTURA, REVEST. E LOUÇAS)", "CONSUMO_M2": 1.00, "CUSTO_UNIT_RS": 450.00}
    ]
    df = pd.DataFrame(data)
    
    # AJUSTE DE PADRÃO
    fator_padrao = 0.85 if padrao == "BAIXO" else (1.00 if padrao == "MÉDIO" else 1.30)
    df["CUSTO_UNIT_RS"] = df["CUSTO_UNIT_RS"] * fator_padrao
    
    # CÁLCULOS
    df["CUSTO_DIRETO_TOTAL"] = df["CONSUMO_M2"] * df["CUSTO_UNIT_RS"] * area_m2
    df["CUSTO_FINAL_COM_BDI"] = df["CUSTO_DIRETO_TOTAL"] * (1 + bdi)
    df["PARTICIPACAO_PCT"] = (df["CUSTO_DIRETO_TOTAL"] / df["CUSTO_DIRETO_TOTAL"].sum()) * 100
    
    valor_total = df["CUSTO_FINAL_COM_BDI"].sum()
    valor_m2 = valor_total / area_m2
    
    # EXIBIÇÃO NA TELA
    col1, col2 = st.columns(2)
    col1.metric("VALOR TOTAL ESTIMADO", f"R$ {valor_total:,.2f}")
    col2.metric("VALOR POR M²", f"R$ {valor_m2:,.2f} / m²")
    
    st.markdown("### 📊 DETALHAMENTO DOS SUBSISTEMAS")
    st.dataframe(df[["SUBSISTEMA", "CUSTO_FINAL_COM_BDI", "PARTICIPACAO_PCT"]].rename(columns={
        "SUBSISTEMA": "Subsistema",
        "CUSTO_FINAL_COM_BDI": "Valor com BDI (R$)",
        "PARTICIPACAO_PCT": "Part. (%)"
    }))
