import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import io
import os

# ==========================================
# 1. CONFIGURAÇÕES GERAIS E CORES DA MARCA
# ==========================================
st.set_page_config(page_title="AMÂNCIO - ORÇAMENTADOR LSF V6.3", page_icon="🏗️", layout="wide")

HEX_PRIMARIA = "#0F2C3D"
HEX_DESTAQUE = "#E83F25"
HEX_SECUNDARIA = "#205475"
HEX_FUNDO = "#F4F7FA" 
HEX_TEXTO = "#1A202C"

COR_PRIMARIA = colors.HexColor(HEX_PRIMARIA)
COR_DESTAQUE = colors.HexColor(HEX_DESTAQUE)
COR_SECUNDARIA = colors.HexColor(HEX_SECUNDARIA)
COR_FUNDO = colors.HexColor(HEX_FUNDO)
COR_TEXTO = colors.HexColor(HEX_TEXTO)

# NOVOS LINKS INTEGRADOS
URL_VALORES = "https://docs.google.com/spreadsheets/d/1kA4NHJ8VU3eDnipJ0ADArTWzm0YOFhD_t4FT1_nuHX4/export?format=csv&gid=0"
URL_MEMORIAL = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv&gid=819485538"

# ==========================================
# 2. CARREGAMENTO DE DADOS (NOVA ESTRUTURA)
# ==========================================
@st.cache_data(ttl=15)
def carregar_valores():
    try:
        df = pd.read_csv(URL_VALORES)
        df.columns = df.columns.str.strip().str.upper()
        if "MAT_BAIXO" in df.columns and len(df) >= 10: 
            return df
    except: pass
    
    # BACKUP SE HOUVER FALHA DE CONEXÃO
    return pd.DataFrame([
        {"SUBSISTEMA": "01. SERVIÇOS PRELIMINARES", "CATEGORIA": "CANTEIRO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 5.0, "MAT_MEDIO": 5.0, "MAT_ALTO": 5.0, "MO_BAIXO": 20.0, "MO_MEDIO": 20.0, "MO_ALTO": 20.0},
        {"SUBSISTEMA": "02. GESTÃO DE OBRA E ADM", "CATEGORIA": "CANTEIRO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 10.0, "MAT_MEDIO": 10.0, "MAT_ALTO": 10.0, "MO_BAIXO": 110.0, "MO_MEDIO": 110.0, "MO_ALTO": 110.0},
        {"SUBSISTEMA": "03. INSTALAÇÕES DO CANTEIRO", "CATEGORIA": "CANTEIRO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 15.0, "MAT_MEDIO": 15.0, "MAT_ALTO": 15.0, "MO_BAIXO": 15.0, "MO_MEDIO": 15.0, "MO_ALTO": 15.0},
        {"SUBSISTEMA": "04. LOCAÇÕES E EQUIPAMENTOS", "CATEGORIA": "CANTEIRO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 12.0, "MAT_MEDIO": 12.0, "MAT_ALTO": 12.0, "MO_BAIXO": 8.0, "MO_MEDIO": 8.0, "MO_ALTO": 8.0},
        {"SUBSISTEMA": "05. INFRAESTRUTURA (FUNDAÇÃO)", "CATEGORIA": "FUNDACAO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 153.0, "MAT_MEDIO": 180.0, "MAT_ALTO": 243.0, "MO_BAIXO": 85.0, "MO_MEDIO": 100.0, "MO_ALTO": 135.0},
        {"SUBSISTEMA": "06. SUPERESTRUTURA LSF", "CATEGORIA": "ESTRUTURA", "CONSUMO_MEDIO_M2": 30.0, "MAT_BAIXO": 6.75, "MAT_MEDIO": 7.5, "MAT_ALTO": 9.37, "MO_BAIXO": 3.15, "MO_MEDIO": 3.5, "MO_ALTO": 4.37},
        {"SUBSISTEMA": "07. FECHAMENTOS (EXT/INT)", "CATEGORIA": "VEDACOES", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 126.0, "MAT_MEDIO": 140.0, "MAT_ALTO": 182.0, "MO_BAIXO": 72.0, "MO_MEDIO": 80.0, "MO_ALTO": 104.0},
        {"SUBSISTEMA": "08. COBERTURA E TELHADO", "CATEGORIA": "ESTRUTURA", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 99.0, "MAT_MEDIO": 110.0, "MAT_ALTO": 137.5, "MO_BAIXO": 45.0, "MO_MEDIO": 50.0, "MO_ALTO": 62.5},
        {"SUBSISTEMA": "09. IMPERMEABILIZAÇÕES", "CATEGORIA": "FUNDACAO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 17.0, "MAT_MEDIO": 20.0, "MAT_ALTO": 27.0, "MO_BAIXO": 12.75, "MO_MEDIO": 15.0, "MO_ALTO": 20.25},
        {"SUBSISTEMA": "10. INSTALAÇÕES HIDRÁULICAS", "CATEGORIA": "INSTALACOES", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 58.5, "MAT_MEDIO": 65.0, "MAT_ALTO": 84.5, "MO_BAIXO": 40.5, "MO_MEDIO": 45.0, "MO_ALTO": 58.5},
        {"SUBSISTEMA": "11. INSTALAÇÕES ELÉTRICAS", "CATEGORIA": "INSTALACOES", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 67.5, "MAT_MEDIO": 75.0, "MAT_ALTO": 97.5, "MO_BAIXO": 49.5, "MO_MEDIO": 55.0, "MO_ALTO": 71.5},
        {"SUBSISTEMA": "12. CLIMATIZAÇÃO E EXAUSTÃO", "CATEGORIA": "INSTALACOES", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 40.5, "MAT_MEDIO": 45.0, "MAT_ALTO": 58.5, "MO_BAIXO": 27.0, "MO_MEDIO": 30.0, "MO_ALTO": 39.0},
        {"SUBSISTEMA": "13. REVESTIMENTOS", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 56.0, "MAT_MEDIO": 70.0, "MAT_ALTO": 98.0, "MO_BAIXO": 56.0, "MO_MEDIO": 70.0, "MO_ALTO": 98.0},
        {"SUBSISTEMA": "14. PISOS E PAVIMENTAÇÕES", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 56.0, "MAT_MEDIO": 70.0, "MAT_ALTO": 98.0, "MO_BAIXO": 40.0, "MO_MEDIO": 50.0, "MO_ALTO": 70.0},
        {"SUBSISTEMA": "15. ESQUADRIAS E VIDROS", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 104.0, "MAT_MEDIO": 130.0, "MAT_ALTO": 182.0, "MO_BAIXO": 40.0, "MO_MEDIO": 50.0, "MO_ALTO": 70.0},
        {"SUBSISTEMA": "16. URBANIZAÇÃO E EXTERNOS", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 24.0, "MAT_MEDIO": 30.0, "MAT_ALTO": 42.0, "MO_BAIXO": 16.0, "MO_MEDIO": 20.0, "MO_ALTO": 28.0},
        {"SUBSISTEMA": "17. LIMPEZA FINAL DA OBRA", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 2.4, "MAT_MEDIO": 3.0, "MAT_ALTO": 4.2, "MO_BAIXO": 9.6, "MO_MEDIO": 12.0, "MO_ALTO": 16.8}
    ])

@st.cache_data(ttl=15)
def carregar_memorial():
    try:
        df = pd.read_csv(URL_MEMORIAL)
        df.columns = df.columns.str.strip().str.upper()
        if "CODIGO" in df.columns:
            df['CODIGO'] = df['CODIGO'].astype(str).str.extract(r'(\d+)')[0].str.zfill(2)
            return df
    except: pass
    return pd.DataFrame()

# ==========================================
# 3. MOTORES DE GRÁFICOS (DASHBOARDS)
# ==========================================
def agrupar_macro(df, col_val):
    m_map = {
        '01':'1. Canteiro', '02':'1. Canteiro', '03':'1. Canteiro', '04':'1. Canteiro', 
        '05':'2. Fundação', '09':'2. Fundação', 
        '06':'3. Estrutura LSF', '08':'3. Estrutura LSF', 
        '07':'4. Instalações/Vedações', '10':'4. Instalações/Vedações', '11':'4. Instalações/Vedações', '12':'4. Instalações/Vedações'
    }
    df_m = df.copy()
    df_m['MACRO'] = df_m['SUBSISTEMA'].apply(lambda x: m_map.get(str(x)[:2], '5. Acabamentos'))
    g = df_m.groupby('MACRO')[col_val].sum().reset_index()
    return g

def plot_rosca(g, val_tot):
    fig = plt.figure(figsize=(8, 4), facecolor=HEX_FUNDO); ax = fig.add_subplot(111)
    if val_tot == 0: ax.axis('off')
    else:
        w, t, at = ax.pie(g.iloc[:,1], labels=g['MACRO'], autopct='%1.1f%%', startangle=140, colors=[HEX_PRIMARIA, HEX_SECUNDARIA, HEX_DESTAQUE, '#319795', '#D69E2E'], wedgeprops=dict(width=0.45, edgecolor=HEX_FUNDO, linewidth=2), textprops=dict(fontsize=9, fontweight='bold'))
        plt.setp(at, color="white"); ax.add_artist(plt.Circle((0,0), 0.55, fc=HEX_FUNDO))
        ax.annotate(f"TOTAL\nR$ {val_tot/1000:,.0f}k", (0, 0), fontsize=12, fontweight='bold', ha='center', va='center', color=HEX_PRIMARIA); ax.axis('equal')
    buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor()); plt.close(fig); buf.seek(0); return buf

def plot_curva_s(g, m, val_tot):
    pesos = (g.iloc[:,1] / val_tot).tolist() if val_tot > 0 else [0]*len(g)
    dur = [max(m*p*2, m*0.2) if p>0 else 0 for p in pesos]
    starts = [0, dur[0]*0.3 if dur[0]>0 else 0, 0, 0, 0]
    for i in range(2, len(dur)): starts[i] = starts[i-1] + (dur[i-1]*0.4 if dur[i-1]>0 else 0)
    
    max_e = max([starts[i]+dur[i] for i in range(len(dur))]) if sum(dur)>0 else 0
    if max_e > m: starts = [s*(m/max_e) for s in starts]; dur = [d*(m/max_e) for d in dur]
    
    fig_c = plt.figure(figsize=(9, 3.2), facecolor=HEX_FUNDO); ax_c = fig_c.add_subplot(111)
    if max_e == 0: ax_c.axis('off')
    else:
        x_c = np.arange(0.5, m+0.5); p_prev = sum([starts[i]+(dur[i]/2) for i in range(len(dur)) if dur[i]>0])/sum(1 for d in dur if d>0)
        x = np.linspace(-2.5, 2.5, m); w = np.exp(-(x - ((p_prev/m)*4-2))**2); p_mensal = (w/w.sum())*100; p_acum = np.cumsum(p_mensal)
        ax_c.bar(x_c, p_mensal, color=HEX_SECUNDARIA, width=0.5); ax_l = ax_c.twinx(); ax_l.plot(x_c, p_acum, color=HEX_DESTAQUE, marker='o', lw=3)
        ax_c.set_xlim(0, m); ax_c.set_xticks(x_c); ax_c.set_xticklabels([f'Mês {i+1}' for i in range(m)]); ax_c.set_ylim(0, max(p_mensal)*1.2); ax_l.set_ylim(0, 110); ax_l.set_yticks([])
    buf_c = io.BytesIO(); plt.savefig(buf_c, format='png', dpi=200, bbox_inches='tight', facecolor=HEX_FUNDO); plt.close(); buf_c.seek(0)
    return buf_c

# ==========================================
# 4. GERADOR DE PDF
# ==========================================
def gerar_pdf(cli, loc, am2, af2, m_prazo, conf_cats, df, v_tot, buf_rosca, buf_curva):
    buf = io.BytesIO(); doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=40)
    styles = getSampleStyleSheet(); elem = []
    
    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=13, textColor=COR_PRIMARIA, spaceAfter=8)
    h2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=10, textColor=COR_DESTAQUE, spaceBefore=8, spaceAfter=4)
    b_b = ParagraphStyle('BB', fontName='Helvetica-Bold', fontSize=8.5, textColor=COR_TEXTO)
    b_n = ParagraphStyle('BN', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)
    b_w = ParagraphStyle('BW', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)
    
    # --- CAPA ---
    elem.append(HRFlowable(width="100%", thickness=3.5, color=COR_DESTAQUE, spaceAfter=15))
    if os.path.exists("logo.png"):
        try:
            ir = ImageReader("logo.png")
            iw, ih = ir.getSize(); nw = 3.0*inch; nh = nw/(iw/ih)
            if nh > 1.2*inch: nh = 1.2*inch; nw = nh*(iw/ih)
            elem.append(Image("logo.png", width=nw, height=nh))
        except: pass
    else:
        elem.append(Paragraph("AMÂNCIO", ParagraphStyle('L', fontName='Helvetica-Bold', fontSize=34, textColor=COR_PRIMARIA, alignment=1)))
        elem.append(Paragraph("CONSTRUTORA INTELIGENTE", ParagraphStyle('S', fontName='Helvetica-Bold', fontSize=10, textColor=COR_PRIMARIA, alignment=1, spaceAfter=15)))
    
    elem.append(Spacer(1, 15))
    elem.append(HRFlowable(width="35%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=25))
    elem.append(Paragraph("PROPOSTA COMERCIAL PARAMETRIZADA", ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=18, textColor=COR_PRIMARIA, alignment=1, spaceAfter=5)))
    elem.append(Paragraph("ENGENHARIA E EDIFICAÇÕES EM LIGHT STEEL FRAME", ParagraphStyle('ST', fontName='Helvetica-Bold', fontSize=11, textColor=COR_DESTAQUE, alignment=1, spaceAfter=25)))
    
    d_capa = [
        [Paragraph("<b>PROJETO / CLIENTE:</b>", b_b), Paragraph(cli.upper(), b_n)],
        [Paragraph("<b>LOCALIZAÇÃO:</b>", b_b), Paragraph(loc.upper(), b_n)],
        [Paragraph("<b>ÁREA CONSTRUIDA:</b>", b_b), Paragraph(f"{am2:,.2f} M²", b_n)],
        [Paragraph("<b>PRAZO DE EXECUÇÃO:</b>", b_b), Paragraph(f"{m_prazo} MESES", b_n)],
        [Paragraph("<b>VERSÃO DO DOCUMENTO:</b>", b_b), Paragraph("V6.3 — DOSSIÊ PARAMÉTRICO DB", b_n)]
    ]
    tc = Table(d_capa, colWidths=[150, 300])
    tc.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), COR_FUNDO), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')), ('PADDING', (0,0), (-1,-1), 6)]))
    elem.append(tc); elem.append(Spacer(1, 30))
    elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_PRIMARIA, spaceAfter=8))
    elem.append(Paragraph("AMÂNCIO CONSTRUTORA INTELIGENTE — ALTA ENGENHARIA", ParagraphStyle('F', fontName='Helvetica-Bold', fontSize=7.5, textColor=COR_PRIMARIA, alignment=1)))
    elem.append(PageBreak())
    
    # --- ÍNDICE ---
    elem.append(Paragraph("SUMÁRIO ANALÍTICO", h1))
    elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
    d_sum = [
        [Paragraph("<b>SEÇÃO</b>", b_w), Paragraph("<b>DESCRIÇÃO DO CONTEÚDO</b>", b_w)],
        [Paragraph("01", b_n), Paragraph("Capa Comercial Institucional e Dados do Projeto", b_n)],
        [Paragraph("02", b_n), Paragraph("Sumário e Apresentação da Amâncio LSF", b_n)],
        [Paragraph("03", b_n), Paragraph("Resumo Executivo e Categorias do Projeto (Escopo)", b_n)],
        [Paragraph("04", b_n), Paragraph("EAP: Estrutura Analítica de Preços e Subsistemas", b_n)],
        [Paragraph("05", b_n), Paragraph("Dashboards: Inteligência de Prazos e Desembolso (Curva S)", b_n)]
    ]
    ts = Table(d_sum, colWidths=[50, 410])
    ts.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), COR_PRIMARIA), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')), ('PADDING', (0,0), (-1,-1), 5)]))
    elem.append(ts); elem.append(PageBreak())
    
    # --- RESUMO EXECUTIVO E CATEGORIAS ---
    elem.append(Paragraph("RESUMO FINANCEIRO E DEFINIÇÕES DE PROJETO", h1))
    elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
    
    elem.append(Paragraph("CLASSIFICAÇÃO PARAMÉTRICA DO ORÇAMENTO", h2))
    elem.append(Paragraph("As categorias abaixo foram selecionadas para compor o nível de complexidade e padrão de entrega desta obra específica:", b_n))
    elem.append(Spacer(1, 5))
    
    d_cat = [
        [Paragraph("<b>GRUPO CONSTRUTIVO</b>", b_w), Paragraph("<b>PADRÃO / COMPLEXIDADE DEFINIDA</b>", b_w)],
        [Paragraph("Fundação e Infraestrutura", b_b), Paragraph(conf_cats['fund'], b_n)],
        [Paragraph("Estrutura LSF e Telhado", b_b), Paragraph(conf_cats['estr'], b_n)],
        [Paragraph("Instalações (Hidro/Elétrica/Clima)", b_b), Paragraph(conf_cats['inst'], b_n)],
        [Paragraph("Acabamentos e Revestimentos", b_b), Paragraph(conf_cats['acab'], b_n)]
    ]
    t_cat = Table(d_cat, colWidths=[180, 280])
    t_cat.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), COR_SECUNDARIA), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 4)]))
    elem.append(t_cat); elem.append(Spacer(1, 15))
    
    elem.append(Paragraph("SÍNTESE DE CUSTOS", h2))
    d_res = [
        [Paragraph("<b>VALOR TOTAL ESTIMADO DA OBRA:</b>", b_b), Paragraph(f"<b>R$ {v_tot:,.2f}</b>", b_b)],
        [Paragraph("<b>CUSTO ESTIMADO POR M² CONSTRUÍDO:</b>", b_b), Paragraph(f"R$ {v_tot/am2:,.2f} / m²", b_n)]
    ]
    t_res = Table(d_res, colWidths=[310, 150])
    t_res.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')), ('BOX', (0,0), (-1,-1), 1, COR_PRIMARIA), ('PADDING', (0,0), (-1,-1), 6)]))
    elem.append(t_res); elem.append(PageBreak())

    # --- EAP DETALHADA ---
    elem.append(Paragraph("EAP: ESTRUTURA ANALÍTICA DE PREÇOS", h1))
    elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
    
    d_tab = [[Paragraph("<b>ITEM / SUBSISTEMA CONSTRUTIVO</b>", b_w), Paragraph("<b>VALOR PARCIAL (R$)</b>", b_w), Paragraph("<b>PESO (%)</b>", b_w)]]
    for i, r in df.iterrows():
        pct = (r['CUSTO_FINAL'] / v_tot * 100) if v_tot > 0 else 0
        d_tab.append([Paragraph(r["SUBSISTEMA"], b_n), f"R$ {r['CUSTO_FINAL']:,.2f}", f"{pct:.1f}%"])
    d_tab.append([Paragraph("<b>TOTAL GERAL ESTIMADO</b>", b_b), Paragraph(f"<b>R$ {v_tot:,.2f}</b>", b_b), "<b>100%</b>"])
    
    t_det = Table(d_tab, colWidths=[260, 120, 80])
    t_det.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), COR_PRIMARIA), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,-1), (-1,-1), COR_FUNDO)]))
    elem.append(t_det); elem.append(PageBreak())

    # --- DASHBOARDS ---
    elem.append(Paragraph("DASHBOARDS E PLANEJAMENTO FINANCEIRO", h1))
    elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
    elem.append(Paragraph("COMPOSIÇÃO FINANCEIRA POR MACRO-ETAPAS", h2))
    elem.append(Image(buf_rosca, width=5.5*inch, height=2.75*inch))
    elem.append(Spacer(1, 10))
    elem.append(Paragraph("FLUXO DE DESEMBOLSO MENSAL E CURVA S ACUMULADA", h2))
    elem.append(Image(buf_curva, width=6.6*inch, height=2.3*inch))

    doc.build(elem, onFirstPage=lambda c, d: None, onLaterPages=lambda c, d: (c.saveState(), c.setFont('Helvetica-Bold', 8), c.setFillColor(COR_PRIMARIA), c.drawRightString(letter[0]-36, 25, f"Página {d.page}"), c.restoreState()))
    buf.seek(0); return buf.getvalue()

# ==========================================
# 5. INTERFACE DO USUÁRIO (STREAMLIT)
# ==========================================
with st.sidebar:
    st.write("### AMÂNCIO")
    st.success("Motor de Banco de Dados Ativo")
    st.info("Conectado à Planilha V6.2 Google Sheets")

st.write("### 📝 DADOS GERAIS DO PROJETO")
col1, col2 = st.columns(2)
cliente = col1.text_input("NOME DO CLIENTE / PROJETO:", value="RESIDENCIAL SILVA")
local = col2.text_input("LOCAL DA OBRA (CIDADE / UF):", value="JOINVILLE / SC")
col3, col4, col5 = st.columns(3)
area_m2 = col3.number_input("ÁREA CONSTRUÍDA (M²):", value=500.0, step=10.0)
area_fundacao_m2 = col4.number_input("ÁREA DA FUNDAÇÃO / PROJEÇÃO (M²):", value=250.0, step=10.0)
prazo_meses = col5.slider("PRAZO DA OBRA (MESES):", 3, 12, 6)

st.write("---")
st.write("### 🎛️ ENGENHARIA PARAMÉTRICA (CLASSIFICAÇÃO POR GRUPOS)")
st.info("O sistema agora lê os valores absolutos (em Reais) diretamente do banco de dados (Planilha Google Sheets) para cada nível de complexidade selecionado abaixo.")

# Mapeamento do Selectbox para a Coluna do Banco de Dados
map_niveis = {
    "Leve / Simples / Básica / Comum": "BAIXO",
    "Moderada / Padrão / Padrão de Entrega": "MEDIO",
    "Pesada / Complexa / Alta Tecnologia / Altíssimo Luxo": "ALTO"
}

c_cat1, c_cat2 = st.columns(2)
with c_cat1:
    st.markdown("**1. Fundação e Infraestrutura**")
    cat_fund = st.selectbox("Tipo de Solo e Carga:", ["Leve / Simples / Básica / Comum", "Moderada / Padrão / Padrão de Entrega", "Pesada / Complexa / Alta Tecnologia / Altíssimo Luxo"], index=1, key='f')
    st.markdown("**2. Instalações (Elétrica, Hidro, Clima)**")
    cat_inst = st.selectbox("Nível de Tecnologia:", ["Leve / Simples / Básica / Comum", "Moderada / Padrão / Padrão de Entrega", "Pesada / Complexa / Alta Tecnologia / Altíssimo Luxo"], index=1, key='i')

with c_cat2:
    st.markdown("**3. Estrutura LSF e Cobertura**")
    cat_estr = st.selectbox("Arquitetura e Vãos:", ["Leve / Simples / Básica / Comum", "Moderada / Padrão / Padrão de Entrega", "Pesada / Complexa / Alta Tecnologia / Altíssimo Luxo"], index=1, key='e')
    st.markdown("**4. Acabamentos e Revestimentos**")
    cat_acab = st.selectbox("Padrão de Entrega:", ["Leve / Simples / Básica / Comum", "Moderada / Padrão / Padrão de Entrega", "Pesada / Complexa / Alta Tecnologia / Altíssimo Luxo"], index=1, key='a')

bdi = st.slider("MARGEM DA CONSTRUTORA / BDI (%):", 10, 35, 20) / 100.0

if st.button("🚀 CALCULAR E GERAR DOSSIÊ", use_container_width=True, type="primary"):
    with st.spinner("Lendo banco de dados de preços da planilha e calculando..."):
        df_base = carregar_valores()
        
        # Converte as escolhas da tela em textos (BAIXO, MEDIO, ALTO)
        nv_fund = map_niveis[cat_fund]
        nv_estr = map_niveis[cat_estr]
        nv_inst = map_niveis[cat_inst]
        nv_acab = map_niveis[cat_acab]
        
        custos_finais = []
        for i, r in df_base.iterrows():
            sub = str(r["SUBSISTEMA"]).upper()
            pref = sub[:2]
            consumo = float(r.get("CONSUMO_MEDIO_M2", 1.0))
            
            # DESCUBRA QUAL NÍVEL APLICAR NESTA LINHA
            if pref in ['05', '09']: nivel_atual = nv_fund
            elif pref in ['06', '08']: nivel_atual = nv_estr
            elif pref in ['07', '10', '11', '12']: nivel_atual = nv_inst
            elif pref in ['13', '14', '15', '16', '17']: nivel_atual = nv_acab
            else: nivel_atual = "MEDIO" # Canteiro sempre Padrão
            
            # PUXA O VALOR EXATO DO BANCO DE DADOS (Ou 0 se não achar)
            c_mat = float(r.get(f"MAT_{nivel_atual}", r.get("MAT_MEDIO", 0)))
            c_mo = float(r.get(f"MO_{nivel_atual}", r.get("MO_MEDIO", 0)))
            
            area = area_fundacao_m2 if pref in ['05', '09'] else area_m2
            
            # CÁLCULO DIRETO (Valor Unitário Absoluto * Consumo * Area * BDI)
            custo_item = (consumo * c_mat * area * (1+bdi)) + (consumo * c_mo * area * (1+bdi))
            custos_finais.append(custo_item)
            
        df_val = df_base.copy()
        df_val["CUSTO_FINAL"] = custos_finais
        v_tot = sum(custos_finais)
        
        # Dashboards
        gm = agrupar_macro(df_val, 'CUSTO_FINAL')
        buf_rosca = plot_rosca(gm, v_tot)
        buf_curva = plot_curva_s(gm, prazo_meses, v_tot)
        
        # Para ficar bonito no PDF
        txt_map = {"BAIXO": "BÁSICA / COMUM", "MEDIO": "PADRÃO", "ALTO": "COMPLEXA / LUXO"}
        conf_cats = {'fund': txt_map[nv_fund], 'estr': txt_map[nv_estr], 'inst': txt_map[nv_inst], 'acab': txt_map[nv_acab]}
        
        pdf = gerar_pdf(cliente, local, area_m2, area_fundacao_m2, prazo_meses, conf_cats, df_val, v_tot, buf_rosca, buf_curva)
        
        st.success("✅ ORÇAMENTO PROCESSADO COM SUCESSO!")
        st.download_button("📥 BAIXAR NOVO DOSSIÊ (V6.3)", data=pdf, file_name=f"ORCAMENTO_AMANCIO_{cliente.replace(' ','_')}.pdf", mime="application/pdf", use_container_width=True)
