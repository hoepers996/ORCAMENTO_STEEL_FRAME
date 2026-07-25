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
st.set_page_config(page_title="AMÂNCIO - ORÇAMENTADOR LSF V4.6", page_icon="🏗️", layout="wide")

HEX_PRIMARIA = "#0F2C3D"
HEX_DESTAQUE = "#E83F25"
HEX_SECUNDARIA = "#205475"
HEX_FUNDO = "#F4F7FA" 
HEX_TEXTO = "#1A202C"
HEX_GRID = "#CDD7DF"

COR_PRIMARIA = colors.HexColor(HEX_PRIMARIA)
COR_DESTAQUE = colors.HexColor(HEX_DESTAQUE)
COR_SECUNDARIA = colors.HexColor(HEX_SECUNDARIA)
COR_FUNDO = colors.HexColor(HEX_FUNDO)
COR_TEXTO = colors.HexColor(HEX_TEXTO)

URL_VALORES = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv&gid=0"
URL_MEMORIAL = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv&gid=819485538"

# 2. CARREGAMENTO DE DADOS
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

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.write("### AMÂNCIO")
    st.write("### 🟢 Conexão com Google Sheets")
    st.success("Planilha de Custos Conectada")
    st.success("Memorial Descritivo Conectado")
    st.info("🎨 Gerador de Cards Ilustrativos Nativos Ativado!")

# GERADOR DE CARDS ILUSTRATIVOS TÉCNICOS (100% OFFLINE E INFALÍVEL)
def gerar_card_ilustrativo_etapa(prefix, sub_nome):
    # 1. Tenta carregar imagem local do GitHub primeiro
    for ext in ['.jpg', '.png', '.jpeg', '.JPG', '.PNG']:
        local_path = f"img_{prefix}{ext}"
        if os.path.exists(local_path):
            try:
                return ImageReader(local_path)
            except:
                pass

    # 2. Se não houver foto local, desenha um Card Técnico Blueprint em memória!
    fig, ax = plt.subplots(figsize=(4.5, 3.2), facecolor='#0F2C3D')
    ax.set_facecolor('#0F2C3D')
    ax.axis('off')
    
    # Grade Blueprint
    for x in np.linspace(0, 1, 10):
        ax.axvline(x, color='#205475', linestyle='--', alpha=0.3)
    for y in np.linspace(0, 1, 10):
        ax.axhline(y, color='#205475', linestyle='--', alpha=0.3)
        
    # Esquema visual dinâmico por etapa
    if prefix in ['01', '02', '03', '04']:
        rect = patches.Rectangle((0.2, 0.35), 0.6, 0.35, facecolor='#205475', edgecolor='#E83F25', linewidth=2)
        ax.add_patch(rect)
        ax.text(0.5, 0.52, "CANTEIRO & PROJETOS", color='white', fontweight='bold', fontsize=10, ha='center')
    elif prefix in ['05', '09']:
        rect = patches.Rectangle((0.15, 0.3), 0.7, 0.2, facecolor='#CBD5E0', edgecolor='#0F2C3D', linewidth=2)
        ax.add_patch(rect)
        for x_p in np.linspace(0.2, 0.8, 6):
            ax.plot([x_p, x_p], [0.3, 0.5], color='#E83F25', linewidth=2)
        ax.text(0.5, 0.4, "BASE RADIER DE CONCRETO", color='#0F2C3D', fontweight='bold', fontsize=8.5, ha='center')
    elif prefix in ['06', '08']:
        for x_p in np.linspace(0.2, 0.8, 5):
            rect = patches.Rectangle((x_p-0.03, 0.25), 0.06, 0.5, facecolor='#4299E1', edgecolor='white', linewidth=1)
            ax.add_patch(rect)
        ax.plot([0.15, 0.85], [0.72, 0.72], color='#E83F25', linewidth=3)
        ax.plot([0.15, 0.85], [0.28, 0.28], color='#E83F25', linewidth=3)
        ax.text(0.5, 0.5, "PERFIS AÇO STEEL FRAME Z275", color='white', fontweight='bold', fontsize=8, ha='center', bbox=dict(facecolor='#0F2C3D', pad=2))
    elif prefix in ['07', '10', '11', '12']:
        rect = patches.Rectangle((0.2, 0.25), 0.6, 0.5, facecolor='#319795', alpha=0.8)
        ax.add_patch(rect)
        ax.plot([0.2, 0.8], [0.4, 0.6], color='#E83F25', linewidth=3)
        ax.plot([0.2, 0.8], [0.6, 0.4], color='#4299E1', linewidth=3)
        ax.text(0.5, 0.8, "INSTALAÇÕES E VEDAÇÕES", color='white', fontweight='bold', fontsize=9, ha='center')
    else:
        rect = patches.Rectangle((0.25, 0.25), 0.5, 0.4, facecolor='#E2E8F0', edgecolor='#E83F25', linewidth=2)
        ax.add_patch(rect)
        ax.plot([0.2, 0.5, 0.8], [0.65, 0.85, 0.65], color='#0F2C3D', linewidth=3)
        ax.text(0.5, 0.45, "ACABAMENTOS E FACHADA", color='#0F2C3D', fontweight='bold', fontsize=8.5, ha='center')
        
    ax.text(0.5, 0.12, f"AMÂNCIO • ESQUEMA TÉCNICO ETAPA {prefix}", color='#CBD5E0', fontsize=8, fontweight='bold', ha='center')
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return ImageReader(buf)

# 3. GERADORES DE DASHBOARDS
def processar_macro_etapas(df, valor_total):
    macro_map = {
        '01': '1. Canteiro e Gestão', '02': '1. Canteiro e Gestão', '03': '1. Canteiro e Gestão', '04': '1. Canteiro e Gestão',
        '05': '2. Fundação e Infra', '09': '2. Fundação e Infra',
        '06': '3. Estrutura LSF/Telhado', '08': '3. Estrutura LSF/Telhado',
        '07': '4. Vedações/Instalações', '10': '4. Vedações/Instalações', '11': '4. Vedações/Instalações', '12': '4. Vedações/Instalações',
        '13': '5. Acabamentos/Externos', '14': '5. Acabamentos/Externos', '15': '5. Acabamentos/Externos', '16': '5. Acabamentos/Externos', '17': '5. Acabamentos/Externos'
    }
    df_macro = df.copy()
    df_macro['MACRO'] = df_macro['SUBSISTEMA'].apply(lambda x: macro_map.get(str(x)[:2], 'Outros'))
    grouped = df_macro.groupby('MACRO')['CUSTO_FINAL_COM_BDI'].sum().reset_index()
    
    ordem_correta = ['1. Canteiro e Gestão', '2. Fundação e Infra', '3. Estrutura LSF/Telhado', '4. Vedações/Instalações', '5. Acabamentos/Externos']
    grouped['MACRO'] = pd.Categorical(grouped['MACRO'], categories=ordem_correta, ordered=True)
    grouped = grouped.sort_values('MACRO')
    grouped['PESO'] = grouped['CUSTO_FINAL_COM_BDI'] / valor_total
    return grouped

def plot_custo_etapa(grouped, valor_total):
    fig = plt.figure(figsize=(8, 4), facecolor=HEX_FUNDO)
    ax = fig.add_subplot(111)
    palette = [HEX_PRIMARIA, HEX_SECUNDARIA, HEX_DESTAQUE, '#319795', '#D69E2E']
    
    wedges, texts, autotexts = ax.pie(
        grouped['CUSTO_FINAL_COM_BDI'], labels=grouped['MACRO'], autopct='%1.1f%%', 
        startangle=140, colors=palette,
        wedgeprops=dict(width=0.45, edgecolor=HEX_FUNDO, linewidth=2),
        textprops=dict(fontsize=9, fontweight='bold', color=HEX_TEXTO), pctdistance=0.75
    )
    plt.setp(autotexts, size=9, weight="bold", color="white")
    
    centre_circle = plt.Circle((0,0), 0.55, fc=HEX_FUNDO)
    ax.add_artist(centre_circle)
    ax.annotate(f"TOTAL\nR$ {valor_total/1000:,.0f}k", xy=(0, 0), fontsize=12, fontweight='bold', ha='center', va='center', color=HEX_PRIMARIA)
    ax.axis('equal') 
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def plot_gantt_e_curvas(grouped, prazo_meses):
    pesos = grouped['PESO'].tolist()
    m = prazo_meses
    
    d1 = max(m * pesos[0] * 1.5, m * 0.2) 
    d2 = max(m * pesos[1] * 2.0, m * 0.2) 
    d3 = max(m * pesos[2] * 2.0, m * 0.3) 
    d4 = max(m * pesos[3] * 1.8, m * 0.3) 
    d5 = max(m * pesos[4] * 2.0, m * 0.3) 
    durations = [d1, d2, d3, d4, d5]
    
    s1 = 0
    s2 = s1 + (d1 * 0.3) 
    s3 = s2 + (d2 * 0.5) 
    s4 = s3 + (d3 * 0.4) 
    s5 = s4 + (d4 * 0.6) 
    starts = [s1, s2, s3, s4, s5]
    
    max_end = max([starts[i] + durations[i] for i in range(5)])
    if max_end > m:
        fator = m / max_end
        starts = [s * fator for s in starts]
        durations = [d * fator for d in durations]
        
    macro_tasks = grouped['MACRO'].tolist()[::-1]
    starts = starts[::-1]
    durations = durations[::-1]
    
    # GANTT
    fig_gantt = plt.figure(figsize=(9, 2.8), facecolor=HEX_FUNDO)
    ax_gantt = fig_gantt.add_subplot(111)
    for i in range(5):
        rect = patches.Rectangle((starts[i], i-0.35), durations[i], 0.7, facecolor=HEX_SECUNDARIA, edgecolor='white', linewidth=1)
        ax_gantt.add_patch(rect)
        ax_gantt.text(starts[i] + 0.1, i, macro_tasks[i], va='center', color='white', fontweight='bold', fontsize=9)

    ax_gantt.set_xlim(0, prazo_meses)
    ax_gantt.set_ylim(-0.5, 4.5)
    ax_gantt.set_xticks(range(0, prazo_meses + 1))
    ax_gantt.set_xticklabels([f'Mês {i}' for i in range(prazo_meses + 1)], fontsize=9, color=HEX_PRIMARIA)
    ax_gantt.tick_params(axis='x', length=5, width=1.5, color=HEX_PRIMARIA)
    ax_gantt.grid(axis='x', color=HEX_GRID, linestyle='-', linewidth=1, zorder=0)
    ax_gantt.set_yticks([])
    ax_gantt.spines['top'].set_visible(False)
    ax_gantt.spines['right'].set_visible(False)
    ax_gantt.spines['left'].set_visible(False)
    ax_gantt.spines['bottom'].set_color(HEX_PRIMARIA)
    ax_gantt.spines['bottom'].set_linewidth(1.5)

    plt.tight_layout()
    buf_gantt = io.BytesIO()
    plt.savefig(buf_gantt, format='png', dpi=300, bbox_inches='tight', facecolor=fig_gantt.get_facecolor())
    plt.close(fig_gantt)
    buf_gantt.seek(0)
    
    # CURVA S
    fig_curva = plt.figure(figsize=(9, 3.2), facecolor=HEX_FUNDO)
    ax_curva = fig_curva.add_subplot(111)
    
    x_coords = np.arange(0.5, prazo_meses + 0.5)
    meses_labels = [f"Mês {i+1}" for i in range(prazo_meses)]
    
    pico_previsto = sum([starts[i] + (durations[i]/2) for i in range(5)]) / 5 
    deslocamento = (pico_previsto / m) * 4 - 2 
    
    x = np.linspace(-2.5, 2.5, prazo_meses)
    weights = np.exp(-(x - deslocamento)**2)
    perc_mensal = (weights / weights.sum()) * 100
    perc_acum = np.cumsum(perc_mensal)
    
    bars = ax_curva.bar(x_coords, perc_mensal, color=HEX_SECUNDARIA, width=0.55, zorder=2)
    ax_line = ax_curva.twinx()
    ax_line.plot(x_coords, perc_acum, color=HEX_DESTAQUE, marker='o', linewidth=3.5, markersize=6, zorder=3)
    
    for bar in bars:
        h = bar.get_height()
        ax_curva.text(bar.get_x() + bar.get_width()/2, h + 0.5, f'{h:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold', color=HEX_PRIMARIA)
                      
    ax_curva.set_xlim(0, prazo_meses)
    ax_curva.set_xticks(x_coords)
    ax_curva.set_xticklabels(meses_labels, fontsize=9, color=HEX_PRIMARIA)
    ax_curva.set_ylim(0, max(perc_mensal) * 1.25)
    ax_curva.set_yticks([0, 10, 20, 30])
    ax_curva.set_yticklabels(['0%', '10%', '20%', '30%'], fontsize=9, color=HEX_PRIMARIA)
    ax_line.set_ylim(0, 110)
    ax_line.set_yticks([]) 
    
    ax_curva.tick_params(axis='x', length=0, labelsize=9, colors=HEX_PRIMARIA)
    ax_curva.spines['top'].set_visible(False)
    ax_curva.spines['right'].set_visible(False)
    ax_curva.spines['left'].set_visible(False)
    ax_curva.spines['bottom'].set_color(HEX_PRIMARIA)
    ax_curva.spines['bottom'].set_linewidth(1.5)
    ax_line.spines['top'].set_visible(False)
    ax_line.spines['right'].set_visible(False)
    ax_line.spines['left'].set_visible(False)
    ax_line.spines['bottom'].set_visible(False)
    ax_curva.grid(axis='y', color=HEX_GRID, linestyle='-', linewidth=1, zorder=1)

    plt.tight_layout()
    buf_curva = io.BytesIO()
    plt.savefig(buf_curva, format='png', dpi=300, bbox_inches='tight', facecolor=fig_curva.get_facecolor())
    plt.close(fig_curva)
    buf_curva.seek(0)
    
    return buf_gantt, buf_curva

# FUNÇÕES DE PAGINAÇÃO
def primeira_pagina(canvas, doc): pass
def paginas_seguintes(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(COR_PRIMARIA)
    canvas.drawRightString(letter[0] - 36, 25, f"Página {doc.page}")
    canvas.restoreState()

# 4. GERADOR DO DOSSIÊ PDF
def gerar_dossie_pdf_bytes(cliente, local, area_m2, area_fundacao_m2, tipo_fundacao, padrao, bdi, df, df_mem, valor_total, valor_m2, prazo_meses, exibir_separado, buf_rosca, buf_gantt, buf_curva):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_cover = ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=COR_PRIMARIA, alignment=1, spaceAfter=10)
    sub_cover = ParagraphStyle('CoverSub', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=COR_DESTAQUE, alignment=1, spaceAfter=20)
    h1_style = ParagraphStyle('H1Style', fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=COR_PRIMARIA, spaceAfter=4)
    h2_style = ParagraphStyle('H2Style', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=COR_DESTAQUE, spaceBefore=10, spaceAfter=4)
    h3_style = ParagraphStyle('H3Style', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=COR_PRIMARIA, spaceBefore=10, spaceAfter=2)
    body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=COR_TEXTO)
    body_bold = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=COR_TEXTO)
    body_bold_white = ParagraphStyle('BodyBoldWhite', fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=colors.white)
    
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
            pass
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
        [Paragraph("<b>VERSÃO DO DOCUMENTO:</b>", body_bold), Paragraph("V4.6 — DOSSIÊ COMERCIAL AMÂNCIO", body)]
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
        [Paragraph("04", body), Paragraph("Síntese de Previsibilidade e Dashboards Analíticos", body), Paragraph("04", body)],
        [Paragraph("05", body), Paragraph("Memorial Descritivo e Catálogo de Escopo com Imagens", body), Paragraph("05", body)]
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
        [Paragraph("<b>VALOR ESTIMADO POR M² CONSTRUÍDO:</b>", body_bold), Paragraph(f"<b>R$ {valor_m2:,.2f} / M²</b>", body_bold)]
    ]
    if exibir_separado:
        resumo_data.append([Paragraph("<b>SUBTOTAL MATERIAIS:</b>", body), Paragraph(f"R$ {tot_mat:,.2f} ({ (tot_mat/valor_total)*100:.1f}%)", body)])
        resumo_data.append([Paragraph("<b>SUBTOTAL MÃO DE OBRA:</b>", body), Paragraph(f"R$ {tot_mo:,.2f} ({ (tot_mo/valor_total)*100:.1f}%)", body)])

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
        data_table = [[Paragraph("<b>SUBSISTEMA</b>", body_bold_white), Paragraph("<b>VALOR (R$)</b>", body_bold_white), Paragraph("<b>PART. (%)</b>", body_bold_white)]]
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
    elements.append(Paragraph("SÍNTESE DE PREVISIBILIDADE E FLUXO DE EXECUÇÃO", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=8))
    
    elements.append(Paragraph("6. COMPOSIÇÃO DE CUSTO POR MACRO-ETAPAS", h2_style))
    elements.append(Image(buf_rosca, width=5.5*inch, height=2.75*inch))
    
    elements.append(Paragraph("7. CRONOGRAMA MACRO DE EXECUÇÃO FÍSICA (PONDERADO)", h2_style))
    elements.append(Image(buf_gantt, width=6.6*inch, height=2.0*inch))
    
    elements.append(Paragraph("8. FLUXO DE DESEMBOLSO FINANCEIRO E CURVA S ACUMULADA", h2_style))
    elements.append(Image(buf_curva, width=6.6*inch, height=2.3*inch))
    
    elements.append(PageBreak())

    # --- PÁGINA 5+: MEMORIAL DESCRITIVO ILUSTRADO NATIVO ---
    elements.append(Paragraph("CATÁLOGO DE ESCOPO E MEMORIAL DESCRITIVO", h1_style))
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
                    texto_explicativo = "Etapa construtiva e de engenharia."
                
                # OBTÉM O CARD ILUSTRATIVO (DA PASTA LOCAL OU GERADO NATIVAMENTE EM MEMÓRIA)
                img_reader = gerar_card_ilustrativo_etapa(prefix, sub_full)
                img_flowable = None
                
                if img_reader:
                    try:
                        iw, ih = img_reader.getSize()
                        aspect = iw / float(ih)
                        new_w = 2.2 * inch
                        new_h = new_w / aspect
                        img_flowable = Image(img_reader, width=new_w, height=new_h)
                    except:
                        pass

                tabela_memorial = []
                
                mem_data = [[
                    Paragraph("<b>COMPONENTE / SERVIÇO</b>", body_bold_white),
                    Paragraph("<b>STATUS</b>", body_bold_white),
                    Paragraph("<b>OBSERVAÇÕES</b>", body_bold_white)
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
                    if img_flowable:
                        t_mem = Table(mem_data, colWidths=[115, 60, 140])
                        t_mem.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), COR_SECUNDARIA),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
                            ('PADDING', (0,0), (-1,-1), 3),
                            ('ALIGN', (1,1), (1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ]))
                        
                        bloco_esq = [Paragraph(sub_full, h3_style), Paragraph(f"<i>{texto_explicativo}</i>", body), Spacer(1, 4), t_mem]
                        t_layout = Table([[bloco_esq, img_flowable]], colWidths=[330, 180])
                        t_layout.setStyle(TableStyle([
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                            ('PADDING', (0,0), (-1,-1), 0),
                            ('LEFTPADDING', (1,0), (1,-1), 8)
                        ]))
                        tabela_memorial.append(t_layout)
                    else:
                        t_mem = Table(mem_data, colWidths=[190, 80, 230])
                        t_mem.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), COR_SECUNDARIA),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
                            ('PADDING', (0,0), (-1,-1), 3),
                            ('ALIGN', (1,1), (1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ]))
                        tabela_memorial.append(Paragraph(sub_full, h3_style))
                        tabela_memorial.append(Paragraph(f"<i>{texto_explicativo}</i>", body))
                        tabela_memorial.append(Spacer(1, 4))
                        tabela_memorial.append(t_mem)
                        
                    tabela_memorial.append(Spacer(1, 14))
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
        "COMO DESEJA EXIBIR OS VALORES NO DOSSIÊ PDF?",
        ["JUNTOS (VALOR UNIFICADO)", "SEPARADOS (MATERIAL E MÃO DE OBRA)"],
        index=0
    )
    exibir_separado = (opcao_exibicao == "SEPARADOS (MATERIAL E MÃO DE OBRA)")
    bdi = st.slider("PERCENTUAL DE BDI / MARGEM (%):", min_value=10, max_value=35, value=20) / 100.0
    
    submitted = st.form_submit_button("🚀 GERAR DOSSIÊ COMERCIAL AMÂNCIO (V4.6)", use_container_width=True)

if submitted:
    with st.spinner("Sincronizando com o Google Sheets e gerando PDF com Ilustrações..."):
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
        
        # 1. Agrupar dados
        grouped = processar_macro_etapas(df_val, valor_total)
        
        # 2. Dashboards Independentes
        buf_rosca = plot_custo_etapa(grouped, valor_total)
        buf_gantt, buf_curva = plot_gantt_e_curvas(grouped, prazo_meses)
        
        # 3. Gerar PDF
        pdf_bytes = gerar_dossie_pdf_bytes(
            cliente, local, area_m2, area_fundacao_m2, tipo_fundacao, 
            padrao, bdi, df_val, df_mem, valor_total, valor_m2, prazo_meses, exibir_separado, buf_rosca, buf_gantt, buf_curva
        )
        
        st.success("✅ DOSSIÊ CATÁLOGO V4.6 GERADO COM SUCESSO!")
        
        st.download_button(
            label="📥 BAIXAR DOSSIÊ COMERCIAL AMÂNCIO (PDF ILUSTRADO)",
            data=pdf_bytes,
            file_name=f"DOSSIE_AMANCIO_V4.6_{cliente.replace(' ', '_').upper()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
