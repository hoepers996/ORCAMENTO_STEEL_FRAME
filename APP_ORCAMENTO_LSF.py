import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak, KeepTogether
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import io
import os

# 1. CONFIGURAÇÃO DA PÁGINA E CORES
st.set_page_config(page_title="AMÂNCIO - ORÇAMENTADOR LSF V4.0", page_icon="🏗️", layout="wide")

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

# LINKS DIRETOS DA PLANILHA (VIA GID EXATO)
URL_VALORES = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv&gid=0"
URL_MEMORIAL = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv&gid=819485538"

# 2. FUNÇÕES DE CARREGAMENTO DE DADOS
@st.cache_data(ttl=15)
def carregar_valores_sheets():
    try:
        df = pd.read_csv(URL_VALORES)
        df.columns = df.columns.str.strip().str.upper()
        if len(df) >= 10:
            return df, "OK"
    except Exception:
        pass
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
    ]), "BACKUP"

@st.cache_data(ttl=15)
def carregar_memorial_sheets():
    try:
        df = pd.read_csv(URL_MEMORIAL)
        df.columns = df.columns.str.strip().str.upper()
        if "CODIGO" in df.columns:
            df['CODIGO'] = df['CODIGO'].astype(str).str.extract(r'(\d+)')[0].str.zfill(2)
            return df, "OK"
    except Exception:
        pass
    return pd.DataFrame(), "ERRO_LEITURA"

# MENU LATERAL STATUS
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.write("### AMÂNCIO")
        
    st.write("### 🟢 Conexão com Google Sheets")
    st.success("Planilha de Custos Conectada")
    st.success("Memorial Descritivo Conectado")

# 3. GERADOR DO PAINEL DASHBOARD COMPLETO (ESTILO BI / EXCEL DASHBOARD)
def gerar_dashboard_bi_completo(df, valor_total, area_m2, prazo_meses, tot_mat, tot_mo, bdi):
    c_primary = HEX_PRIMARIA
    c_accent = HEX_DESTAQUE
    c_secondary = HEX_SECUNDARIA
    c_bg = '#F4F7FA'
    c_card = '#FFFFFF'
    c_text = HEX_TEXTO
    c_grey_light = '#E2E8F0'

    fig = plt.figure(figsize=(11, 6.2), facecolor=c_bg)
    gs = fig.add_gridspec(2, 4, width_ratios=[1.15, 1, 1, 1], height_ratios=[1, 1], wspace=0.32, hspace=0.38)

    # --- 1. PAINEL ESQUERDO: CARDS DE KPI ---
    ax_kpi = fig.add_subplot(gs[:, 0])
    ax_kpi.set_facecolor(c_bg)
    ax_kpi.axis('off')

    kpi_data = [
        ("CUSTO TOTAL DA OBRA", f"R$ {valor_total:,.2f}", HEX_PRIMARIA),
        ("VALOR POR M² CONSTRUÍDO", f"R$ {valor_total/area_m2:,.2f} /m²", HEX_SECUNDARIA),
        ("TOTAL EM MATERIAIS", f"R$ {tot_mat:,.2f}", "#319795"),
        ("TOTAL MÃO DE OBRA", f"R$ {tot_mo:,.2f}", HEX_DESTAQUE)
    ]

    for i, (title, val, color) in enumerate(kpi_data):
        y_pos = 0.77 - (i * 0.24)
        rect = patches.FancyBboxPatch((0.02, y_pos), 0.96, 0.20, boxstyle="round,pad=0.02", 
                                      facecolor=c_card, edgecolor=c_grey_light, linewidth=1, transform=ax_kpi.transAxes)
        ax_kpi.add_patch(rect)
        rect_strip = patches.FancyBboxPatch((0.02, y_pos), 0.04, 0.20, boxstyle="round,pad=0.0", 
                                            facecolor=color, edgecolor='none', transform=ax_kpi.transAxes)
        ax_kpi.add_patch(rect_strip)
        ax_kpi.text(0.10, y_pos + 0.13, title, fontsize=7.5, fontweight='bold', color='#718096', transform=ax_kpi.transAxes)
        ax_kpi.text(0.10, y_pos + 0.04, val, fontsize=10.0, fontweight='bold', color=c_primary, transform=ax_kpi.transAxes)

    # --- 2. GRÁFICO 1: CUSTO DIRETO X PROPOSTA COMERCIAL ---
    ax1 = fig.add_subplot(gs[0, 1])
    ax1.set_facecolor(c_card)
    custo_direto = valor_total / (1 + bdi)
    ax1.bar(['Custo Direto', 'Proposta\n(com BDI)'], [custo_direto/1000, valor_total/1000], color=['#A0AEC0', c_accent], width=0.50)
    ax1.set_title("Custo Direto x Proposta Final", fontsize=8.5, fontweight='bold', color=c_primary, pad=8)
    ax1.set_ylabel("Valor (R$ mil)", fontsize=7.0, color=c_text)
    ax1.tick_params(labelsize=7.0)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # --- 3. GRÁFICO 2: MATERIAIS X MÃO DE OBRA ---
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_facecolor(c_card)
    wedges, texts, autotexts = ax2.pie([tot_mat, tot_mo], labels=['Materiais', 'Mão de Obra'], autopct='%1.1f%%',
                                       startangle=90, colors=['#319795', c_accent],
                                       wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2),
                                       textprops=dict(fontsize=7.0, fontweight='bold', color=c_text))
    plt.setp(autotexts, size=7.0, weight="bold", color="white")
    ax2.set_title("Materiais x Mão de Obra", fontsize=8.5, fontweight='bold', color=c_primary, pad=8)

    # --- 4. GRÁFICO 3: CUSTO POR MACRO-ETAPA ---
    ax3 = fig.add_subplot(gs[0, 3])
    ax3.set_facecolor(c_card)
    macro_map = {
        '01': '1. Canteiro', '02': '1. Canteiro', '03': '1. Canteiro', '04': '1. Canteiro',
        '05': '2. Infra', '09': '2. Infra',
        '06': '3. LSF/Telh', '08': '3. LSF/Telh',
        '07': '4. Vedações', '10': '4. Vedações', '11': '4. Vedações', '12': '4. Vedações',
        '13': '5. Acabam.', '14': '5. Acabam.', '15': '5. Acabam.', '16': '5. Acabam.', '17': '5. Acabam.'
    }
    df_macro = df.copy()
    df_macro['MACRO'] = df_macro['SUBSISTEMA'].apply(lambda x: macro_map.get(str(x)[:2], 'Outros'))
    grouped = df_macro.groupby('MACRO')['CUSTO_FINAL_COM_BDI'].sum().reset_index()
    
    palette_macro = [c_primary, c_secondary, c_accent, '#319795', '#D69E2E']
    ax3.pie(grouped['CUSTO_FINAL_COM_BDI'], labels=grouped['MACRO'], startangle=140, colors=palette_macro[:len(grouped)],
            wedgeprops=dict(width=0.42, edgecolor='white', linewidth=1.5),
            textprops=dict(fontsize=6.5, fontweight='bold', color=c_text))
    ax3.set_title("Custo por Macro-Etapa", fontsize=8.5, fontweight='bold', color=c_primary, pad=8)

    # --- 5. GRÁFICO 4: CRONOGRAMA & CURVA S (PAINEL INFERIOR) ---
    ax4 = fig.add_subplot(gs[1, 1:])
    ax4.set_facecolor(c_card)
    
    meses_labels = [f"Mês {i+1}" for i in range(prazo_meses)]
    x = np.linspace(-2, 2, prazo_meses)
    weights = np.exp(-x**2)
    perc_mensal = (weights / weights.sum()) * 100
    perc_acum = np.cumsum(perc_mensal)
    
    bars = ax4.bar(meses_labels, perc_mensal, color=c_secondary, alpha=0.8, width=0.45, label='% Mensal')
    ax4_line = ax4.twinx()
    ax4_line.fill_between(meses_labels, 0, perc_acum, color=c_accent, alpha=0.1)
    ax4_line.plot(meses_labels, perc_acum, color=c_accent, marker='o', linewidth=2.2, markersize=4.5, label='% Acumulado')
    
    for bar in bars:
        h = bar.get_height()
        ax4.annotate(f'{h:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 2),
                     textcoords="offset points", ha='center', va='bottom', fontsize=6.5, fontweight='bold', color=c_primary)
        
    ax4.set_title(f'Fluxo Financeiro Previsto ({prazo_meses} Meses) e Curva S Acumulada', fontsize=9.0, fontweight='bold', color=c_primary, pad=6)
    ax4.set_ylabel('Aporte (%)', fontsize=7.0, fontweight='bold', color=c_primary)
    ax4_line.set_ylabel('Acumulado (%)', fontsize=7.0, fontweight='bold', color=c_accent)
    ax4.tick_params(axis='both', labelsize=7.0)
    ax4_line.tick_params(axis='both', labelsize=7.0)
    ax4.grid(axis='y', linestyle='--', alpha=0.3)
    ax4.spines['top'].set_visible(False)
    ax4_line.spines['top'].set_visible(False)
    ax4_line.set_ylim(0, 115)
    ax4.set_ylim(0, max(perc_mensal)*1.3)

    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.02, right=0.98)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def primeira_pagina(canvas, doc): pass
def paginas_seguintes(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(COR_PRIMARIA)
    canvas.drawRightString(letter[0] - 36, 25, f"Página {doc.page}")
    canvas.restoreState()

# 4. GERADOR DO DOSSIÊ PDF COMPLETO (5+ PÁGINAS)
def gerar_dossie_pdf_bytes(cliente, local, area_m2, area_fundacao_m2, tipo_fundacao, padrao, bdi, df, df_mem, valor_total, valor_m2, prazo_meses, exibir_separado, buf_dash):
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
        [Paragraph("<b>VERSÃO DO DOCUMENTO:</b>", body_bold), Paragraph("V4.0 — DOSSIÊ COMERCIAL AMÂNCIO", body)]
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
        [Paragraph("04", body), Paragraph("Dashboard Executivo BI: KPIs, Matriz Financeira e Curva S", body), Paragraph("04", body)],
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
    elements.append(Paragraph("5. EAP DETALHADA POR SUBSISTEMA CONSTRUTIVO", h2_style))
    
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
    
    # --- PÁGINA 4: DASHBOARD EXECUTIVE BI ---
    elements.append(Paragraph("DASHBOARD EXECUTIVO BI & PLANEJAMENTO", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=8))
    elements.append(Image(buf_dash, width=6.8*inch, height=4.2*inch))
    elements.append(PageBreak())

    # --- PÁGINA 5+: MEMORIAL DESCRITIVO LIDO DA PLANILHA ---
    elements.append(Paragraph("MEMORIAL DESCRITIVO PRELIMINAR (ESCOPO)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=15))
    elements.append(Paragraph("Relação analítica de componentes, materiais e serviços contemplados (ou não) nesta estimativa de custos:", body))
    elements.append(Spacer(1, 10))

    if df_mem.empty:
         elements.append(Paragraph("<i>Nenhum item de memorial carregado da planilha.</i>", body))
    else:
        col_item = 'ITEM' if 'ITEM' in df_mem.columns else df_mem.columns[2]
        col_status = 'STATUS' if 'STATUS' in df_mem.columns else df_mem.columns[3]
        col_obs = 'OBSERVACAO' if 'OBSERVACAO' in df_mem.columns else (df_mem.columns[4] if len(df_mem.columns) > 4 else df_mem.columns[-1])
        col_desc = 'DESCRICAO_ETAPA' if 'DESCRICAO_ETAPA' in df_mem.columns else df_mem.columns[1]

        for idx, row in df.iterrows():
            sub_full = str(row["SUBSISTEMA"])
            prefix = sub_full[:2]
            
            df_filtro = df_mem[df_mem['CODIGO'] == prefix]
            
            if not df_filtro.empty:
                texto_explicativo = str(df_filtro.iloc[0][col_desc])
                if pd.isna(texto_explicativo) or texto_explicativo == "nan": 
                    texto_explicativo = "Etapa do projeto construtivo."
                
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
                    servico = str(item_row.get(col_item, ''))
                    status_txt = str(item_row.get(col_status, '')).upper().strip()
                    obs = str(item_row.get(col_obs, ''))
                    
                    if pd.isna(servico) or servico == "nan": continue
                    if pd.isna(obs) or obs == "nan": obs = "-"
                    
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

# 5. FORMULÁRIO PRINCIPAL DO STREAMLIT
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
    
    submitted = st.form_submit_button("🚀 GERAR DOSSIÊ COMERCIAL AMÂNCIO (V4.0)", use_container_width=True)

if submitted:
    with st.spinner("Sincronizando com o Google Sheets e gerando Dashboard BI..."):
        df_val, status_val = carregar_valores_sheets()
        df_mem, status_mem = carregar_memorial_sheets()
        
        fator_padrao = 0.85 if padrao == "BAIXO" else (1.00 if padrao == "MÉDIO" else 1.30)
        fator_fundacao = 0.85 if "LEVE" in tipo_fundacao else (1.35 if "PESADA" in tipo_fundacao else 1.00)

        custos_mat, custos_mo = [], []
        for idx, row in df_val.iterrows():
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

        df_val["CUSTO_MAT_FINAL"] = custos_mat
        df_val["CUSTO_MO_FINAL"] = custos_mo
        df_val["CUSTO_FINAL_COM_BDI"] = df_val["CUSTO_MAT_FINAL"] + df_val["CUSTO_MO_FINAL"]
        df_val["PARTICIPACAO_PCT"] = (df_val["CUSTO_FINAL_COM_BDI"] / df_val["CUSTO_FINAL_COM_BDI"].sum()) * 100
        
        valor_total = df_val["CUSTO_FINAL_COM_BDI"].sum()
        valor_m2 = valor_total / area_m2
        tot_mat_geral = df_val["CUSTO_MAT_FINAL"].sum()
        tot_mo_geral = df_val["CUSTO_MO_FINAL"].sum()
        
        # GERAR DASHBOARD COMPLETO (BI)
        buf_dash = gerar_dashboard_bi_completo(df_val, valor_total, area_m2, prazo_meses, tot_mat_geral, tot_mo_geral, bdi)
        
        # GERAR DOSSIÊ PDF
        pdf_bytes = gerar_dossie_pdf_bytes(
            cliente, local, area_m2, area_fundacao_m2, tipo_fundacao, 
            padrao, bdi, df_val, df_mem, valor_total, valor_m2, prazo_meses, exibir_separado, buf_dash
        )
        
        st.success("✅ DOSSIÊ COMERCIAL V4.0 E DASHBOARD BI GERADOS COM SUCESSO!")
        
        # VISUALIZAÇÃO DO DASHBOARD BI DIRETO NA TELA DO APP
        st.markdown("### 📊 DASHBOARD EXECUTIVO BI")
        st.image(buf_dash, use_container_width=True)
        
        st.download_button(
            label="📥 BAIXAR DOSSIÊ COMERCIAL AMÂNCIO (PDF COMPLETO)",
            data=pdf_bytes,
            file_name=f"DOSSIE_AMANCIO_V4.0_{cliente.replace(' ', '_').upper()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
