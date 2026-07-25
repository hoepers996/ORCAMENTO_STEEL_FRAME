import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.units import inch
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="GERADOR DE ORÇAMENTOS LSF", page_icon="🏗️", layout="centered")

st.title("🏗️ GERADOR DE ORÇAMENTOS - STEEL FRAME")
st.subheader("SISTEMA CONECTADO AO GOOGLE SHEETS V3.0")

st.markdown("---")

# 2. FUNÇÃO PARA LER OS DADOS DIRETO DA SUA PLANILHA NO GOOGLE DRIVE
@st.cache_data(ttl=60)  # ATUALIZA A CADA 60 SEGUNDOS
def carregar_dados_google_sheets():
    # LINK DE EXPORTAÇÃO CSV DA SUA PLANILHA
    sheet_url = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv"
    try:
        df = pd.read_csv(sheet_url)
        return df
    except Exception as e:
        # BASE DE BACKUP CASO A INTERNET DA PLANILHA FALHE
        data_backup = [
            {"SUBSISTEMA": "INFRAESTRUTURA", "DESCRICAO_DO_ITEM": "RADIER OTIMIZADO E IMPERMEABILIZACAO", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_UNITARIO_REF_RS": 300.00},
            {"SUBSISTEMA": "ESTRUTURA_LSF", "DESCRICAO_DO_ITEM": "PERFIS GALVANIZADOS ENGENHERADOS", "CONSUMO_MEDIO_M2": 30.00, "CUSTO_UNITARIO_REF_RS": 11.00},
            {"SUBSISTEMA": "FECHAMENTO_EXTERNO", "DESCRICAO_DO_ITEM": "SISTEMA EIFS (MEMBRANA EPS BASECOAT)", "CONSUMO_MEDIO_M2": 1.20, "CUSTO_UNITARIO_REF_RS": 120.00},
            {"SUBSISTEMA": "ISOLAMENTO", "DESCRICAO_DO_ITEM": "LA DE ROCHA OU LA DE VIDRO 50MM", "CONSUMO_MEDIO_M2": 1.50, "CUSTO_UNITARIO_REF_RS": 25.00},
            {"SUBSISTEMA": "FECHAMENTO_INTERNO", "DESCRICAO_DO_ITEM": "CHAPAS DE DRYWALL ST/RU E PARAFUSOS", "CONSUMO_MEDIO_M2": 2.20, "CUSTO_UNITARIO_REF_RS": 35.00},
            {"SUBSISTEMA": "COBERTURA", "DESCRICAO_DO_ITEM": "ESTRUTURA DE TELHADO LSF E TELHA TERMOACUSTICA", "CONSUMO_MEDIO_M2": 1.10, "CUSTO_UNITARIO_REF_RS": 150.00},
            {"SUBSISTEMA": "INSTALACOES", "DESCRICAO_DO_ITEM": "KITS DE INSTALACOES PEX/PPR E ELETRICA PRE-FURADA", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_UNITARIO_REF_RS": 375.00},
            {"SUBSISTEMA": "ACABAMENTOS", "DESCRICAO_DO_ITEM": "PINTURA REVESTIMENTOS E LOUCAS", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_UNITARIO_REF_RS": 450.00}
        ]
        return pd.DataFrame(data_backup)

# 3. FUNÇÃO PARA GERAR O PDF NA MEMÓRIA
def gerar_pdf_bytes(cliente, local, area_m2, padrao, bdi, df, valor_total, valor_m2):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    
    # GERAR GRÁFICO
    fig, ax = plt.subplots(figsize=(6, 3))
    labels = ['INFRA', 'ESTRUTURA LSF', 'FECH. EXT.', 'ISOLAMENTO', 'FECH. INT.', 'COBERTURA', 'INSTALAÇÕES', 'ACABAMENTOS']
    sizes = df["PARTICIPACAO_PCT"].tolist()
    colors_list = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors_list, textprops={'fontsize': 8})
    ax.set_title('DISTRIBUIÇÃO DE CUSTOS POR SUBSISTEMA', fontsize=10, fontweight='bold')
    plt.tight_layout()
    
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=200)
    plt.close(fig)
    chart_buffer.seek(0)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#1A365D'), spaceAfter=10)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#4A5568'), spaceAfter=15)
    section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#2C5282'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#2D3748'))
    
    elements = []
    elements.append(Paragraph("PROPOSTA COMERCIAL PRELIMINAR — LIGHT STEEL FRAME", title_style))
    elements.append(Paragraph("SISTEMA DE ENGENHARIA E ORÇAMENTAÇÃO AUTOMATIZADA", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2B6CB0'), spaceAfter=15))
    
    dados_cliente = [
        [Paragraph(f"<b>CLIENTE:</b> {cliente}", body_style), Paragraph(f"<b>LOCAL:</b> {local}", body_style)],
        [Paragraph(f"<b>ÁREA CONSTRUÍDA:</b> {area_m2:,.2f} M²", body_style), Paragraph("<b>SISTEMA:</b> LIGHT STEEL FRAME (LSF)", body_style)],
        [Paragraph(f"<b>PADRÃO DE ACABAMENTO:</b> {padrao}", body_style), Paragraph("<b>PRAZO ESTIMADO:</b> 4 A 5 MESES", body_style)]
    ]
    t_cliente = Table(dados_cliente, colWidths=[270, 270])
    t_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF2F7')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
    ]))
    elements.append(t_cliente)
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("1. RESUMO EXECUTIVO DO ORÇAMENTO", section_style))
    resumo_data = [
        [Paragraph("<b>VALOR TOTAL ESTIMADO:</b>", body_style), Paragraph(f"<b>R$ {valor_total:,.2f}</b>", body_style)],
        [Paragraph("<b>VALOR ESTIMADO POR M²:</b>", body_style), Paragraph(f"<b>R$ {valor_m2:,.2f} / M²</b>", body_style)]
    ]
    t_resumo = Table(resumo_data, colWidths=[200, 340])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#2B6CB0')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#3182CE')),
    ]))
    elements.append(t_resumo)
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("2. DETALHAMENTO POR SUBSISTEMA CONSTRUTIVO", section_style))
    data_table = [[Paragraph("<b>SUBSISTEMA</b>", body_style), Paragraph("<b>VALOR COM BDI (R$)</b>", body_style), Paragraph("<b>PART. (%)</b>", body_style)]]
    
    for idx, row in df.iterrows():
        data_table.append([
            Paragraph(str(row["SUBSISTEMA"]), body_style),
            f"R$ {row['CUSTO_FINAL_COM_BDI']:,.2f}",
            f"{row['PARTICIPACAO_PCT']:.1f}%"
        ])
    data_table.append([
        Paragraph("<b>TOTAL GERAL</b>", body_style),
        Paragraph(f"<b>R$ {valor_total:,.2f}</b>", body_style),
        Paragraph("<b>100,0%</b>", body_style)
    ])
    
    t_detalhes = Table(data_table, colWidths=[280, 150, 110])
    t_detalhes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EDF2F7')),
    ]))
    elements.append(t_detalhes)
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("3. VISUALIZAÇÃO DA COMPOSIÇÃO DE CUSTOS", section_style))
    elements.append(Image(chart_buffer, width=5.5*inch, height=2.75*inch))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# 4. FORMULÁRIO INTERATIVO NO STREAMLIT
with st.form("form_orcamento"):
    st.write("### 📝 DADOS DA OBRA E CLIENTE")
    cliente = st.text_input("NOME DO CLIENTE / PROJETO:", value="RESIDENCIAL SILVA")
    local = st.text_input("LOCAL DA OBRA (CIDADE / UF):", value="JOINVILLE / SC")
    area_m2 = st.number_input("ÁREA TOTAL CONSTRUÍDA (M²):", min_value=10.0, max_value=5000.0, value=250.0, step=10.0)
    padrao = st.selectbox("PADRÃO DE ACABAMENTO:", ["BAIXO", "MÉDIO", "ALTO"], index=1)
    bdi = st.slider("PERCENTUAL DE BDI / MARGEM (%):", min_value=10, max_value=35, value=20) / 100.0
    
    submitted = st.form_submit_button("🚀 CALCULAR E GERAR PROPOSTA")

if submitted:
    st.success("✅ CÁLCULOS REALIZADOS COM SUCESSO!")
    
    # CARREGAR DADOS DA PLANILHA GOOGLE
    df = carregar_dados_google_sheets()
    
    # AJUSTE CONFORME PADRÃO
    fator_padrao = 0.85 if padrao == "BAIXO" else (1.00 if padrao == "MÉDIO" else 1.30)
    
    # PROCESSAMENTO DE CUSTOS
    df["CUSTO_DIRETO_TOTAL"] = df["CONSUMO_MEDIO_M2"] * df["CUSTO_UNITARIO_REF_RS"] * fator_padrao * area_m2
    df["CUSTO_FINAL_COM_BDI"] = df["CUSTO_DIRETO_TOTAL"] * (1 + bdi)
    df["PARTICIPACAO_PCT"] = (df["CUSTO_DIRETO_TOTAL"] / df["CUSTO_DIRETO_TOTAL"].sum()) * 100
    
    valor_total = df["CUSTO_FINAL_COM_BDI"].sum()
    valor_m2 = valor_total / area_m2
    
    # RESUMO FINANCEIRO NA TELA
    col1, col2 = st.columns(2)
    col1.metric("VALOR TOTAL ESTIMADO", f"R$ {valor_total:,.2f}")
    col2.metric("VALOR POR M²", f"R$ {valor_m2:,.2f} / m²")
    
    st.markdown("---")
    
    # GERAÇÃO DO ARQUIVO PDF
    pdf_bytes = gerar_pdf_bytes(cliente, local, area_m2, padrao, bdi, df, valor_total, valor_m2)
    
    # BOTÃO DE DOWNLOAD DO PDF
    st.download_button(
        label="📥 BAIXAR PROPOSTA COMERCIAL EM PDF",
        data=pdf_bytes,
        file_name=f"PROPOSTA_{cliente.replace(' ', '_').upper()}.pdf",
        mime="application/pdf"
    )
