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

st.set_page_config(page_title="AMÂNCIO - ORÇAMENTADOR LSF V5.5", page_icon="🏗️", layout="wide")

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

URL_VALORES = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv&gid=0"
URL_MEMORIAL = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv&gid=819485538"

@st.cache_data(ttl=15)
def carregar_valores():
    try:
        df = pd.read_csv(URL_VALORES)
        df.columns = df.columns.str.strip().str.upper()
        if len(df) >= 10: return df
    except: pass
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

df_base = carregar_valores()
n_itens = len(df_base)

if 'escopo_status' not in st.session_state:
    st.session_state.escopo_status = ["COMPLETO (MAT + M.O.)"] * n_itens

def att_status(val):
    st.session_state.escopo_status = [val] * n_itens

def card_etapa(prefix):
    for ext in ['.jpg', '.png']:
        if os.path.exists(f"img_{prefix}{ext}"):
            try: return ImageReader(f"img_{prefix}{ext}")
            except: pass
    fig, ax = plt.subplots(figsize=(4.5, 3.2), facecolor='#0F2C3D')
    ax.axis('off')
    if prefix in ['01', '02', '03', '04']: ax.text(0.5, 0.5, "CANTEIRO E GESTÃO", color='white', ha='center')
    elif prefix in ['05', '09']: ax.text(0.5, 0.5, "RADIER E FUNDAÇÃO", color='white', ha='center')
    elif prefix in ['06', '08']: ax.text(0.5, 0.5, "ESTRUTURA LSF E TELHADO", color='white', ha='center')
    elif prefix in ['07', '10', '11', '12']: ax.text(0.5, 0.5, "INSTALAÇÕES E VEDAÇÃO", color='white', ha='center')
    else: ax.text(0.5, 0.5, "ACABAMENTOS", color='white', ha='center')
    ax.text(0.5, 0.2, "ILUSTRAÇÃO TÉCNICA", color='#CBD5E0', fontsize=8, ha='center')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0F2C3D')
    plt.close(fig); buf.seek(0)
    return ImageReader(buf)

def agrupar_macro(df, col_val):
    m_map = {'01':'1. Canteiro', '02':'1. Canteiro', '03':'1. Canteiro', '04':'1. Canteiro', '05':'2. Fundação', '09':'2. Fundação', '06':'3. Estrutura/Telhado', '08':'3. Estrutura/Telhado', '07':'4. Instalações/Vedação', '10':'4. Instalações/Vedação', '11':'4. Instalações/Vedação', '12':'4. Instalações/Vedação'}
    df_m = df.copy()
    df_m['MACRO'] = df_m['SUBSISTEMA'].apply(lambda x: m_map.get(str(x)[:2], '5. Acabamentos'))
    g = df_m.groupby('MACRO')[col_val].sum().reset_index()
    return g

def plot_rosca(g, val_tot, label):
    fig = plt.figure(figsize=(8, 4), facecolor=HEX_FUNDO); ax = fig.add_subplot(111)
    if val_tot == 0: ax.text(0.5, 0.5, "SEM ITENS SELECIONADOS", ha='center', va='center', color=HEX_PRIMARIA, fontweight='bold'); ax.axis('off')
    else:
        w, t, at = ax.pie(g.iloc[:,1], labels=g['MACRO'], autopct='%1.1f%%', startangle=140, colors=[HEX_PRIMARIA, HEX_SECUNDARIA, HEX_DESTAQUE, '#319795', '#D69E2E'], wedgeprops=dict(width=0.45, edgecolor=HEX_FUNDO, linewidth=2), textprops=dict(fontsize=9, fontweight='bold'))
        plt.setp(at, color="white"); ax.add_artist(plt.Circle((0,0), 0.55, fc=HEX_FUNDO))
        ax.annotate(f"TOTAL {label}\nR$ {val_tot/1000:,.0f}k", (0, 0), fontsize=10, fontweight='bold', ha='center', va='center', color=HEX_PRIMARIA); ax.axis('equal')
    buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor()); plt.close(fig); buf.seek(0); return buf

def plot_gantt_curva(g, m, val_tot):
    pesos = (g.iloc[:,1] / val_tot).tolist() if val_tot > 0 else [0]*len(g)
    dur = [max(m*p*2, m*0.2) if p>0 else 0 for p in pesos]
    starts = [0, dur[0]*0.3 if dur[0]>0 else 0, 0, 0, 0]
    for i in range(2, len(dur)): starts[i] = starts[i-1] + (dur[i-1]*0.4 if dur[i-1]>0 else 0)
    
    max_e = max([starts[i]+dur[i] for i in range(len(dur))]) if sum(dur)>0 else 0
    if max_e > m: starts = [s*(m/max_e) for s in starts]; dur = [d*(m/max_e) for d in dur]
    
    fig_g = plt.figure(figsize=(9, 2.5), facecolor=HEX_FUNDO); ax_g = fig_g.add_subplot(111)
    if max_e == 0: ax_g.axis('off')
    else:
        for i in range(len(dur)):
            if dur[i]>0: ax_g.add_patch(patches.Rectangle((starts[i], len(dur)-i-1), dur[i], 0.7, facecolor=HEX_SECUNDARIA)); ax_g.text(starts[i]+0.1, len(dur)-i-0.65, g['MACRO'].tolist()[i], color='white', fontsize=8, fontweight='bold')
        ax_g.set_xlim(0, m); ax_g.set_ylim(-0.5, len(dur)); ax_g.set_xticks(range(0, m+1)); ax_g.set_xticklabels([f'Mês {i}' for i in range(m+1)]); ax_g.grid(axis='x', alpha=0.3); ax_g.set_yticks([])
    buf_g = io.BytesIO(); plt.savefig(buf_g, format='png', dpi=200, bbox_inches='tight', facecolor=HEX_FUNDO); plt.close(); buf_g.seek(0)
    
    fig_c = plt.figure(figsize=(9, 2.8), facecolor=HEX_FUNDO); ax_c = fig_c.add_subplot(111)
    if max_e == 0: ax_c.axis('off')
    else:
        x_c = np.arange(0.5, m+0.5); p_prev = sum([starts[i]+(dur[i]/2) for i in range(len(dur)) if dur[i]>0])/sum(1 for d in dur if d>0)
        x = np.linspace(-2.5, 2.5, m); w = np.exp(-(x - ((p_prev/m)*4-2))**2); p_mensal = (w/w.sum())*100; p_acum = np.cumsum(p_mensal)
        ax_c.bar(x_c, p_mensal, color=HEX_SECUNDARIA, width=0.5); ax_l = ax_c.twinx(); ax_l.plot(x_c, p_acum, color=HEX_DESTAQUE, marker='o', lw=3)
        ax_c.set_xlim(0, m); ax_c.set_xticks(x_c); ax_c.set_xticklabels([f'Mês {i+1}' for i in range(m)]); ax_c.set_ylim(0, max(p_mensal)*1.2); ax_l.set_ylim(0, 110); ax_l.set_yticks([])
    buf_c = io.BytesIO(); plt.savefig(buf_c, format='png', dpi=200, bbox_inches='tight', facecolor=HEX_FUNDO); plt.close(); buf_c.seek(0)
    return buf_g, buf_c

def pdf_b(cli, loc, am2, af2, tf, pdr, df, df_m, v_mer, v_con, tm_c, tmo_c, m, ex_s, g_m, g_c):
    buf = io.BytesIO(); doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=40)
    styles = getSampleStyleSheet(); elem = []
    
    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=13, textColor=COR_PRIMARIA, spaceAfter=8)
    h2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=10, textColor=COR_DESTAQUE, spaceBefore=8, spaceAfter=4)
    b_b = ParagraphStyle('BB', fontName='Helvetica-Bold', fontSize=8, textColor=COR_TEXTO)
    b_n = ParagraphStyle('BN', fontName='Helvetica', fontSize=8, textColor=COR_TEXTO)
    
    # 1. CAPA E INFOS
    elem.append(HRFlowable(width="100%", thickness=3.5, color=COR_DESTAQUE, spaceAfter=15))
    elem.append(Paragraph("PROPOSTA COMERCIAL PRELIMINAR - STEEL FRAME", ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=16, textColor=COR_PRIMARIA, alignment=1, spaceAfter=20)))
    d_capa = [[Paragraph("<b>CLIENTE:</b>", b_b), Paragraph(cli, b_n)], [Paragraph("<b>LOCAL:</b>", b_b), Paragraph(loc, b_n)], [Paragraph("<b>ÁREA:</b>", b_b), Paragraph(f"{am2} m²", b_n)], [Paragraph("<b>PRAZO:</b>", b_b), Paragraph(f"{m} MESES", b_n)]]
    t_capa = Table(d_capa, colWidths=[100, 350]); t_capa.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), COR_FUNDO), ('PADDING', (0,0), (-1,-1), 6)]))
    elem.append(t_capa); elem.append(PageBreak())
    
    # 2. PROPOSTA FINANCEIRA (COM NOTA)
    elem.append(Paragraph("RESUMO FINANCEIRO E ESCOPO", h1))
    
    # NOTA DE RESSALVA
    aviso = "<font color='white'><b>NOTA TÉCNICA/COMERCIAL (ESTIMATIVA INICIAL)</b><br/>Este documento é um balizamento estimado baseado em parâmetros de mercado. Valores definitivos exigem aprovação dos Projetos Executivos. Os itens identificados como 'NÃO INCLUSOS' no contrato servem para programação financeira do cliente e não fazem parte da nossa responsabilidade.</font>"
    t_aviso = Table([[Paragraph(aviso, b_b)]], colWidths=[450]); t_aviso.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#C53030')), ('PADDING', (0,0), (-1,-1), 6)]))
    elem.append(t_aviso); elem.append(Spacer(1, 15))
    
    d_res = [[Paragraph("<b>VALOR TOTAL DA OBRA (ESTIMATIVA MERCADO):</b>", b_b), Paragraph(f"R$ {v_mer:,.2f}", b_b)], [Paragraph("<b>VALOR CONTRATO AMÂNCIO (SEU ESCOPO):</b>", b_b), Paragraph(f"<font color='{HEX_DESTAQUE}'>R$ {v_con:,.2f}</font>", b_b)]]
    t_res = Table(d_res, colWidths=[330, 120]); t_res.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')), ('BOX', (0,0), (-1,-1), 1, COR_PRIMARIA), ('PADDING', (0,0), (-1,-1), 5)]))
    elem.append(t_res); elem.append(Spacer(1, 15))
    
    d_tab = [[Paragraph("<b>ETAPA</b>", ParagraphStyle('W', fontName='Helvetica-Bold', fontSize=7, textColor=colors.white)), Paragraph("<b>CONTRATO</b>", ParagraphStyle('W', fontName='Helvetica-Bold', fontSize=7, textColor=colors.white)), Paragraph("<b>V. CONTRATO</b>", ParagraphStyle('W', fontName='Helvetica-Bold', fontSize=7, textColor=colors.white)), Paragraph("<b>MERCADO</b>", ParagraphStyle('W', fontName='Helvetica-Bold', fontSize=7, textColor=colors.white))]]
    for i, r in df.iterrows():
        s = r["STATUS"]
        if "NÃO" in s: sf = f'<font color="{HEX_DESTAQUE}">{s}</font>'
        elif "COMP" in s: sf = f'<font color="{HEX_PRIMARIA}">{s}</font>'
        else: sf = f'<font color="{HEX_SECUNDARIA}">{s}</font>'
        d_tab.append([Paragraph(r["SUBSISTEMA"], ParagraphStyle('x', fontSize=7)), Paragraph(sf, ParagraphStyle('x', fontSize=7)), f"R$ {r['TOTAL_CONTRATO']:,.2f}", f"R$ {r['TOTAL_MERCADO']:,.2f}"])
    d_tab.append([Paragraph("<b>TOTAL</b>", b_b), "", Paragraph(f"<b>R$ {v_con:,.2f}</b>", b_b), Paragraph(f"<b>R$ {v_mer:,.2f}</b>", b_b)])
    t_det = Table(d_tab, colWidths=[180, 110, 80, 80]); t_det.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), COR_PRIMARIA), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 3)]))
    elem.append(t_det); elem.append(PageBreak())
    
    # 3. DASHBOARDS
    elem.append(Paragraph("DASHBOARDS: VISÃO GLOBAL (100% DA OBRA)", h1))
    elem.append(Image(g_m[0], width=5*inch, height=2.5*inch)); elem.append(Image(g_m[1], width=6*inch, height=1.7*inch)); elem.append(Image(g_m[2], width=6*inch, height=1.9*inch)); elem.append(PageBreak())
    
    elem.append(Paragraph("DASHBOARDS: VISÃO DO SEU CONTRATO AMÂNCIO", h1))
    elem.append(Image(g_c[0], width=5*inch, height=2.5*inch)); elem.append(Image(g_c[1], width=6*inch, height=1.7*inch)); elem.append(Image(g_c[2], width=6*inch, height=1.9*inch)); elem.append(PageBreak())
    
    # 4. MEMORIAL
    elem.append(Paragraph("CATÁLOGO DE ESCOPO E MEMORIAL", h1))
    if df_m.empty: elem.append(Paragraph("Sem itens de memorial.", b_n))
    else:
        col_it = 'ITEM' if 'ITEM' in df_m.columns else df_m.columns[2]
        col_ob = 'OBSERVACAO' if 'OBSERVACAO' in df_m.columns else (df_m.columns[4] if len(df_m.columns)>4 else df_m.columns[-1])
        for i, r in df.iterrows():
            pref = str(r["SUBSISTEMA"])[:2]; f = df_m[df_m['CODIGO'] == pref]
            if not f.empty:
                img_f = Image(card_etapa(pref), width=2.0*inch, height=1.4*inch)
                md = [[Paragraph("<b>ITEM</b>", b_b), Paragraph("<b>OBSERVAÇÃO</b>", b_b)]]
                for _, ir in f.iterrows():
                    if str(ir.get(col_it, '')) != "nan": md.append([Paragraph(str(ir.get(col_it, '')), b_n), Paragraph(str(ir.get(col_ob, '-')), b_n)])
                tm = Table(md, colWidths=[120, 180]); tm.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), COR_SECUNDARIA), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 3)]))
                lt = Table([[[Paragraph(r["SUBSISTEMA"], h2), Spacer(1,3), tm], img_f]], colWidths=[310, 160])
                lt.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,-1), 'RIGHT')]))
                elem.append(lt); elem.append(Spacer(1, 15))

    doc.build(elem); buf.seek(0); return buf.getvalue()

# INTERFACE
with st.sidebar:
    st.write("### AMÂNCIO")
    st.success("Planilha Conectada")

st.write("### 📝 DADOS E RESSALVA COMERCIAL")
st.error("🚨 **NOTA:** Os valores apresentados são ESTIMATIVAS de viabilidade técnica. O orçamento definitivo e o escopo dependem 100% da conclusão dos Projetos Executivos.")

col1, col2 = st.columns(2)
cliente = col1.text_input("NOME DO CLIENTE:", value="RESIDENCIAL SILVA")
local = col2.text_input("LOCAL DA OBRA:", value="JOINVILLE / SC")
col3, col4 = st.columns(2)
area_m2 = col3.number_input("ÁREA (M²):", value=500.0, step=10.0)
padrao = col4.selectbox("PADRÃO GERAL:", ["BAIXO", "MÉDIO", "ALTO"], index=1)

st.write("### 🏗️ FUNDAÇÃO E PRAZO")
col5, col6 = st.columns(2)
area_fundacao_m2 = col5.number_input("ÁREA FUNDAÇÃO (M²):", value=250.0)
tipo_fundacao = col6.selectbox("FUNDAÇÃO:", ["LEVE (SOLO BOM)", "MODERADA", "PESADA (ESTACAS)"], index=1)
prazo_meses = st.slider("PRAZO OBRA (MESES):", 3, 12, 6)

st.write("### 🎛️ ESCOPO DE CONTRATO (MARCAÇÃO RÁPIDA)")
bc1, bc2, bc3, bc4 = st.columns(4)
bc1.button("✅ Tudo (Mat+M.O.)", on_click=att_status, args=("COMPLETO (MAT + M.O.)",), use_container_width=True)
bc2.button("👷 Só M.O.", on_click=att_status, args=("SÓ MÃO DE OBRA",), use_container_width=True)
bc3.button("🧱 Só Material", on_click=att_status, args=("SÓ MATERIAL",), use_container_width=True)
bc4.button("❌ Zerar Tudo", on_click=att_status, args=("NÃO INCLUSO",), use_container_width=True)

df_opcoes = pd.DataFrame({"SUBSISTEMA": df_base["SUBSISTEMA"], "STATUS DO CONTRATO": st.session_state.escopo_status})
df_ed = st.data_editor(df_opcoes, hide_index=True, use_container_width=True, column_config={"STATUS DO CONTRATO": st.column_config.SelectboxColumn("STATUS DO CONTRATO", options=["COMPLETO (MAT + M.O.)", "SÓ MATERIAL", "SÓ MÃO DE OBRA", "NÃO INCLUSO"])})
st.session_state.escopo_status = df_ed["STATUS DO CONTRATO"].tolist()

bdi = st.slider("BDI (%):", 10, 35, 20) / 100.0
subm = st.button("🚀 GERAR DOSSIÊ", use_container_width=True, type="primary")

if subm:
    with st.spinner("Processando..."):
        df_mem = carregar_memorial()
        df_val = df_base.copy()
        
        f_pdr = 0.85 if padrao=="BAIXO" else (1.0 if padrao=="MÉDIO" else 1.3)
        f_fun = 0.85 if "LEVE" in tipo_fundacao else (1.35 if "PESADA" in tipo_fundacao else 1.0)
        
        cm_m, cmo_m, cm_c, cmo_c = [], [], [], []
        for i, r in df_val.iterrows():
            sb = str(r["SUBSISTEMA"])
            c, cm, cmo = r["CONSUMO_MEDIO_M2"], r["CUSTO_MAT_UNIT_RS"], r["CUSTO_MO_UNIT_RS"]
            a = area_fundacao_m2 if "FUND" in sb or "INFRA" in sb else area_m2
            fe = f_fun if "FUND" in sb or "INFRA" in sb else 1.0
            
            mt_i = c * cm * f_pdr * fe * a * (1+bdi)
            mo_i = c * cmo * f_pdr * fe * a * (1+bdi)
            cm_m.append(mt_i); cmo_m.append(mo_i)
            
            s = st.session_state.escopo_status[i]
            if s == "COMPLETO (MAT + M.O.)": cm_c.append(mt_i); cmo_c.append(mo_i)
            elif s == "SÓ MATERIAL": cm_c.append(mt_i); cmo_c.append(0)
            elif s == "SÓ MÃO DE OBRA": cm_c.append(0); cmo_c.append(mo_i)
            else: cm_c.append(0); cmo_c.append(0)

        df_val["TOTAL_MERCADO"] = [x+y for x,y in zip(cm_m, cmo_m)]
        df_val["MAT_CONTRATO"] = cm_c
        df_val["MO_CONTRATO"] = cmo_c
        df_val["TOTAL_CONTRATO"] = [x+y for x,y in zip(cm_c, cmo_c)]
        df_val["STATUS"] = st.session_state.escopo_status
        
        v_mer = sum(df_val["TOTAL_MERCADO"]); v_con = sum(df_val["TOTAL_CONTRATO"])
        
        gm = agrupar_macro(df_val, 'TOTAL_MERCADO')
        gc = agrupar_macro(df_val, 'TOTAL_CONTRATO')
        
        g1 = [plot_rosca(gm, v_mer, "MERCADO"), *plot_gantt_curva(gm, prazo_meses, v_mer)]
        g2 = [plot_rosca(gc, v_con, "CONTRATO"), *plot_gantt_curva(gc, prazo_meses, v_con)]
        
        pdf = pdf_b(cliente, local, area_m2, area_fundacao_m2, tipo_fundacao, padrao, df_val, df_mem, v_mer, v_con, sum(cm_c), sum(cmo_c), prazo_meses, False, g1, g2)
        st.success("✅ GERADO!")
        st.download_button("📥 BAIXAR PDF", data=pdf, file_name=f"ORCAMENTO_{cliente}.pdf", mime="application/pdf", use_container_width=True)
