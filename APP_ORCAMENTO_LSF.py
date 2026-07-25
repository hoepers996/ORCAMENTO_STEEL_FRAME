import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
from reportlab.lib.units import inch
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="GERADOR DE ORÇAMENTOS LSF V2.0", page_icon="🏗️", layout="centered")

st.title("🏗️ GERADOR DE ORÇAMENTOS - STEEL FRAME")
st.subheader("DASHBOARDS EXECUTIVOS E PROPOSTA 2 PÁGINAS V2.0")

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

# 3. GERADOR DE GRÁFICOS DASHBOARD (DONUT, GANTT E CURVA S)
def gerar_graficos_dashboard(df, valor_total, prazo_meses=6):
    macro_map = {
        '01': '1. Gestão e Canteiro',
        '02': '1. Gestão e Canteiro',
        '03': '1. Gestão e Canteiro',
        '04': '1. Gestão e Canteiro',
        '05': '2. Fundação e Infra',
        '09': '2. Fundação e Infra',
        '06': '3. Estrutura LSF e Cobertura',
        '08': '3. Estrutura LSF e Cobertura',
        '07': '4. Vedações e Instalações',
        '10': '4. Vedações e Instalações',
        '11': '4. Vedações e Instalações',
        '12': '4. Vedações e Instalações',
        '13': '5. Acabamentos e Esquadrias',
        '14': '5. Acabamentos e Esquadrias',
        '15': '5. Acabamentos e Esquadrias',
        '16': '5. Acabamentos e Esquadrias',
        '17': '5. Acabamentos e Esquadrias'
    }
    
    df_macro = df.copy()
    df_macro['MACRO_GRUPO'] = df_macro['SUBSISTEMA'].apply(lambda x: macro_map.get(str(x)[:2], 'Outros'))
    grouped = df_macro.groupby('MACRO_GRUPO')['CUSTO_FINAL_COM_BDI'].sum().reset_index()
    grouped['PARTICIPACAO'] = (grouped['CUSTO_FINAL_COM_BDI'] / valor_total) * 100
    
    # A. GRÁFICO DE ROSCA (MACRO COMPOSIÇÃO)
    fig1, ax1 = plt.subplots(figsize=(6.2, 2.8))
    labels = [f"{row['MACRO_GRUPO']}\n(R$ {row['CUSTO_FINAL_COM_BDI']/1000:,.0f}k - {row['PARTICIPACAO']:.1f}%)" for idx, row in grouped.iterrows()]
    palette = ['#1A365D', '#2B6CB0', '#3182CE', '#319795', '#D69E2E']
    
    wedges, texts, autotexts = ax1.pie(
        grouped['CUSTO_FINAL_COM_BDI'], 
        labels=labels, 
        autopct='', 
        startangle=140, 
        colors=palette[:len(grouped)],
        pctdistance=0.75, 
        wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2)
    )
    for text in texts:
        text.set_fontsize(7.0)
        text.set_fontweight('bold')
        text.set_color('#2D3748')
        
    ax1.set_title("DISTRIBUIÇÃO DE CUSTOS POR MACRO-ETAPAS", fontsize=9.5, fontweight='bold', color='#1A365D', pad=10)
    plt.tight_layout()
    
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png', dpi=200)
    plt.close(fig1)
    buf1.seek(0)
    
    # B. CRONOGRAMA GANTT + CURVA S
    fig2, (ax_gantt, ax_curva) = plt.subplots(2, 1, figsize=(6.2, 4.3), gridspec_kw={'height_ratios': [1.1, 1]})
    
    macro_tasks = grouped['MACRO_GRUPO'].tolist()[::-1]
    m = prazo_meses
    starts = [m*0.6, m*0.4, m*0.25, m*0.1, 0]
    durations = [m*0.4, m*0.5, m*0.45, m*0.35, m*0.3]
    
    colors_gantt = palette[:len(grouped)][::-1]
    ax_gantt.barh(macro_tasks, durations, left=starts, color=colors_gantt, height=0.45, edgecolor='#1A365D')
    ax_gantt.set_xlabel('Prazo de Execução (Meses)', fontsize=7.5, fontweight='bold', color='#2D3748')
    ax_gantt.set_title(f'CRONOGRAMA MACRO DE EXECUÇÃO FÍSICA ({prazo_meses} MESES)', fontsize=9.5, fontweight='bold', color='#1A365D')
    ax_gantt.set_xlim(0, prazo_meses)
    ax_gantt.grid(axis='x', linestyle='--', alpha=0.5)
    ax_gantt.tick_params(axis='both', labelsize=7.0)
    
    # FLUXO FINANCEIRO & CURVA S
    meses_labels = [f"Mês {i+1}" for i in range(prazo_meses)]
    x = np.linspace(-2, 2, prazo_meses)
    weights = np.exp(-x**2)
    perc_mensal = (weights / weights.sum()) * 100
    perc_acum = np.cumsum(perc_mensal)
    
    bars = ax_curva.bar(meses_labels, perc_mensal, color='#4299E1', alpha=0.65, label='% Mensal', width=0.5)
    ax_curva_line = ax_curva.twinx()
    ax_curva_line.plot(meses_labels, perc_acum, color='#D69E2E', marker='o', linewidth=2.2, markersize=4.5, label='% Acumulado')
    
    for bar in bars:
        height = bar.get_height()
        ax_curva.annotate(f'{height:.1f}%',
                          xy=(bar.get_x() + bar.get_width() / 2, height),
                          xytext=(0, 2),
                          textcoords="offset points",
                          ha='center', va='bottom', fontsize=6.0, fontweight='bold', color='#1A365D')
                          
    ax_curva.set_title('FLUXO DE DESEMBOLSO MENSAL E CURVA S ACUMULADA', fontsize=9.5, fontweight='bold', color='#1A365D')
    ax_curva.set_ylabel('Aporte Mensal (%)', fontsize=7.0, fontweight='bold', color='#2B6CB0')
    ax_curva_line.set_ylabel('Acumulado (%)', fontsize=7.0, fontweight='bold', color='#D69E2E')
    ax_curva.tick_params(axis='both', labelsize=7.0)
    ax_curva_line.tick_params(axis='both', labelsize=7.0)
    ax_curva_line.set_ylim(0, 115)
    ax_curva.set_ylim(0, max(perc_mensal)*1.25)
    
    plt.tight_layout()
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', dpi=200)
    plt.close(fig2)
    buf2.seek(0)
    
    return buf1, buf2, grouped

# 4. GERADOR DE PDF MULTIPÁGINAS (2 PÁGINAS)
def gerar_pdf_bytes(cliente, local, area_m2, area_fundacao_m2, tipo_fundacao, padrao, bdi, df, valor_total, valor_m2, prazo_meses, exibir_separado, buf1, buf2):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, textColor=colors.HexColor('#1A365D'), spaceAfter=6)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor('#4A5568'), spaceAfter=10)
    section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10.5, textColor=colors.HexColor('#2C5282'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#2D3748'))
    
    elements = []
    
    # ------------------ PÁGINA 1: PROPOSTA COMERCIAL & EAP ------------------
    elements.append(Paragraph("PROPOSTA COMERCIAL PRELIMINAR — LIGHT STEEL FRAME", title_style))
    elements.append(Paragraph("SISTEMA DE ENGENHARIA E ORÇAMENTAÇÃO AUTOMATIZADA (V2.0)", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=10))
    
    dados_cliente = [
        [Paragraph(f"<b>CLIENTE:</b> {cliente}", body_style), Paragraph(f"<b>LOCAL:</b> {local}", body_style)],
        [Paragraph(f"<b>ÁREA CONSTRUÍDA TOTAL:</b> {area_m2:,.2f} M²", body_style), Paragraph(f"<b>ÁREA FUNDAÇÃO:</b> {area_fundacao_m2:,.2f} M² ({tipo_fundacao})", body_style)],
        [Paragraph(f"<b>PADRÃO ACABAMENTO:</b> {padrao}", body_style), Paragraph(f"<b>PRAZO PREVISTO DA OBRA:</b> {prazo_meses} MESES", body_style)]
    ]
    t_cliente = Table(dados_cliente, colWidths=[270, 270])
    t_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF2F7')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#CBD5E0')),
    ]))
    elements.append(t_cliente)
    elements.append(Spacer(1, 8))
    
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
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor('#3182CE')),
    ]))
    elements.append(t_resumo)
    elements.append(Spacer(1, 8))
    
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
        ('PADDING', (0,0), (-1,-1), 2.8),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EDF2F7')),
    ]))
    elements.append(t_detalhes)
    
    # ------------------ PÁGINA 2: DASHBOARDS & PLANEJAMENTO ------------------
    elements.append(PageBreak())
    
    elements.append(Paragraph("DASHBOARD EXECUTIVO & PLANO DE EXECUÇÃO DA OBRA", title_style))
    elements.append(Paragraph("ANÁLISE DE COMPOSIÇÃO, CRONOGRAMA FÍSICO E FLUXO FINANCEIRO ACUMULADO", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=8))
    
    elements.append(Paragraph("3. DISTRIBUIÇÃO DE CUSTOS POR MACRO-ETAPAS", section_style))
    elements.append(Image(buf1, width=6.2*inch, height=2.8*inch))
    elements.append(Spacer(1, 6))
    
    elements.append(Paragraph("4. CRONOGRAMA FÍSICO-FINANCEIRO E CURVA S ACUMULADA", section_style))
    elements.append(Image(buf2, width=6.2*inch, height=4.3*inch))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# 5. FORMULÁRIO DE ENTRADA INTERATIVO
with st.form("form_orcamento"):
    st.write("### 📝 DADOS GERAIS DA OBRA")
    cliente = st.text_input("NOME DO CLIENTE / PROJETO:", value="RESIDENCIAL SILVA")
    local = st.text_input("LOCAL DA OBRA (CIDADE / UF):", value="JOINVILLE / SC")
    area_m2 = st.number_input("ÁREA TOTAL CONSTRUÍDA DA OBRA (M²):", min_value=10.0, max_value=5000.0, value=500.0, step=10.0)
    padrao = st.selectbox("PADRÃO DE ACABAMENTO GERAL:", ["BAIXO", "MÉDIO", "ALTO"], index=1)
    
    st.write("### 🏗️ PARÂMETROS DA FUNDAÇÃO E PRAZO")
    area_fundacao_m2 = st.number_input("ÁREA DA FUNDAÇÃO / PROJEÇÃO (M²):", min_value=10.0, max_value=5000.0, value=250.0, step=10.0)
    tipo_fundacao = st.selectbox("COMPLEXIDADE DA FUNDAÇÃO:", [
        "LEVE (SOLO BOM / RADIER SIMPLES)", 
        "MODERADA (PADRÃO DE MERCADO)", 
        "PESADA (SOLO FRÁGIL / REFORÇO DE ESTACAS)"
    ], index=1)
    
    prazo_meses = st.slider("PRAZO ESTIMADO DE EXECUÇÃO DA OBRA (MESES):", min_value=3, max_value=12, value=6, step=1)
    
    st.write("### ⚙️ FORMATO DE APRESENTAÇÃO E BDI")
    opcao_exibicao = st.radio(
        "COMO DESEJA EXIBIR OS VALORES NA TELA E NO PDF?",
        ["JUNTOS (VALOR UNIFICADO)", "SEPARADOS (MATERIAL E MÃO DE OBRA)"],
        index=0
    )
    exibir_separado = (opcao_exibicao == "SEPARADOS (MATERIAL E MÃO DE OBRA)")
    
    bdi = st.slider("PERCENTUAL DE BDI / MARGEM (%):", min_value=10, max_value=35, value=20) / 100.0
    
    submitted = st.form_submit_button("🚀 CALCULAR E GERAR PROPOSTA E DASHBOARDS (V2.0)")

if submitted:
    st.success("✅ PROPOSTA V2.0 E DASHBOARDS PROCESSADOS COM SUCESSO!")
    
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
    
    # METRICAS NO PAINEL
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
    
    # GERAR GRÁFICOS DO DASHBOARD
    buf1, buf2, grouped = gerar_graficos_dashboard(df, valor_total, prazo_meses)
    
    # GERAR PDF DE 2 PÁGINAS
    pdf_bytes = gerar_pdf_bytes(
        cliente, local, area_m2, area_fundacao_m2, tipo_fundacao.split(' ')[0], 
        padrao, bdi, df, valor_total, valor_m2, prazo_meses, exibir_separado, buf1, buf2
    )
    
    # BOTÃO DE DOWNLOAD
    st.download_button(
        label="📥 BAIXAR RELATÓRIO EXECUTIVO E DASHBOARDS (PDF 2 PÁGINAS)",
        data=pdf_bytes,
        file_name=f"RELATORIO_EXECUTIVO_{cliente.replace(' ', '_').upper()}.pdf",
        mime="application/pdf"
    )

    # VISUALIZAÇÃO NATIVA DOS DASHBOARDS E DA EAP NO STREAMLIT
    with st.expander("👁️ CLIQUE AQUI PARA VER A PRÉ-VISUALIZAÇÃO COMPLETA DA PROPOSTA"):
        st.markdown("### 📄 PÁGINA 1: EAP E VALORES DETALHADOS")
        st.markdown(f"**Cliente:** {cliente.upper()} | **Local:** {local} | **Prazo:** {prazo_meses} meses")
        st.info(f"💰 **VALOR TOTAL DO PROJETO:** R$ {valor_total:,.2f} (R$ {valor_m2:,.2f} / m²)")
        
        if exibir_separado:
            df_preview = df[["SUBSISTEMA", "CUSTO_MAT_FINAL", "CUSTO_MO_FINAL", "CUSTO_FINAL_COM_BDI", "PARTICIPACAO_PCT"]].copy()
            df_preview.columns = ["Subsistema", "Material (R$)", "Mão de Obra (R$)", "Total com BDI (R$)", "Part. (%)"]
            st.dataframe(df_preview.style.format({
                "Material (R$)": "R$ {:,.2f}",
                "Mão de Obra (R$)": "R$ {:,.2f}",
                "Total com BDI (R$)": "R$ {:,.2f}",
                "Part. (%)": "{:.1f}%"
            }), use_container_width=True)
        else:
            df_preview = df[["SUBSISTEMA", "CUSTO_FINAL_COM_BDI", "PARTICIPACAO_PCT"]].copy()
            df_preview.columns = ["Subsistema", "Valor com BDI (R$)", "Part. (%)"]
            st.dataframe(df_preview.style.format({
                "Valor com BDI (R$)": "R$ {:,.2f}",
                "Part. (%)": "{:.1f}%"
            }), use_container_width=True)
            
        st.markdown("---")
        st.markdown("### 📊 PÁGINA 2: DASHBOARDS EXECUTIVOS E PLANEJAMENTO")
        st.image(buf1, caption="Distribuição de Custos por Macro-Etapas", use_column_width=True)
        st.image(buf2, caption="Cronograma Físico (Gantt) e Fluxo Financeiro (Curva S)", use_column_width=True)
