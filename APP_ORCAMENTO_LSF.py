import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak, KeepTogether
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import io
import os
import re

# 1. CONFIGURAÇÃO DA PÁGINA E CORES
st.set_page_config(page_title="AMÂNCIO - ORÇAMENTADOR LSF V3.4", page_icon="🏗️", layout="wide")

HEX_PRIMARIA = "#0F2C3D"
HEX_DESTAQUE = "#E83F25"
HEX_SECUNDARIA = "#205475"
HEX_FUNDO = "#F0F4F8"
HEX_TEXTO = "#1A202C"

COR_PRIMARIA = colors.HexColor(HEX_PRIMARIA)
COR_DESTAQUE = colors.HexColor(HEX_DESTAQUE)
COR_SECUNDARIA = colors.HexColor(HEX_SECUNDARIA)
COR_FUNDO = colors.HexColor(HEX_FUNDO)
COR_TEXTO = colors.HexColor(HEX_TEXTO)

# MENU LATERAL PARA LINKS DO GOOGLE SHEETS
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.write("### AMÂNCIO")
    st.write("### 🔗 Conexões Google Sheets")
    link_valores = st.text_input("Link da Aba VALORES:", value="https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv")
    link_memorial = st.text_input("Link do Navegador da Aba MEMORIAL:", placeholder="Cole aqui o link da barra superior...")
    
    st.info("Copie o link da barra do seu navegador (URL) enquanto estiver visualizando a aba MEMORIAL e cole no campo acima.")

# EXTRATOR INTELIGENTE DE LINKS
def converter_link_sheets(url):
    match = re.search(r'd/([a-zA-Z0-9-_]+)', url)
    gid_match = re.search(r'gid=([0-9]+)', url)
    if match:
        sheet_id = match.group(1)
        gid = gid_match.group(1) if gid_match else "0"
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return url

# 2. CARREGAR DADOS DE VALORES
@st.cache_data(ttl=15)
def carregar_dados_google_sheets(url):
    try:
        url_csv = converter_link_sheets(url)
        df = pd.read_csv(url_csv)
        if len(df) >= 10:
            return df, "OK"
    except Exception as e:
        pass
    # BACKUP CASO FALHE
    return pd.DataFrame([
        {"SUBSISTEMA": "01. SERVIÇOS PRELIMINARES", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 5.0, "CUSTO_MO_UNIT_RS": 20.0},
        {"SUBSISTEMA": "02. GESTÃO DE OBRA E ADM", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 10.0, "CUSTO_MO_UNIT_RS": 110.0},
        {"SUBSISTEMA": "03. INSTALAÇÕES DO CANTEIRO", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 15.0, "CUSTO_MO_UNIT_RS": 15.0},
        {"SUBSISTEMA": "04. LOCAÇÕES E EQUIPAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 12.0, "CUSTO_MO_UNIT_RS": 8.0},
        {"SUBSISTEMA": "05. INFRAESTRUTURA (FUNDAÇÃO)", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 180.0, "CUSTO_MO_UNIT_RS": 100.0},
        {"SUBSISTEMA": "06. SUPERESTRUTURA LSF", "CONSUMO_MEDIO_M2": 30.0, "CUSTO_MAT_UNIT_RS": 7.5, "CUSTO_MO_UNIT_RS": 3.5},
        {"SUBSISTEMA": "07. FECHAMENTOS (EXT/INT)", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 140.0, "CUSTO_MO_UNIT_RS": 80.0},
        {"SUBSISTEMA": "08. COBERTURA E TELHADO", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 110.0, "CUSTO_MO_UNIT_RS": 50.0},
        {"SUBSISTEMA": "09. IMPERMEABILIZAÇÕES", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 20.0, "CUSTO_MO_UNIT_RS": 15.0},
        {"SUBSISTEMA": "10. INSTALAÇÕES HIDRÁULICAS", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 65.0, "CUSTO_MO_UNIT_RS": 45.0},
        {"SUBSISTEMA": "11. INSTALAÇÕES ELÉTRICAS", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 75.0, "CUSTO_MO_UNIT_RS": 55.0},
        {"SUBSISTEMA": "12. CLIMATIZAÇÃO E EXAUSTÃO", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 45.0, "CUSTO_MO_UNIT_RS": 30.0},
        {"SUBSISTEMA": "13. REVESTIMENTOS", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 70.0, "CUSTO_MO_UNIT_RS": 70.0},
        {"SUBSISTEMA": "14. PISOS E PAVIMENTAÇÕES", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 70.0, "CUSTO_MO_UNIT_RS": 50.0},
        {"SUBSISTEMA": "15. ESQUADRIAS E VIDROS", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 130.0, "CUSTO_MO_UNIT_RS": 50.0},
        {"SUBSISTEMA": "16. URBANIZAÇÃO E EXTERNOS", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 30.0, "CUSTO_MO_UNIT_RS": 20.0},
        {"SUBSISTEMA": "17. LIMPEZA FINAL DA OBRA", "CONSUMO_MEDIO_M2": 1.0, "CUSTO_MAT_UNIT_RS": 3.0, "CUSTO_MO_UNIT_RS": 12.0}
    ]), "USANDO BACKUP (Verifique o Link)"

# 3. CARREGAR DADOS DO MEMORIAL (COM LIMPEZA DE DADOS)
@st.cache_data(ttl=15)
def carregar_memorial_google_sheets(url_navegador):
    if not url_navegador:
        return pd.DataFrame(), "LINK VAZIO"
        
    url_csv = converter_link_sheets(url_navegador)
    try:
        df_mem = pd.read_csv(url_csv)
        # Limpar espaços invisíveis no nome das colunas e forçar maiúsculo
        df_mem.columns = df_mem.columns.str.strip().str.upper()
        
        if "CODIGO" in df_mem.columns:
            # Extrair apenas os números e garantir 2 dígitos (ex: "1" vira "01")
            df_mem['CODIGO'] = df_mem['CODIGO'].astype(str).str.extract(r'(\d+)')[0].str.zfill(2)
            return df_mem, "OK"
        else:
            return pd.DataFrame(), "ERRO: Coluna 'CODIGO' não encontrada na planilha."
    except Exception as e:
        return pd.DataFrame(), f"ERRO DE LEITURA: {str(e)}"

# 4. GERADOR DE GRÁFICOS DO DASHBOARD
def gerar_graficos_dashboard(df, valor_total, prazo_meses=6):
    macro_map = {
        '01': '1. Gestão e Canteiro', '02': '1. Gestão e Canteiro', '03': '1. Gestão e Canteiro', '04': '1. Gestão e Canteiro',
        '05': '2. Fundação e Infra', '09': '2. Fundação e Infra',
        '06': '3. Estrutura LSF e Telhado', '08': '3. Estrutura LSF e Telhado',
        '07': '4. Vedações e Instalações', '10': '4. Vedações e Instalações', '11': '4. Vedações e Instalações', '12': '4. Vedações e Instalações',
        '13': '5. Acabamentos e Externos', '14': '5. Acabamentos e Externos', '15': '5. Acabamentos e Externos', '16': '5. Acabamentos e Externos', '17': '5. Acabamentos e Externos'
    }
    df_macro = df.copy()
    df_macro['MACRO_GRUPO'] = df_macro['SUBSISTEMA'].apply(lambda x: macro_map.get(str(x)[:2], 'Outros'))
    grouped = df_macro.groupby('MACRO_GRUPO')['CUSTO_FINAL_COM_BDI'].sum().reset_index()
    grouped['PARTICIPACAO'] = (grouped['CUSTO_FINAL_COM_BDI'] / valor_total) * 100
    
    palette = [HEX_PRIMARIA, HEX_DESTAQUE, HEX_SECUNDARIA, '#319795', '#D69E2E']
    
    fig1, ax1 = plt.subplots(figsize=(6.2, 2.7))
    labels = [f"{r['MACRO_GRUPO']}\n({r['PARTICIPACAO']:.1f}%)" for idx, r in grouped.iterrows()]
    ax1.pie(grouped['CUSTO_FINAL_COM_BDI'], labels=labels, startangle=140, colors=palette[:len(grouped)],
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2.5),
            textprops=dict(fontsize=7, fontweight='bold', color=HEX_TEXTO))
    centre_circle = plt.Circle((0,0), 0.55, fc='white')
    ax1.add_artist(centre_circle)
    ax1.annotate(f"TOTAL\nR$ {valor_total/1000:,.0f}k", xy=(0, 0), fontsize=9, fontweight='bold', ha='center', va='center', color=HEX_PRIMARIA)
    ax1.set_title("DISTRIBUIÇÃO FINANCEIRA POR MACRO-GRUPO DE OBRA", fontsize=9.5, fontweight='bold', color=HEX_PRIMARIA, pad=8)
    plt.tight_layout()
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png', dpi=300)
    plt.close(fig1)
    buf1.seek(0)
    
    fig2, (ax_gantt, ax_curva) = plt.subplots(2, 1, figsize=(6.2, 4.4), gridspec_kw={'height_ratios': [1.1, 1]})
    macro_tasks = grouped['MACRO_GRUPO'].tolist()[::-1]
    m = prazo_meses
    starts = [m*0.6, m*0.4, m*0.25, m*0.1, 0]
    durations = [m*0.4, m*0.5, m*0.45, m*0.35, m*0.3]
    
    ax_gantt.barh(macro_tasks, durations, left=starts, color=palette[:len(grouped)][::-1], height=0.45, edgecolor='white', linewidth=1)
    ax_gantt.set_xlabel('Prazo de Execução (Meses)', fontsize=7.5, fontweight='bold', color=HEX_TEXTO)
    ax_gantt.set_title(f'CRONOGRAMA MACRO DE EXECUÇÃO FÍSICA ({prazo_meses} MESES)', fontsize=9.5, fontweight='bold', color=HEX_PRIMARIA)
    ax_gantt.set_xlim(0, prazo_meses)
    ax_gantt.grid(axis='x', linestyle='--', alpha=0.3)
    ax_gantt.tick_params(axis='both', labelsize=7.0, color=HEX_TEXTO)
    ax_gantt.spines['top'].set_visible(False)
    ax_gantt.spines['right'].set_visible(False)
    
    meses_labels = [f"Mês {i+1}" for i in range(prazo_meses)]
    x = np.linspace(-2, 2, prazo_meses)
    weights = np.exp(-x**2)
    perc_mensal = (weights / weights.sum()) * 100
    perc_acum = np.cumsum(perc_mensal)
    
    bars = ax_curva.bar(meses_labels, perc_mensal, color=HEX_SECUNDARIA, alpha=0.8, width=0.45, edgecolor='white')
    ax_curva_line = ax_curva.twinx()
    ax_curva_line.fill_between(meses_labels, 0, perc_acum, color=HEX_DESTAQUE, alpha=0.1)
    ax_curva_line.plot(meses_labels, perc_acum, color=HEX_DESTAQUE, marker='o', linewidth=2.5, markersize=5)
    
    for bar in bars:
        h = bar.get_height()
        ax_curva.annotate(f'{h:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 2), textcoords="offset points", ha='center', va='bottom', fontsize=6.5, fontweight='bold', color=HEX_PRIMARIA)
        
    ax_curva.set_title('FLUXO DE DESEMBOLSO MENSAL E CURVA S ACUMULADA', fontsize=9.5, fontweight='bold', color=HEX_PRIMARIA, pad=10)
    ax_curva.set_ylabel('Aporte (%)', fontsize=7.0, fontweight='bold', color=HEX_PRIMARIA)
    ax_curva_line.set_ylabel('Acumulado (%)', fontsize=7.0, fontweight='bold', color=HEX_DESTAQUE)
    ax_curva.tick_params(axis='both', labelsize=7.0)
    ax_curva_line.tick_params(axis='both', labelsize=7.0)
    ax_curva.grid(axis='y', linestyle='--', alpha=0.3)
    ax_curva.spines['top'].set_visible(False)
    ax_curva_line.spines['top'].set_visible(False)
    ax_curva_line.set_ylim(0, 115)
    ax_curva.set_ylim(0, max(perc_mensal)*1.25)
    
    plt.tight_layout()
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', dpi=300)
    plt.close(fig2)
    buf2.seek(0)
    
    return buf1, buf2

def primeira_pagina(canvas, doc): pass
def paginas_seguintes(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(COR_PRIMARIA)
    canvas.drawRightString(letter[0] - 36, 25, f"Página {doc.page}")
    canvas.restoreState()

# 5. GERADOR DO DOSSIÊ PDF
def gerar_dossie_pdf_bytes(cliente, local, area_m2, area_fundacao_m2, tipo_fundacao, padrao, bdi, df, df_mem, valor_total, valor_m2, prazo_meses, exibir_separado, buf1, buf2):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_cover = ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=COR_PRIMARIA, alignment=1, spaceAfter=10)
    sub_cover = ParagraphStyle('CoverSub', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=COR_DESTAQUE, alignment=1, spaceAfter=20)
    h1_style = ParagraphStyle('H1Style', fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=COR_PRIMARIA, spaceAfter=4)
    h2_style = ParagraphStyle('H2Style', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=COR_DESTAQUE, spaceBefore=10, spaceAfter=4)
    h3_style = ParagraphStyle('H3Style', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=COR_PRIMARIA, spaceBefore=10, spaceAfter=2)
    body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8, leading=10.5, textColor=COR_TEXTO)
    body_bold = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=COR_TEXTO)
    body_bold_white = ParagraphStyle('BodyBoldWhite', fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=colors.white)
    
    elements = []
    
    # --- PÁGINA 1: CAPA ---
    elements.append(HRFlowable(width="100%", thickness=3.5, color=COR_DESTAQUE, spaceAfter=15))
    if os.path.exists("logo.png"):
        try:
            img_reader = ImageReader("logo.png")
            img_w, img_h = img_reader.getSize()
            aspect = img_w / float(img_h)
            new_w = 3.0 * inch
            new_h = new_w / aspect
            if new_h > 1.2 * inch:
                new_h = 1.2 * inch
                new_w = new_h * aspect
            elements.append(Image("logo.png", width=new_w, height=new_h))
        except:
            elements.append(Image("logo.png", width=2.5*inch, height=1.0*inch))
    else:
        elements.append(Paragraph("AMÂNCIO", ParagraphStyle('LogoTxt', fontName='Helvetica-Bold', fontSize=34, textColor=COR_PRIMARIA, alignment=1)))
        elements.append(Paragraph("CONSTRUTORA INTELIGENTE", ParagraphStyle('SubLogoTxt', fontName='Helvetica-Bold', fontSize=10, textColor=COR_PRIMARIA, alignment=1, spaceAfter=15)))
    
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="35%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=25))
    elements.append(Paragraph("PROPOSTA COMERCIAL PRELIMINAR", title_cover))
    elements.append(Paragraph("ENGENHARIA E EDIFICAÇÕES EM LIGHT STEEL FRAME", sub_cover))
    elements.append(Spacer(1, 15))
    
    info_capa = [
        [Paragraph("<b>PROJETO / CLIENTE:</b>", body_bold), Paragraph(f"{cliente.upper()}", body)],
        [Paragraph("<b>LOCALIZAÇÃO:</b>", body_bold), Paragraph(f"{local.upper()}", body)],
        [Paragraph("<b>ÁREA CONSTRUÍDA TOTAL:</b>", body_bold), Paragraph(f"{area_m2:,.2f} M²", body)],
        [Paragraph("<b>ÁREA DA FUNDAÇÃO:</b>", body_bold), Paragraph(f"{area_fundacao_m2:,.2f} M² ({tipo_fundacao.split(' ')[0]})", body)],
        [Paragraph("<b>PADRÃO DE ACABAMENTO:</b>", body_bold), Paragraph(f"{padrao} PADRÃO", body)],
        [Paragraph("<b>PRAZO DE EXECUÇÃO:</b>", body_bold), Paragraph(f"{prazo_meses} MESES", body)],
        [Paragraph("<b>VERSÃO DO DOCUMENTO:</b>", body_bold), Paragraph("V3.4 — DOSSIÊ COMERCIAL AMÂNCIO", body)]
    ]
    t_capa = Table(info_capa, colWidths=[160, 300])
    t_capa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COR_FUNDO),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('PADDING', (0,0), (-1,-1), 6.5),
    ]))
    elements.append(t_capa)
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COR_PRIMARIA, spaceAfter=8))
    elements.append(Paragraph("AMÂNCIO CONSTRUTORA INTELIGENTE — INDUSTRIALIZAÇÃO E ALTA ENGENHARIA", ParagraphStyle('FootCapa', fontName='Helvetica-Bold', fontSize=7.5, textColor=COR_PRIMARIA, alignment=1)))
    elements.append(PageBreak())
    
    # --- PÁGINA 2: SUMÁRIO ---
    elements.append(Paragraph("SUMÁRIO ANALÍTICO & APRESENTAÇÃO INSTITUCIONAL", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
    elements.append(Paragraph("1. ESTRUTURA DO DOSSIÊ", h2_style))
    sumario_data = [
        [Paragraph("<b>SEÇÃO</b>", body_bold_white), Paragraph("<b>DESCRIÇÃO DO CONTEÚDO</b>", body_bold_white), Paragraph("<b>PÁG.</b>", body_bold_white)],
        [Paragraph("01", body), Paragraph("Capa Comercial Institucional e Dados do Cliente", body), Paragraph("01", body)],
        [Paragraph("02", body), Paragraph("Sumário, Apresentação da Amâncio e Vantagens da Engenharia LSF", body), Paragraph("02", body)],
        [Paragraph("03", body), Paragraph("Proposta Financeira, Resumo Executivo e EAP Detalhada", body), Paragraph("03", body)],
        [Paragraph("04", body), Paragraph("Dashboards Executivos: Macro-Grupos, Cronograma e Curva S", body), Paragraph("04", body)],
        [Paragraph("05", body), Paragraph("Memorial Descritivo: Escopo Analítico (Inclusos e Não Inclusos)", body), Paragraph("05", body)]
    ]
    t_sumario = Table(sumario_data, colWidths=[55, 405, 40])
    t_sumario.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COR_PRIMARIA),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    elements.append(t_sumario)
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("2. SOBRE A AMÂNCIO CONSTRUTORA INTELIGENTE", h2_style))
    elements.append(Paragraph("A <b>AMÂNCIO Construtora Inteligente</b> tem como premissa a engenharia e execução de edificações utilizando o sistema <b>Light Steel Frame (LSF)</b>. Buscamos integrar tecnologia, processos padronizados e gestão profissional para entregar obras com maior precisão, redução de desperdícios e prazos otimizados em relação à construção convencional, atuando sempre com transparência e foco no cliente.", body))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("3. DIFERENCIAIS DA ENGENHARIA EM LIGHT STEEL FRAME", h2_style))
    lsf_diffs = [
        [Paragraph("• <b>VELOCIDADE E PREVISIBILIDADE:</b>", body_bold), Paragraph("Processos estruturados e industrializados que ajudam a mitigar atrasos comuns.", body)],
        [Paragraph("• <b>DESEMPENHO TÉRMICO E ACÚSTICO:</b>", body_bold), Paragraph("Isolamento multicamadas, favorecendo o conforto térmico e eficiência.", body)],
        [Paragraph("• <b>PRECISÃO MILIMÉTRICA:</b>", body_bold), Paragraph("Estrutura em aço galvanizado Z275 engenheirado, reduzindo desvios.", body)],
        [Paragraph("• <b>SUSTENTABILIDADE E OBRA LIMPA:</b>", body_bold), Paragraph("Redução drástica de entulho e consumo de água mínimo.", body)]
    ]
    t_lsf = Table(lsf_diffs, colWidths=[170, 330])
    t_lsf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COR_FUNDO),
        ('PADDING', (0,0), (-1,-1), 5.5),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
    ]))
    elements.append(t_lsf)
    elements.append(PageBreak())
    
    # --- PÁGINA 3: PROPOSTA FINANCEIRA ---
    elements.append(Paragraph("PROPOSTA FINANCEIRA & DETALHAMENTO DE CUSTOS", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=8))
    elements.append(Paragraph("4. RESUMO EXECUTIVO DO ORÇAMENTO", h2_style))
    tot_mat = df["CUSTO_MAT_FINAL"].sum()
    tot_mo = df["CUSTO_MO_FINAL"].sum()
    resumo_data = [
        [Paragraph("<b>VALOR TOTAL ESTIMADO DO PROJETO:</b>", body_bold), Paragraph(f"<b>R$ {valor_total:,.2f}</b>", body_bold)],
        [Paragraph("<b>VALOR ESTIMADO POR M² CONSTRUÍDO:</b>", body_bold), Paragraph(f"<b>R$ {valor_m2:,.2f} / M²</b>", body_bold)],
        [Paragraph("<b>SUBTOTAL MATERIAIS COM BDI:</b>", body), Paragraph(f"R$ {tot_mat:,.2f} ({ (tot_mat/valor_total)*100:.1f}%)", body)],
        [Paragraph("<b>SUBTOTAL MÃO DE OBRA COM BDI:</b>", body), Paragraph(f"R$ {tot_mo:,.2f} ({ (tot_mo/valor_total)*100:.1f}%)", body)]
    ]
    t_resumo = Table(resumo_data, colWidths=[220, 280])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('BOX', (0,0), (-1,-1), 1.2, COR_PRIMARIA),
    ]))
    elements.append(t_resumo)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("5. EAP DETALHADA POR SUBSISTEMA CONSTRUTIVO (17 ITENS)", h2_style))
    
    if exibir_separado:
        data_table = [[
            Paragraph("<b>SUBSISTEMA</b>", body_bold_white), Paragraph("<b>MATERIAL (R$)</b>", body_bold_white), 
            Paragraph("<b>MÃO DE OBRA (R$)</b>", body_bold_white), Paragraph("<b>TOTAL (R$)</b>", body_bold_white), Paragraph("<b>PART. (%)</b>", body_bold_white)
        ]]
        for idx, row in df.iterrows():
            data_table.append([Paragraph(str(row["SUBSISTEMA"]), body), f"R$ {row['CUSTO_MAT_FINAL']:,.2f}", f"R$ {row['CUSTO_MO_FINAL']:,.2f}", f"R$ {row['CUSTO_FINAL_COM_BDI']:,.2f}", f"{row['PARTICIPACAO_PCT']:.1f}%"])
        data_table.append([Paragraph("<b>TOTAL GERAL</b>", body_bold), Paragraph(f"<b>R$ {tot_mat:,.2f}</b>", body_bold), Paragraph(f"<b>R$ {tot_mo:,.2f}</b>", body_bold), Paragraph(f"<b>R$ {valor_total:,.2f}</b>", body_bold), Paragraph("<b>100,0%</b>", body_bold)])
        t_detalhes = Table(data_table, colWidths=[165, 95, 95, 100, 45])
    else:
        data_table = [[Paragraph("<b>SUBSISTEMA</b>", body_bold_white), Paragraph("<b>VALOR COM BDI (R$)</b>", body_bold_white), Paragraph("<b>PART. (%)</b>", body_bold_white)]]
        for idx, row in df.iterrows():
            data_table.append([Paragraph(str(row["SUBSISTEMA"]), body), f"R$ {row['CUSTO_FINAL_COM_BDI']:,.2f}", f"{row['PARTICIPACAO_PCT']:.1f}%"])
        data_table.append([Paragraph("<b>TOTAL GERAL</b>", body_bold), Paragraph(f"<b>R$ {valor_total:,.2f}</b>", body_bold), Paragraph("<b>100,0%</b>", body_bold)])
        t_detalhes = Table(data_table, colWidths=[270, 140, 90])

    t_detalhes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COR_PRIMARIA),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 2.2),
        ('BACKGROUND', (0,-1), (-1,-1), COR_FUNDO),
    ]))
    elements.append(t_detalhes)
    elements.append(PageBreak())
    
    # --- PÁGINA 4: DASHBOARDS ---
    elements.append(Paragraph("DASHBOARDS EXECUTIVOS & FLUXO DE EXECUÇÃO", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=8))
    elements.append(Image(buf1, width=6.2*inch, height=2.7*inch))
    elements.append(Spacer(1, 4))
    elements.append(Image(buf2, width=6.2*inch, height=4.4*inch))
    elements.append(PageBreak())

    # --- PÁGINA 5+: MEMORIAL DESCRITIVO LIDO DA PLANILHA ---
    elements.append(Paragraph("MEMORIAL DESCRITIVO PRELIMINAR (ESCOPO)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=15))
    elements.append(Paragraph("Relação analítica de componentes, materiais e serviços contemplados (ou não) nesta estimativa de custos:", body))
    elements.append(Spacer(1, 10))

    if df_mem.empty:
         elements.append(Paragraph("<i>Nenhum item de memorial carregado. Verifique a aba e a coluna CODIGO.</i>", body))
    else:
        for idx, row in df.iterrows():
            sub_full = str(row["SUBSISTEMA"])
            prefix = sub_full[:2]
            
            df_filtro = df_mem[df_mem['CODIGO'] == prefix]
            
            if not df_filtro.empty:
                texto_explicativo = str(df_filtro.iloc[0]['DESCRICAO_ETAPA'])
                if pd.isna(texto_explicativo): texto_explicativo = "Etapa do projeto."
                
                tabela_memorial = []
                tabela_memorial.append(Paragraph(sub_full, h3_style))
                tabela_memorial.append(Paragraph(f"<i>{texto_explicativo}</i>", body))
                tabela_memorial.append(Spacer(1, 4))
                
                mem_data = [[
                    Paragraph("<b>ITEM / SERVIÇO</b>", body_bold_white),
                    Paragraph("<b>STATUS</b>", body_bold_white),
                    Paragraph("<b>OBSERVAÇÕES / PADRÃO</b>", body_bold_white)
                ]]
                
                for _, item_row in df_filtro.iterrows():
                    servico = str(item_row.get('ITEM', ''))
                    status_txt = str(item_row.get('STATUS', '')).upper()
                    obs = str(item_row.get('OBSERVACAO', ''))
                    
                    if pd.isna(servico) or servico == "nan": continue
                    
                    if "NÃO" in status_txt or "NAO" in status_txt:
                        status_f = f'<font color="{HEX_DESTAQUE}"><b>{status_txt}</b></font>'
                    else:
                        status_f = f'<font color="{HEX_PRIMARIA}"><b>{status_txt}</b></font>'
                        
                    mem_data.append([Paragraph(servico, body), Paragraph(status_f, body), Paragraph(obs, body)])
                    
                if len(mem_data) > 1:
                    t_mem = Table(mem_data, colWidths=[190, 80, 230])
                    t_mem.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), COR_SECUNDARIA),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
                        ('PADDING', (0,0), (-1,-1), 3),
                        ('ALIGN', (1,1), (1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ]))
                    tabela_memorial.append(t_mem)
                    tabela_memorial.append(Spacer(1, 8))
                    elements.append(KeepTogether(tabela_memorial))

    doc.build(elements, onFirstPage=primeira_pagina, onLaterPages=paginas_seguintes)
    buffer.seek(0)
    return buffer.getvalue()

# 6. APP PRINCIPAL E FORMULÁRIO
st.write("### 📝 DADOS GERAIS DO PROJETO E CLIENTE")
with st.form("form_orcamento"):
    col1, col2 = st.columns(2)
    cliente = col1.text_input("NOME DO CLIENTE / PROJETO:", value="RESIDENCIAL SILVA")
    local = col2.text_input("LOCAL DA OBRA (CIDADE / UF):", value="JOINVILLE / SC")
    
    col3, col4 = st.columns(2)
    area_m2 = col3.number_input("ÁREA TOTAL CONSTRUÍDA (M²):", min_value=10.0, max_value=5000.0, value=500.0, step=10.0)
    padrao = col4.selectbox("PADRÃO DE ACABAMENTO GERAL:", ["BAIXO", "MÉDIO", "ALTO"], index=1)
    
    st.write("### 🏗️ PARÂMETROS DA FUNDAÇÃO E PRAZO")
    col5, col6 = st.columns(2)
    area_fundacao_m2 = col5.number_input("ÁREA DA FUNDAÇÃO / PROJEÇÃO (M²):", min_value=10.0, max_value=5000.0, value=250.0, step=10.0)
    tipo_fundacao = col6.selectbox("COMPLEXIDADE DA FUNDAÇÃO:", [
        "LEVE (SOLO BOM / RADIER SIMPLES)", 
        "MODERADA (PADRÃO DE MERCADO)", 
        "PESADA (SOLO FRÁGIL / REFORÇO DE ESTACAS)"
    ], index=1)
    
    prazo_meses = st.slider("PRAZO ESTIMADO DE EXECUÇÃO DA OBRA (MESES):", min_value=3, max_value=12, value=6, step=1)
    
    st.write("### ⚙️ FORMATO DE EXIBIÇÃO E MARGEM BDI")
    opcao_exibicao = st.radio(
        "COMO DESEJA EXIBIR OS VALORES NA TELA E NO DOSSIÊ PDF?",
        ["JUNTOS (VALOR UNIFICADO)", "SEPARADOS (MATERIAL E MÃO DE OBRA)"],
        index=0
    )
    exibir_separado = (opcao_exibicao == "SEPARADOS (MATERIAL E MÃO DE OBRA)")
    bdi = st.slider("PERCENTUAL DE BDI / MARGEM (%):", min_value=10, max_value=35, value=20) / 100.0
    
    submitted = st.form_submit_button("🚀 GERAR DOSSIÊ COMERCIAL AMÂNCIO (V3.4)", use_container_width=True)

if submitted:
    with st.spinner("Conectando ao Google Sheets e gerando Dossiê Analítico..."):
        df, status_val = carregar_dados_google_sheets(link_valores)
        df_mem, status_mem = carregar_memorial_google_sheets(link_memorial)
        
        # EXIBIR AVISOS CASO A CONEXÃO FALHE
        if status_mem != "OK":
            st.warning(f"⚠️ AVISO MEMORIAL: {status_mem}. O sistema pode não carregar todos os itens. Verifique o link fornecido e se a planilha está com acesso público.")
            
        fator_padrao = 0.85 if padrao == "BAIXO" else (1.00 if padrao == "MÉDIO" else 1.30)
        fator_fundacao = 0.85 if "LEVE" in tipo_fundacao else (1.35 if "PESADA" in tipo_fundacao else 1.00)

        custos_mat, custos_mo = [], []
        
        for idx, row in df.iterrows():
            sub = str(row["SUBSISTEMA"]).upper()
            consumo = float(row.get("CONSUMO_MEDIO_M2", 1.0))
            c_mat = float(row.get("CUSTO_MAT_UNIT_RS", 50.0))
            c_mo = float(row.get("CUSTO_MO_UNIT_RS", 50.0))
            
            area_aplicada = area_fundacao_m2 if "INFRA" in sub or "FUNDAÇ" in sub or "RADIER" in sub else area_m2
            fator_extra = fator_fundacao if "INFRA" in sub or "FUNDAÇ" in sub or "RADIER" in sub else 1.00
                
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
        
        # GERAR GRÁFICOS E PDF
        buf1, buf2 = gerar_graficos_dashboard(df, valor_total, prazo_meses)
        pdf_bytes = gerar_dossie_pdf_bytes(
            cliente, local, area_m2, area_fundacao_m2, tipo_fundacao, 
            padrao, bdi, df, df_mem, valor_total, valor_m2, prazo_meses, exibir_separado, buf1, buf2
        )
        
        st.success("✅ DOSSIÊ COMERCIAL V3.4 GERADO COM SUCESSO!")
        
        st.download_button(
            label="📥 BAIXAR DOSSIÊ COMERCIAL AMÂNCIO (COM MEMORIAL DINÂMICO)",
            data=pdf_bytes,
            file_name=f"DOSSIE_AMANCIO_{cliente.replace(' ', '_').upper()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
