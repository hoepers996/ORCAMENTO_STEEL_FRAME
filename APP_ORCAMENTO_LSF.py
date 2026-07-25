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
st.set_page_config(page_title="GERADOR DE ORÇAMENTOS LSF V1.6", page_icon="🏗️", layout="centered")

st.title("🏗️ GERADOR DE ORÇAMENTOS - STEEL FRAME")
st.subheader("ESTIMATIVA PARAMÉTRICA DETALHADA V1.6 (MAT/MO SEPARADOS)")

st.markdown("---")

# 2. CARREGAR DADOS DO GOOGLE SHEETS COM BACKUP DUAL
@st.cache_data(ttl=60)
def carregar_dados_google_sheets():
    sheet_url = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv"
    try:
        df = pd.read_csv(sheet_url)
        if len(df) >= 10 and "CUSTO_MAT_UNIT_RS" in df.columns:
            return df
        else:
            raise ValueError("Colunas desatualizadas na planilha.")
    except Exception as e:
        data_backup = [
            {"SUBSISTEMA": "01. SERVIÇOS PRELIMINARES", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 5.00, "CUSTO_MO_UNIT_RS": 20.00},
            {"SUBSISTEMA": "02. GESTÃO DE OBRA E ADM", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 10.00, "CUSTO_MO_UNIT_RS": 110.00},
            {"SUBSISTEMA": "03. INSTALAÇÕES DO CANTEIRO", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 15.00, "CUSTO_MO_UNIT_RS": 15.00},
            {"SUBSISTEMA": "04. LOCAÇÕES E EQUIPAMENTOS", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 12.00, "CUSTO_MO_UNIT_RS": 8.00},
            {"SUBSISTEMA": "05. INFRAESTRUTURA (FUNDAÇÃO)", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 180.00, "CUSTO_MO_UNIT_RS": 100.00},
            {"SUBSISTEMA": "06. SUPERESTRUTURA LSF", "CONSUMO_MEDIO_M2": 30.00, "CUSTO_MAT_UNIT_RS": 7.50, "CUSTO_MO_UNIT_RS": 3.50},
            {"SUBSISTEMA": "07. FECHAMENTOS (EXT/INT)", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 140.00, "CUSTO_MO_UNIT_RS": 80.00},
            {"SUBSISTEMA": "08. COBERTURA E TELHADO", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 110.00, "CUSTO_MO_UNIT_RS": 50.00},
            {"SUBSISTEMA": "09. IMPERMEABILIZAÇÕES", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 20.00, "CUSTO_MO_UNIT_RS": 15.00},
            {"SUBSISTEMA": "10. INSTALAÇÕES HIDRÁULICAS", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 65.00, "CUSTO_MO_UNIT_RS": 45.00},
            {"SUBSISTEMA": "11. INSTALAÇÕES ELÉTRICAS", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 75.00, "CUSTO_MO_UNIT_RS": 55.00},
            {"SUBSISTEMA": "12. CLIMATIZAÇÃO E EXAUSTÃO", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 45.00, "CUSTO_MO_UNIT_RS": 30.00},
            {"SUBSISTEMA": "13. REVESTIMENTOS", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 70.00, "CUSTO_MO_UNIT_RS": 70.00},
            {"SUBSISTEMA": "14. PISOS E PAVIMENTAÇÕES", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 70.00, "CUSTO_MO_UNIT_RS": 50.00},
            {"SUBSISTEMA": "15. ESQUADRIAS E VIDROS", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 130.00, "CUSTO_MO_UNIT_RS": 50.00},
            {"SUBSISTEMA": "16. URBANIZAÇÃO E EXTERNOS", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 30.00, "CUSTO_MO_UNIT_RS": 20.00},
            {"SUBSISTEMA": "17. LIMPEZA FINAL DA OBRA", "CONSUMO_MEDIO_M2": 1.00, "CUSTO_MAT_UNIT_RS": 3.00, "CUSTO_MO_UNIT_RS": 12.00}
        ]
        return pd.DataFrame(data_backup)

# 3. GERADOR DE PDF FLEXÍVEL
def gerar_pdf_bytes(cliente, local, area_m2, area_fundacao_m2, tipo_fundacao, padrao, bdi, df, valor_total, valor_m2, exibir_separado):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    
    # GRÁFICO
    fig, ax = plt.subplots(figsize=(7, 3.8))
    sub_names = [str(x)[:22] for x in df["SUBSISTEMA"].tolist()]
    values = df["PARTICIPACAO_PCT"].tolist()
    
    ax.barh(sub_names[::-1], values[::-1], color='#2B6CB0')
    ax.set_xlabel('Participação (%)', fontsize=8, fontweight='bold')
    ax.set_title('DISTRIBUIÇÃO DE CUSTOS POR SUBSISTEMA (%)', fontsize=10, fontweight='bold')
    plt.tight_layout()
    
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=200)
    plt.close(fig)
    chart_buffer.seek(0)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#1A365D'), spaceAfter=8)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#4A5568'), spaceAfter=12)
    section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#2C5282'), spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#2D3748'))
    
    elements = []
    elements.append(Paragraph("PROPOSTA COMERCIAL PRELIMINAR — LIGHT STEEL FRAME", title_style))
    elements.append(Paragraph("SISTEMA DE ENGENHARIA E ORÇAMENTAÇÃO AUTOMATIZADA (V1.6)", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=12))
    
    dados_cliente = [
        [Paragraph(f"<b>CLIENTE:</b> {cliente}", body_style), Paragraph(f"<b>LOCAL:</b> {local}", body_style)],
        [Paragraph(f"<b>ÁREA CONSTRUÍDA TOTAL:</b> {area_m2:,.2f} M²", body_style), Paragraph(f"<b>ÁREA FUNDAÇÃO:</b> {area_fundacao_m2:,.2f} M² ({tipo_fundacao})", body_style)],
        [Paragraph(f"<b>PADRÃO ACABAMENTO:</b> {padrao}", body_style), Paragraph("<b>SISTEMA:</b> LIGHT STEEL FRAME (LSF)", body_style)]
    ]
    t_cliente = Table(dados_cliente, colWidths=[270, 270])
    t_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF2F7')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#CBD5E0')),
    ]))
    elements.append(t_cliente)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("1. RESUMO EXECUTIVO DO ORÇAMENTO", section_style))
    
    tot_mat = df["CUSTO_MAT_FINAL"].sum()
    tot_mo = df["CUSTO_MO_FINAL"].sum()
    
    resumo_data = [
        [Paragraph("<b>VALOR TOTAL ESTIMADO:</b>", body_style), Paragraph(f"<b>R$ {valor_total:,.2f}</b>", body_style)],
        [Paragraph("<b>VALOR ESTIMADO POR M² CONSTRUÍDO:</b>", body_style), Paragraph(f"<b>R$ {valor_m2:,.2f} / M²</b>", body_style)]
    ]
    if exibir_separado:
        resumo_data.append([Paragraph("<b>TOTAL MATERIAIS COM BDI:</b>", body_style), Paragraph(f"R$ {tot_mat:,.2f} ({ (tot_mat/valor_total)*100:.1f}%)", body_style)])
        resumo_data.append([Paragraph("<b>TOTAL MÃO DE OBRA COM BDI:</b>", body_style), Paragraph(f"R$ {tot_mo:,.2f} ({ (tot_mo/valor_total)*100:.1f}%)", body_style)])

    t_resumo = Table(resumo_data, colWidths=[200, 340])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#2B6CB0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor('#3182CE')),
    ]))
    elements.append(t_resumo)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("2. DETALHAMENTO POR SUBSISTEMA CONSTRUTIVO (EAP)", section_style))
    
    if exibir_separado:
        data_table = [[
            Paragraph("<b>SUBSISTEMA</b>", body_style), 
            Paragraph("<b>MATERIAL (R$)</b>", body_style), 
            Paragraph("<b>MÃO DE OBRA (R$)</b>", body_style), 
            Paragraph("<b>TOTAL (R$)</b>", body_style), 
            Paragraph("<b>PART. (%)</b>", body_style)
        ]]
        for idx, row in df.iterrows():
            data_table.append([
                Paragraph(str(row["SUBSISTEMA"]), body_style),
                f"R$ {row['CUSTO_MAT_FINAL']:,.2f}",
                f"R$ {row['CUSTO_MO_FINAL']:,.2f}",
                f"R$ {row['CUSTO_FINAL_COM_BDI']:,.2f}",
                f"{row['PARTICIPACAO_PCT']:.1f}%"
            ])
        data_table.append([
            Paragraph("<b>TOTAL GERAL</b>", body_style),
            Paragraph(f"<b>R$ {tot_mat:,.2f}</b>", body_style),
            Paragraph(f"<b>R$ {tot_mo:,.2f}</b>", body_style),
            Paragraph(f"<b>R$ {valor_total:,.2f}</b>", body_style),
            Paragraph("<b>100,0%</b>", body_style)
        ])
        t_detalhes = Table(data_table, colWidths=[170, 95, 95, 105, 75])
    else:
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
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EDF2F7')),
    ]))
    elements.append(t_detalhes)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("3. VISUALIZAÇÃO DA COMPOSIÇÃO DE CUSTOS", section_style))
    elements.append(Image(chart_buffer, width=5.5*inch, height=3.0*inch))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# 4. FORMULÁRIO DE ENTRADA
with st.form("form_orcamento"):
    st.write("### 📝 DADOS GERAIS DA OBRA")
    cliente = st.text_input("NOME DO CLIENTE / PROJETO:", value="RESIDENCIAL SILVA")
    local = st.text_input("LOCAL DA OBRA (CIDADE / UF):", value="JOINVILLE / SC")
    area_m2 = st.number_input("ÁREA TOTAL CONSTRUÍDA DA OBRA (M²):", min_value=10.0, max_value=5000.0, value=500.0, step=10.0)
    padrao = st.selectbox("PADRÃO DE ACABAMENTO GERAL:", ["BAIXO", "MÉDIO", "ALTO"], index=1)
    
    st.write("### 🏗️ PARÂMETROS DA FUNDAÇÃO / INFRAESTRUTURA")
    area_fundacao_m2 = st.number_input("ÁREA DA FUNDAÇÃO / PROJEÇÃO (M²):", min_value=10.0, max_value=5000.0, value=250.0, step=10.0)
    tipo_fundacao = st.selectbox("COMPLEXIDADE DA FUNDAÇÃO:", [
        "LEVE (SOLO BOM / RADIER SIMPLES)", 
        "MODERADA (PADRÃO DE MERCADO)", 
        "PESADA (SOLO FRÁGIL / REFORÇO DE ESTACAS)"
    ], index=1)
    
    st.write("### ⚙️ FORMATO DE APRESENTAÇÃO DOS VALORES")
    opcao_exibicao = st.radio(
        "COMO DESEJA EXIBIR OS VALORES NA TELA E NO PDF?",
        ["JUNTOS (VALOR UNIFICADO)", "SEPARADOS (MATERIAL E MÃO DE OBRA)"],
        index=0
    )
    exibir_separado = (opcao_exibicao == "SEPARADOS (MATERIAL E MÃO DE OBRA)")
    
    bdi = st.slider("PERCENTUAL DE BDI / MARGEM (%):", min_value=10, max_value=35, value=20) / 100.0
    
    submitted = st.form_submit_button("🚀 CALCULAR E GERAR PROPOSTA (V1.6)")

if submitted:
    st.success("✅ CÁLCULOS EXECUTADOS NA VERSÃO 1.6!")
    
    df = carregar_dados_google_sheets()
    
    fator_padrao = 0.85 if padrao == "BAIXO" else (1.00 if padrao == "MÉDIO" else 1.30)
    fator_fundacao = 0.85 if "LEVE" in tipo_fundacao else (1.35 if "PESADA" in tipo_fundacao else 1.00)

    custos_mat = []
    custos_mo = []
    
    for idx, row in df.iterrows():
        sub = str(row["SUBSISTEMA"]).upper()
        consumo = float(row.get("CONSUMO_MEDIO_M2", 1.0))
        c_mat = float(row.get("CUSTO_MAT_UNIT_RS", 50.0))
        c_mo = float(row.get("CUSTO_MO_UNIT_RS", 50.0))
        
        if "INFRA" in sub or "FUNDAÇ" in sub or "RADIER" in sub:
            area_aplicada = area_fundacao_m2
            fator_extra = fator_fundacao
        else:
            area_aplicada = area_m2
            fator_extra = 1.00
            
        mat_item = consumo * c_mat * fator_padrao * fator_extra * area_aplicada * (1 + bdi)
        mo_item = consumo * c_mo * fator_padrao * fator_extra * area_aplicada * (1 + bdi)
        
        custos_mat.append(mat_item)
        custos_mo.append(mo_item)

    df["CUSTO_MAT_FINAL"] = custos_mat
    df["CUSTO_MO_FINAL"] = custos_mo
    df["CUSTO_FINAL_COM_BDI"] = df["CUSTO_MAT_FINAL"] + df["CUSTO_MO_FINAL"]
    df["PARTICIPACAO_PCT"] = (df["CUSTO_FINAL_COM_BDI"] / df["CUSTO_FINAL_COM_BDI"].sum()) * 100
    
    valor_total = df["CUSTO_FINAL_COM_BDI"].sum()
    valor_m2 = valor_total / area_m2
    
    tot_mat_geral = df["CUSTO_MAT_FINAL"].sum()
    tot_mo_geral = df["CUSTO_MO_FINAL"].sum()
    
    if exibir_separado:
        c1, c2, c3 = st.columns(3)
        c1.metric("VALOR TOTAL ESTIMADO", f"R$ {valor_total:,.2f}")
        c2.metric("TOTAL MATERIAIS", f"R$ {tot_mat_geral:,.2f}")
        c3.metric("TOTAL MÃO DE OBRA", f"R$ {tot_mo_geral:,.2f}")
    else:
        col1, col2 = st.columns(2)
        col1.metric("VALOR TOTAL ESTIMADO", f"R$ {valor_total:,.2f}")
        col2.metric("VALOR POR M² CONSTRUÍDO", f"R$ {valor_m2:,.2f} / m²")
    
    st.markdown("---")
    
    pdf_bytes = gerar_pdf_bytes(cliente, local, area_m2, area_fundacao_m2, tipo_fundacao.split(' ')[0], padrao, bdi, df, valor_total, valor_m2, exibir_separado)
    
    st.download_button(
        label="📥 BAIXAR PROPOSTA COMERCIAL V1.6 EM PDF",
        data=pdf_bytes,
        file_name=f"PROPOSTA_V1_6_{cliente.replace(' ', '_').upper()}.pdf",
        mime="application/pdf"
    )
