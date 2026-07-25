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

# ==========================================
# 1. CONFIGURAÇÕES GERAIS E CORES
# ==========================================
st.set_page_config(page_title="AMÂNCIO - ORÇAMENTADOR LSF V8.2", page_icon="🏗️", layout="wide")

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

URL_VALORES = "https://docs.google.com/spreadsheets/d/1kA4NHJ8VU3eDnipJ0ADArTWzm0YOFhD_t4FT1_nuHX4/export?format=csv&gid=0"
URL_MEMORIAL = "https://docs.google.com/spreadsheets/d/1ovEvMmtrE4VVaXaxQQlUh0I7bAkbQKNL-cBEPgwGDR4/export?format=csv&gid=819485538"

# ==========================================
# DICIONÁRIOS DE ESPECIFICAÇÕES TÉCNICAS
# ==========================================
DESC_CATS = {
    'fund': {
        'titulo': '1. FUNDAÇÃO E INFRAESTRUTURA',
        'BAIXO': '<b>Leve / Básica:</b> Terreno plano e firme. Utiliza Radier simples de concreto armado com espessura padrão, sem necessidade de estacas profundas ou muros de arrimo complexos.',
        'MEDIO': '<b>Moderada / Padrão:</b> Terreno com leve declive ou resistência mediana. Exige Radier reforçado com vigas de bordo ou estacas rasas de apoio.',
        'ALTO': '<b>Pesada / Complexa:</b> Terreno com desnível acentuado ou solo frágil. Demanda estacas profundas, blocos de coroamento, vigas baldrame robustas e/ou muros de contenção estruturais.'
    },
    'estr': {
        'titulo': '2. ESTRUTURA LSF E COBERTURA',
        'BAIXO': '<b>Simples / Básica:</b> Arquitetura predominante retangular com vãos curtos. Otimiza o consumo de aço com treliças padronizadas e telhado com beirais convencionais.',
        'MEDIO': '<b>Moderada / Padrão:</b> Arquitetura residencial típica. Contempla platibandas, vãos moderados (até 5m livres) e mezaninos residenciais.',
        'ALTO': '<b>Complexa / Alto Padrão:</b> Projetos arrojados com grandes vãos livres, balanços estruturais, pé-direito duplo e fachada imponente. Exige perfis de aço com maior espessura e vigas treliçadas robustas.'
    },
    'inst': {
        'titulo': '3. INSTALAÇÕES (HIDRO, ELÉTRICA E CLIMA)',
        'BAIXO': '<b>Básica / Convencional:</b> Quantidade padrão de pontos elétricos/iluminação, distribuição hidráulica simples e infraestrutura para ar-condicionado focada apenas nos dormitórios.',
        'MEDIO': '<b>Moderada / Padrão:</b> Circuitos elétricos amplos e segmentados, água quente em torneiras (monocomando), rede de dados estruturada e infra de ar-condicionado em toda a edificação.',
        'ALTO': '<b>Alta Tecnologia:</b> Altíssima densidade de tomadas, quadros dedicados para automação residencial, aquecimento de piso, pressurização potente e infraestrutura para ar dutado.'
    },
    'acab': {
        'titulo': '4. ACABAMENTOS E REVESTIMENTOS',
        'BAIXO': '<b>Comum / Comercial:</b> Revestimentos e pisos cerâmicos padronizados, esquadrias de alumínio em linha básica, portas lisas e pintura convencional.',
        'MEDIO': '<b>Alto Padrão:</b> Porcelanatos padrão (ex: 80x80cm), esquadrias de alumínio Linha Gold/Suprema, pintura acrílica premium e louças/metais de alta qualidade e durabilidade.',
        'ALTO': '<b>Altíssimo Luxo:</b> Pedras naturais (Mármores/Granitos), porcelanatos de grandes formatos (ex: 120x120cm+), esquadrias de PVC acústicas e fechaduras eletrônicas / acabamentos premium.'
    }
}

DESC_INSUMOS = {
    '01': "Abrange a preparação inicial do terreno, ligações provisórias (padrão de água e energia), locação topográfica, limpeza do lote e fechamento frontal com tapumes.",
    '02': "Contempla os custos gerenciais indiretos: aprovações, emissão de ARTs (Anotação de Responsabilidade Técnica), taxas de prefeitura e remuneração da equipe de gestão (engenheiro e mestre de obras).",
    '03': "Envolve a montagem da infraestrutura de apoio à equipe de construção, como instalação de contêineres/barracão, banheiro químico, refeitório provisório e local seguro para armazenagem de materiais.",
    '04': "Custos logísticos com fretes, caçambas de descarte durante a execução, e locação de maquinários diários (betoneiras, rompedores, andaimes e escoramentos).",
    '05': "Composição da base de contato com o solo que receberá a montagem LSF. Inclui concreto usinado (FCK adequado), armaduras (malhas pop ou treliças), lona plástica preta, fôrmas, e possíveis estacas escavadas/brocas.",
    '06': "O esqueleto principal e portante da edificação. Constituído 100% por perfis formados a frio em aço galvanizado (revestimento mínimo Z275), parafusos estruturais autoperfurantes, fitas de ancoragem tensionadas e chumbadores químicos/mecânicos.",
    '07': "Sistema multicamadas que atua como as 'paredes' do projeto. Compreende placas estruturais OSB, membrana hidrófuga respirável (ex: Tyvek), isolamento termoacústico interno (Lã de Vidro ou PET), placas cimentícias (face externa), chapas de gesso acartonado/Drywall (face interna) e fitas/massas para tratamento de juntas.",
    '08': "Composição superior da obra, incluindo estrutura do telhado (tesouras em LSF), mantas de subcobertura, telhas escolhidas (shingle, metálica termoacústica ou fibrocimento), além da funilaria completa (calhas, rufos e pingadeiras).",
    '09': "Etapa de blindagem contra umidade. Aplicação de mantas asfálticas, fitas butílicas de alta adesão e impermeabilizantes líquidos/cimentícios nas áreas úmidas (banheiros/lavanderia) e nas faixas de contato do radier.",
    '10': "Malha de fluidos da edificação. Tubulações e conexões de água fria e quente (em PVC, PPR ou PEX termofundido), tubos de esgoto, caixas sifonadas, ralos invisíveis/lineares, registros de gaveta/pressão e caixas d'água.",
    '11': "Sistema de energia e dados. Inclui eletrodutos flexíveis corrugados (anti-chama) e rígidos, caixas de passagem e derivação, cabeamento em cobre flexível, disjuntores DIN, DR, quadros de distribuição (QDC) e hastes para malha de aterramento.",
    '12': "Infraestrutura frigorígena (tubulação de cobre para os splits), revestimento de isolamento térmico (esponjoso), cabeamento PP de comando entre unidades e sistema de drenos em PVC para escoamento de condensado.",
    '13': "Tratamento de embelezamento de paredes e forros. Inclui aplicação de massas (corrida/acrílica), lixamento, tintas premium, texturas/grafiatos externos, assentamento de revestimentos cerâmicos, argamassas colantes (ACII/ACIII) e rejuntamentos.",
    '14': "Preparo da base (contrapiso leve de regularização), aplicação de primer, assentamento de pisos (porcelanatos, vinílicos ou laminados), além de instalação de rodapés e soleiras/baguetes em pedra.",
    '15': "Fechamentos de vãos. Esquadrias externas (janelas e portas em alumínio ou PVC), portas internas prontas (madeira estruturada), vidros (temperados e laminados) e todo o conjunto de ferragens e fechaduras.",
    '16': "Tratamento final da área externa do lote. Calçadas e pavimentação externa, preparação de terra/grama para paisagismo básico, muros de divisa, pintura externa e instalação de portões.",
    '17': "Remoção fina de detritos, contratação de limpeza especializada pós-obra (higienização de vidros, polimento de porcelanatos, desinfecção de louças e metais) preparando o imóvel para a entrega das chaves ao cliente."
}

# ==========================================
# 2. CARREGAMENTO DE DADOS (DB ABSOLUTO)
# ==========================================
@st.cache_data(ttl=15)
def carregar_valores():
    try:
        df = pd.read_csv(URL_VALORES)
        df.columns = df.columns.str.strip().str.upper()
        if "MAT_BAIXO" in df.columns and len(df) >= 10: 
            return df
    except: pass
    
    return pd.DataFrame([
        {"SUBSISTEMA": "01. SERVIÇOS PRELIMINARES", "CATEGORIA": "CANTEIRO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 15.0, "MAT_MEDIO": 25.0, "MAT_ALTO": 40.0, "MO_BAIXO": 20.0, "MO_MEDIO": 30.0, "MO_ALTO": 45.0},
        {"SUBSISTEMA": "02. GESTÃO DE OBRA E ADM", "CATEGORIA": "CANTEIRO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 5.0, "MAT_MEDIO": 10.0, "MAT_ALTO": 20.0, "MO_BAIXO": 80.0, "MO_MEDIO": 120.0, "MO_ALTO": 180.0},
        {"SUBSISTEMA": "03. INSTALAÇÕES DO CANTEIRO", "CATEGORIA": "CANTEIRO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 20.0, "MAT_MEDIO": 30.0, "MAT_ALTO": 45.0, "MO_BAIXO": 15.0, "MO_MEDIO": 25.0, "MO_ALTO": 35.0},
        {"SUBSISTEMA": "04. LOCAÇÕES E EQUIPAMENTOS", "CATEGORIA": "CANTEIRO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 25.0, "MAT_MEDIO": 45.0, "MAT_ALTO": 75.0, "MO_BAIXO": 5.0, "MO_MEDIO": 10.0, "MO_ALTO": 15.0},
        {"SUBSISTEMA": "05. INFRAESTRUTURA (FUNDAÇÃO)", "CATEGORIA": "FUNDACAO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 140.0, "MAT_MEDIO": 200.0, "MAT_ALTO": 320.0, "MO_BAIXO": 80.0, "MO_MEDIO": 110.0, "MO_ALTO": 160.0},
        {"SUBSISTEMA": "06. SUPERESTRUTURA LSF", "CATEGORIA": "ESTRUTURA", "CONSUMO_MEDIO_M2": 30.0, "MAT_BAIXO": 10.0, "MAT_MEDIO": 12.5, "MAT_ALTO": 16.0, "MO_BAIXO": 4.0, "MO_MEDIO": 5.0, "MO_ALTO": 7.5},
        {"SUBSISTEMA": "07. FECHAMENTOS (EXT/INT)", "CATEGORIA": "VEDACOES", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 160.0, "MAT_MEDIO": 220.0, "MAT_ALTO": 310.0, "MO_BAIXO": 80.0, "MO_MEDIO": 110.0, "MO_ALTO": 150.0},
        {"SUBSISTEMA": "08. COBERTURA E TELHADO", "CATEGORIA": "ESTRUTURA", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 90.0, "MAT_MEDIO": 140.0, "MAT_ALTO": 220.0, "MO_BAIXO": 45.0, "MO_MEDIO": 65.0, "MO_ALTO": 90.0},
        {"SUBSISTEMA": "09. IMPERMEABILIZAÇÕES", "CATEGORIA": "FUNDACAO", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 25.0, "MAT_MEDIO": 40.0, "MAT_ALTO": 70.0, "MO_BAIXO": 15.0, "MO_MEDIO": 25.0, "MO_ALTO": 40.0},
        {"SUBSISTEMA": "10. INSTALAÇÕES HIDRÁULICAS", "CATEGORIA": "INSTALACOES", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 60.0, "MAT_MEDIO": 90.0, "MAT_ALTO": 140.0, "MO_BAIXO": 50.0, "MO_MEDIO": 70.0, "MO_ALTO": 100.0},
        {"SUBSISTEMA": "11. INSTALAÇÕES ELÉTRICAS", "CATEGORIA": "INSTALACOES", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 70.0, "MAT_MEDIO": 110.0, "MAT_ALTO": 180.0, "MO_BAIXO": 60.0, "MO_MEDIO": 85.0, "MO_ALTO": 130.0},
        {"SUBSISTEMA": "12. CLIMATIZAÇÃO E EXAUSTÃO", "CATEGORIA": "INSTALACOES", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 30.0, "MAT_MEDIO": 60.0, "MAT_ALTO": 150.0, "MO_BAIXO": 20.0, "MO_MEDIO": 40.0, "MO_ALTO": 90.0},
        {"SUBSISTEMA": "13. REVESTIMENTOS", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 50.0, "MAT_MEDIO": 90.0, "MAT_ALTO": 180.0, "MO_BAIXO": 50.0, "MO_MEDIO": 80.0, "MO_ALTO": 140.0},
        {"SUBSISTEMA": "14. PISOS E PAVIMENTAÇÕES", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 60.0, "MAT_MEDIO": 120.0, "MAT_ALTO": 250.0, "MO_BAIXO": 45.0, "MO_MEDIO": 70.0, "MO_ALTO": 130.0},
        {"SUBSISTEMA": "15. ESQUADRIAS E VIDROS", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 120.0, "MAT_MEDIO": 200.0, "MAT_ALTO": 450.0, "MO_BAIXO": 30.0, "MO_MEDIO": 50.0, "MO_ALTO": 90.0},
        {"SUBSISTEMA": "16. URBANIZAÇÃO E EXTERNOS", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 40.0, "MAT_MEDIO": 70.0, "MAT_ALTO": 120.0, "MO_BAIXO": 25.0, "MO_MEDIO": 45.0, "MO_ALTO": 80.0},
        {"SUBSISTEMA": "17. LIMPEZA FINAL DA OBRA", "CATEGORIA": "ACABAMENTOS", "CONSUMO_MEDIO_M2": 1.0, "MAT_BAIXO": 5.0, "MAT_MEDIO": 10.0, "MAT_ALTO": 20.0, "MO_BAIXO": 15.0, "MO_MEDIO": 25.0, "MO_ALTO": 40.0}
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

# ==========================================
# 3. MOTORES DE GRÁFICOS E CRONOGRAMA
# ==========================================
def card_etapa(prefix):
    for ext in ['.jpg', '.png']:
        if os.path.exists(f"img_{prefix}{ext}"): return f"img_{prefix}{ext}"
    fig, ax = plt.subplots(figsize=(4.5, 3.2), facecolor='#0F2C3D'); ax.axis('off')
    if prefix in ['01', '02', '03', '04']: ax.text(0.5, 0.5, "CANTEIRO E GESTÃO", color='white', ha='center')
    elif prefix in ['05', '09']: ax.text(0.5, 0.5, "RADIER E FUNDAÇÃO", color='white', ha='center')
    elif prefix in ['06', '08']: ax.text(0.5, 0.5, "ESTRUTURA LSF E TELHADO", color='white', ha='center')
    elif prefix in ['07', '10', '11', '12']: ax.text(0.5, 0.5, "INSTALAÇÕES E VEDAÇÃO", color='white', ha='center')
    else: ax.text(0.5, 0.5, "ACABAMENTOS", color='white', ha='center')
    buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0F2C3D'); plt.close(fig); buf.seek(0)
    return buf

def agrupar_macro(df, col_val):
    m_map = {'01':'1. Canteiro', '02':'1. Canteiro', '03':'1. Canteiro', '04':'1. Canteiro', '05':'2. Fundação', '09':'2. Fundação', '06':'3. Estrutura/Telhado', '08':'3. Estrutura/Telhado', '07':'4. Instalações/Vedação', '10':'4. Instalações/Vedação', '11':'4. Instalações/Vedação', '12':'4. Instalações/Vedação'}
    df_m = df.copy(); df_m['MACRO'] = df_m['SUBSISTEMA'].apply(lambda x: m_map.get(str(x)[:2], '5. Acabamentos'))
    return df_m.groupby('MACRO')[col_val].sum().reset_index()

def plot_rosca(g, val_tot):
    fig = plt.figure(figsize=(9, 4), facecolor=HEX_FUNDO); ax = fig.add_subplot(111)
    if val_tot == 0: 
        ax.text(0.5, 0.5, "SEM ITENS NO ESCOPO", ha='center', va='center', color=HEX_PRIMARIA, fontweight='bold'); ax.axis('off')
    else:
        palette = [HEX_PRIMARIA, HEX_SECUNDARIA, HEX_DESTAQUE, '#319795', '#D69E2E']
        w, t, at = ax.pie(g.iloc[:,1], labels=None, autopct='%1.1f%%', startangle=140, colors=palette, wedgeprops=dict(width=0.45, edgecolor=HEX_FUNDO, linewidth=2), textprops=dict(fontsize=9, fontweight='bold', color='white'), pctdistance=0.75)
        for autotext in at: autotext.set_bbox(dict(facecolor=HEX_PRIMARIA, edgecolor='none', boxstyle='round,pad=0.3', alpha=0.85))
        ax.legend(w, g['MACRO'], loc="center left", bbox_to_anchor=(1, 0.5), frameon=False, fontsize=9)
        ax.add_artist(plt.Circle((0,0), 0.55, fc=HEX_FUNDO))
        ax.annotate(f"TOTAL\nR$ {val_tot/1000:,.0f}k", (0, 0), fontsize=12, fontweight='bold', ha='center', va='center', color=HEX_PRIMARIA); ax.axis('equal')
    plt.tight_layout()
    buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor()); plt.close(fig); buf.seek(0); return buf

def calcular_linha_do_tempo(g, dur_w, inic_w):
    dur = [dur_w[i] if g.iloc[i,1] > 0 else 0 for i in range(5)]
    starts = [0] * 5
    for i in range(1, 5):
        if dur[i] > 0:
            ant = i - 1
            while ant >= 0 and dur[ant] == 0: ant -= 1 
            starts[i] = starts[ant] + inic_w[i] if ant >= 0 else 0
    max_w = max([starts[i]+dur[i] for i in range(5)]) if sum(dur) > 0 else 0
    starts_m = [s / 4.0 for s in starts]
    dur_m = [d / 4.0 for d in dur]
    max_m = max_w / 4.0
    return starts_m, dur_m, max_m

def plot_gantt(g, m_prazo, val_tot, dur_semanas, inic_semanas):
    starts_m, dur_m, _ = calcular_linha_do_tempo(g, dur_semanas, inic_semanas)
    fig_g = plt.figure(figsize=(9, 2.5), facecolor=HEX_FUNDO); ax_g = fig_g.add_subplot(111)
    if val_tot == 0: 
        ax_g.text(0.5, 0.5, "SEM ITENS NO ESCOPO", ha='center', va='center', color=HEX_PRIMARIA, fontweight='bold'); ax_g.axis('off')
    else:
        for i in range(5):
            if dur_m[i] > 0:
                ax_g.add_patch(patches.Rectangle((starts_m[i], 5-i-1), dur_m[i], 0.7, facecolor=HEX_SECUNDARIA, edgecolor='white', lw=1))
                ax_g.text(starts_m[i]+0.1, 5-i-0.65, g['MACRO'].tolist()[i], color='white', fontsize=8, fontweight='bold')
        ax_g.set_xlim(0, m_prazo); ax_g.set_ylim(-0.5, 5); ax_g.set_xticks(range(0, m_prazo+1)); ax_g.set_xticklabels([f'Mês {i}' for i in range(m_prazo+1)], color=HEX_PRIMARIA, fontsize=9)
        ax_g.grid(axis='x', alpha=0.3); ax_g.set_yticks([])
        ax_g.spines['top'].set_visible(False); ax_g.spines['right'].set_visible(False); ax_g.spines['left'].set_visible(False); ax_g.spines['bottom'].set_color(HEX_PRIMARIA)
    plt.tight_layout()
    buf_g = io.BytesIO(); plt.savefig(buf_g, format='png', dpi=200, bbox_inches='tight', facecolor=HEX_FUNDO); plt.close(); buf_g.seek(0); return buf_g

def plot_curva_s(g, m_prazo, val_tot, dur_semanas, inic_semanas):
    starts_m, dur_m, _ = calcular_linha_do_tempo(g, dur_semanas, inic_semanas)
    fig_c = plt.figure(figsize=(9, 3.2), facecolor=HEX_FUNDO); ax_c = fig_c.add_subplot(111)
    if val_tot == 0: 
        ax_c.text(0.5, 0.5, "SEM ITENS NO ESCOPO", ha='center', va='center', color=HEX_PRIMARIA, fontweight='bold'); ax_c.axis('off')
    else:
        x_c = np.arange(0.5, m_prazo+0.5)
        somas = 0
        for i in range(5):
            if dur_m[i] > 0: somas += (starts_m[i] + (dur_m[i]/2))
        qtd_validos = sum(1 for d in dur_m if d > 0)
        pico_previsto = (somas / qtd_validos) if qtd_validos > 0 else m_prazo/2
        
        x = np.linspace(-2.5, 2.5, m_prazo)
        w = np.exp(-(x - ((pico_previsto/m_prazo)*4-2))**2)
        p_mensal = (w/w.sum()) * 100
        v_mensal = (w/w.sum()) * val_tot 
        p_acum = np.cumsum(p_mensal)
        
        bars = ax_c.bar(x_c, p_mensal, color=HEX_SECUNDARIA, width=0.5)
        ax_l = ax_c.twinx(); ax_l.plot(x_c, p_acum, color=HEX_DESTAQUE, marker='o', lw=3)
        
        for idx, bar in enumerate(bars):
            h = bar.get_height(); val = v_mensal[idx]
            txt = f'R$ {val/1000:,.1f}k'.replace('.', ',')
            ax_c.text(bar.get_x() + bar.get_width()/2, h + 1, txt, ha='center', va='bottom', fontsize=8, fontweight='bold', color=HEX_PRIMARIA)
            
        ax_c.set_xlim(0, m_prazo); ax_c.set_xticks(x_c); ax_c.set_xticklabels([f'Mês {i+1}' for i in range(m_prazo)], color=HEX_PRIMARIA)
        ax_c.set_ylim(0, max(p_mensal)*1.3); ax_l.set_ylim(0, 110); ax_l.set_yticks([])
        ax_c.spines['top'].set_visible(False); ax_c.spines['right'].set_visible(False); ax_c.spines['left'].set_visible(False); ax_c.spines['bottom'].set_color(HEX_PRIMARIA)
        ax_l.spines['top'].set_visible(False); ax_l.spines['right'].set_visible(False); ax_l.spines['left'].set_visible(False); ax_l.spines['bottom'].set_visible(False)
        ax_c.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    buf_c = io.BytesIO(); plt.savefig(buf_c, format='png', dpi=200, bbox_inches='tight', facecolor=HEX_FUNDO); plt.close(); buf_c.seek(0); return buf_c

# ==========================================
# 4. GERADOR DE PDF
# ==========================================
def gerar_pdf(cli, loc, am2, af2, ac2, m_prazo, sem_prazo, conf_cats, df, v_mer, v_con, t_mat_c, t_mo_c, gm_r, gm_g, gm_c, gc_r, gc_g, gc_c, df_m, exibir_graficos, perc_pagamento):
    buf = io.BytesIO(); doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=40)
    styles = getSampleStyleSheet(); elem = []
    
    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=13, textColor=COR_PRIMARIA, spaceAfter=8)
    h2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=10, textColor=COR_DESTAQUE, spaceBefore=8, spaceAfter=4)
    h3 = ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=9, textColor=COR_PRIMARIA, spaceBefore=8, spaceAfter=2)
    b_b = ParagraphStyle('BB', fontName='Helvetica-Bold', fontSize=8.5, textColor=COR_TEXTO)
    b_n = ParagraphStyle('BN', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO, alignment=4) # Justificado
    b_w = ParagraphStyle('BW', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)
    
    # --- CAPA ---
    elem.append(HRFlowable(width="100%", thickness=3.5, color=COR_DESTAQUE, spaceAfter=15))
    if os.path.exists("logo.png"):
        try:
            ir = ImageReader("logo.png"); iw, ih = ir.getSize(); nw = 3.0*inch; nh = nw/(iw/ih)
            if nh > 1.2*inch: nh = 1.2*inch; nw = nh*(iw/ih)
            elem.append(Image("logo.png", width=nw, height=nh))
        except: pass
    else:
        elem.append(Paragraph("AMÂNCIO", ParagraphStyle('L', fontName='Helvetica-Bold', fontSize=34, textColor=COR_PRIMARIA, alignment=1)))
        elem.append(Paragraph("CONSTRUTORA INTELIGENTE", ParagraphStyle('S', fontName='Helvetica-Bold', fontSize=10, textColor=COR_PRIMARIA, alignment=1, spaceAfter=15)))
    
    elem.append(Spacer(1, 15)); elem.append(HRFlowable(width="35%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=25))
    elem.append(Paragraph("PROPOSTA COMERCIAL PARAMETRIZADA", ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=18, textColor=COR_PRIMARIA, alignment=1, spaceAfter=5)))
    elem.append(Paragraph("ENGENHARIA E EDIFICAÇÕES EM LIGHT STEEL FRAME", ParagraphStyle('ST', fontName='Helvetica-Bold', fontSize=11, textColor=COR_DESTAQUE, alignment=1, spaceAfter=25)))
    
    d_capa = [[Paragraph("<b>PROJETO / CLIENTE:</b>", b_b), Paragraph(cli.upper(), ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))], [Paragraph("<b>LOCALIZAÇÃO:</b>", b_b), Paragraph(loc.upper(), ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))], [Paragraph("<b>ÁREA CONSTRUIDA:</b>", b_b), Paragraph(f"{am2:,.2f} M²", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))], [Paragraph("<b>ÁREA DA FUNDAÇÃO:</b>", b_b), Paragraph(f"{af2:,.2f} M²", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))], [Paragraph("<b>ÁREA DE COBERTURA:</b>", b_b), Paragraph(f"{ac2:,.2f} M²", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))], [Paragraph("<b>PRAZO DE EXECUÇÃO:</b>", b_b), Paragraph(f"{m_prazo} MESES ({sem_prazo} Semanas)", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))], [Paragraph("<b>VERSÃO DO DOCUMENTO:</b>", b_b), Paragraph("V8.2 — DOSSIÊ DE ENGENHARIA", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))]]
    tc = Table(d_capa, colWidths=[150, 300]); tc.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), COR_FUNDO), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')), ('PADDING', (0,0), (-1,-1), 6)]))
    elem.append(tc); elem.append(Spacer(1, 30)); elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_PRIMARIA, spaceAfter=8)); elem.append(Paragraph("AMÂNCIO CONSTRUTORA INTELIGENTE", ParagraphStyle('F', fontName='Helvetica-Bold', fontSize=7.5, textColor=COR_PRIMARIA, alignment=1))); elem.append(PageBreak())
    
    # --- RESUMO FINANCEIRO ---
    elem.append(Paragraph("RESUMO FINANCEIRO E DEFINIÇÕES DE PROJETO", h1)); elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
    aviso = "<font color='white'><b>NOTA TÉCNICA/COMERCIAL:</b> Este documento é um balizamento paramétrico de mercado. Itens 'NÃO INCLUSOS' servem para visão global da obra e planejamento do cliente. Valores exatos exigem projetos executivos.</font>"
    t_aviso = Table([[Paragraph(aviso, b_b)]], colWidths=[450]); t_aviso.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#C53030')), ('PADDING', (0,0), (-1,-1), 6)])); elem.append(t_aviso); elem.append(Spacer(1, 10))

    txt_m_fund = {"BAIXO": "BÁSICA", "MEDIO": "PADRÃO", "ALTO": "COMPLEXA/LUXO"}
    
    elem.append(Paragraph("CLASSIFICAÇÃO PARAMÉTRICA DA OBRA", h2))
    d_cat = [[Paragraph("<b>GRUPO CONSTRUTIVO</b>", b_w), Paragraph("<b>PADRÃO / COMPLEXIDADE DEFINIDA</b>", b_w)], [Paragraph("Fundação e Infra", b_b), Paragraph(txt_m_fund[conf_cats['fund']], ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))], [Paragraph("Estrutura LSF", b_b), Paragraph(txt_m_fund[conf_cats['estr']], ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))], [Paragraph("Instalações Gerais", b_b), Paragraph(txt_m_fund[conf_cats['inst']], ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))], [Paragraph("Acabamentos", b_b), Paragraph(txt_m_fund[conf_cats['acab']], ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))]]
    t_cat = Table(d_cat, colWidths=[150, 310]); t_cat.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), COR_SECUNDARIA), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 4)])); elem.append(t_cat); elem.append(Spacer(1, 15))
    
    elem.append(Paragraph("SÍNTESE DE CUSTOS", h2))
    d_res = [[Paragraph("<b>VALOR ESTIMADO MERCADO (100% OBRA):</b>", b_b), Paragraph(f"R$ {v_mer:,.2f}", b_b)], [Paragraph("<b>VALOR DO CONTRATO AMÂNCIO (SEU ESCOPO):</b>", b_b), Paragraph(f"<font color='{HEX_DESTAQUE}'>R$ {v_con:,.2f}</font>", b_b)]]
    t_res = Table(d_res, colWidths=[310, 150]); t_res.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')), ('BOX', (0,0), (-1,-1), 1, COR_PRIMARIA), ('PADDING', (0,0), (-1,-1), 6)])); elem.append(t_res); elem.append(PageBreak())

    # --- EAP 01: MERCADO ---
    elem.append(Paragraph("EAP 01: ESTRUTURA ANALÍTICA GLOBAL DA OBRA (MERCADO)", h1)); elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
    elem.append(Paragraph("<i>Visão geral e estimativa de todos os subsistemas construtivos para execução plena do projeto.</i>", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))); elem.append(Spacer(1,5))
    d_tab_m = [[Paragraph("<b>ITEM / SUBSISTEMA CONSTRUTIVO</b>", b_w), Paragraph("<b>STATUS CONTRATO</b>", b_w), Paragraph("<b>VALOR ESTIMADO (R$)</b>", b_w)]]
    for i, r in df.iterrows():
        s = r["STATUS"]
        if "NÃO" in s: sf = f'<font color="{HEX_DESTAQUE}">{s}</font>'
        elif "COMPLETO" in s: sf = f'<font color="{HEX_PRIMARIA}"><b>{s}</b></font>'
        else: sf = f'<font color="{HEX_SECUNDARIA}">{s}</font>'
        d_tab_m.append([Paragraph(r["SUBSISTEMA"], ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)), Paragraph(sf, ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)), f"R$ {r['CUSTO_MERCADO']:,.2f}"])
    d_tab_m.append([Paragraph("<b>TOTAL GERAL ESTIMADO (MERCADO)</b>", b_b), "", Paragraph(f"<b>R$ {v_mer:,.2f}</b>", b_b)])
    t_m = Table(d_tab_m, colWidths=[200, 140, 120]); t_m.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), COR_PRIMARIA), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,-1), (-1,-1), COR_FUNDO)])); elem.append(t_m); elem.append(PageBreak())

    # --- DASHBOARDS MERCADO ---
    if exibir_graficos:
        elem.append(Paragraph("DASHBOARDS GLOBAIS (100% DA OBRA)", h1)); elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
        elem.append(Paragraph("<b>1. COMPOSIÇÃO DE CUSTOS</b>", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)))
        elem.append(Image(gm_r, width=5.5*inch, height=2.44*inch)); elem.append(Spacer(1, 10))
        elem.append(Paragraph("<b>2. CRONOGRAMA DE EXECUÇÃO FÍSICA (GANTT)</b>", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)))
        elem.append(Image(gm_g, width=6.6*inch, height=1.83*inch)); elem.append(Spacer(1, 10))
        elem.append(Paragraph("<b>3. FLUXO DE DESEMBOLSO FINANCEIRO</b>", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)))
        elem.append(Image(gm_c, width=6.6*inch, height=2.3*inch)); elem.append(PageBreak())

    # --- EAP 02: CONTRATO ---
    elem.append(Paragraph("EAP 02: O SEU CONTRATO AMÂNCIO (FILTRADO)", h1)); elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
    elem.append(Paragraph("<i>Detalhamento exclusivo dos itens aprovados e selecionados para o escopo da construtora.</i>", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))); elem.append(Spacer(1,5))
    d_tab_c = [[Paragraph("<b>ITEM INCLUSO</b>", b_w), Paragraph("<b>MATERIAIS</b>", b_w), Paragraph("<b>MÃO DE OBRA</b>", b_w), Paragraph("<b>TOTAL ITEM</b>", b_w)]]
    df_filtrado = df[df["CUSTO_CONTRATO"] > 0]
    if df_filtrado.empty:
        d_tab_c.append([Paragraph("Nenhum item selecionado para o contrato.", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)), "-", "-", "-"])
    else:
        for i, r in df_filtrado.iterrows():
            d_tab_c.append([Paragraph(r["SUBSISTEMA"], ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)), f"R$ {r['MAT_CONTRATO']:,.2f}", f"R$ {r['MO_CONTRATO']:,.2f}", f"R$ {r['CUSTO_CONTRATO']:,.2f}"])
    d_tab_c.append([Paragraph("<b>TOTAL DO SEU CONTRATO</b>", b_b), Paragraph(f"<b>R$ {t_mat_c:,.2f}</b>", b_b), Paragraph(f"<b>R$ {t_mo_c:,.2f}</b>", b_b), Paragraph(f"<b>R$ {v_con:,.2f}</b>", b_b)])
    t_c = Table(d_tab_c, colWidths=[200, 85, 85, 90]); t_c.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), COR_SECUNDARIA), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 3), ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EBF8FF'))])); elem.append(t_c); elem.append(PageBreak())

    # --- CRONOGRAMA DE PAGAMENTO COMERCIAL ---
    if v_con > 0:
        elem.append(Paragraph("PROPOSTA DE PAGAMENTO (FLUXO DO CONTRATO)", h1))
        elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
        elem.append(Paragraph("<i>Previsão de faturamento mensal baseada no valor total do escopo selecionado para o contrato (R$).</i>", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)))
        elem.append(Spacer(1,5))
        
        d_pag = [[Paragraph("<b>PARCELA / MÊS</b>", b_w), Paragraph("<b>PERCENTUAL (%)</b>", b_w), Paragraph("<b>VALOR DA PARCELA (R$)</b>", b_w)]]
        soma_val = 0
        for idx, perc in enumerate(perc_pagamento):
            val_parc = v_con * (perc / 100.0)
            soma_val += val_parc
            d_pag.append([f"Mês {idx+1}", f"{perc:.2f}%", f"R$ {val_parc:,.2f}"])
        
        d_pag.append([Paragraph("<b>TOTAL PROPOSTO</b>", b_b), Paragraph(f"<b>{sum(perc_pagamento):.2f}%</b>", b_b), Paragraph(f"<b>R$ {soma_val:,.2f}</b>", b_b)])
        t_pag = Table(d_pag, colWidths=[150, 100, 150])
        t_pag.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COR_SECUNDARIA),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 4),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EBF8FF'))
        ]))
        elem.append(t_pag); elem.append(PageBreak())

    # --- DASHBOARDS CONTRATO ---
    if exibir_graficos:
        elem.append(Paragraph("DASHBOARDS DO CONTRATO (ESCOPO AMÂNCIO)", h1)); elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=10))
        elem.append(Paragraph("<b>1. COMPOSIÇÃO DE CUSTOS DO CONTRATO</b>", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)))
        elem.append(Image(gc_r, width=5.5*inch, height=2.44*inch)); elem.append(Spacer(1, 10))
        elem.append(Paragraph("<b>2. CRONOGRAMA DE ATUAÇÃO (GANTT)</b>", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)))
        elem.append(Image(gc_g, width=6.6*inch, height=1.83*inch)); elem.append(Spacer(1, 10))
        elem.append(Paragraph("<b>3. FLUXO DE DESEMBOLSO DA OBRA (FÍSICO)</b>", ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)))
        elem.append(Image(gc_c, width=6.6*inch, height=2.3*inch)); elem.append(PageBreak())

    # --- NOVO: ESPECIFICAÇÕES TÉCNICAS E MEMORIAL ---
    elem.append(Paragraph("ESPECIFICAÇÕES TÉCNICAS E MEMORIAL", h1))
    elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=15))
    
    # 1. EXPLICAÇÃO DAS CATEGORIAS
    elem.append(Paragraph("1. PARÂMETROS DE ENGENHARIA E COMPLEXIDADE", h2))
    elem.append(Paragraph("Abaixo apresentamos as opções de padrão e complexidade técnica para cada grupo construtivo. A opção <font color='#E83F25'><b>destacada em Laranja</b></font> indica a escolha aplicada para o dimensionamento exclusivo desta proposta.", b_n))
    elem.append(Spacer(1, 10))
    
    # Renderizar blocos das categorias
    for key in ['fund', 'estr', 'inst', 'acab']:
        elem.append(Paragraph(DESC_CATS[key]['titulo'], h3))
        cat_selecionada = conf_cats[key] # "BAIXO", "MEDIO" ou "ALTO"
        
        for nivel in ['BAIXO', 'MEDIO', 'ALTO']:
            if nivel == cat_selecionada:
                # Destaque
                txt = f"<font color='{HEX_DESTAQUE}'>✓ {DESC_CATS[key][nivel]}</font>"
                elem.append(Paragraph(txt, b_n))
            else:
                # Normal/Cinza
                txt = f"<font color='#718096'>{DESC_CATS[key][nivel]}</font>"
                elem.append(Paragraph(txt, b_n))
        elem.append(Spacer(1, 8))
    
    elem.append(PageBreak())

    # 2. DETALHAMENTO DE CADA SUBSISTEMA
    elem.append(Paragraph("ESPECIFICAÇÕES TÉCNICAS E MEMORIAL", h1))
    elem.append(HRFlowable(width="100%", thickness=1.5, color=COR_DESTAQUE, spaceAfter=15))
    elem.append(Paragraph("2. DESCRIÇÃO DOS SUBSISTEMAS E INSUMOS", h2))
    elem.append(Spacer(1, 10))
    
    col_it = 'ITEM' if 'ITEM' in df_m.columns else (df_m.columns[2] if not df_m.empty else '')
    col_ob = 'OBSERVACAO' if 'OBSERVACAO' in df_m.columns else (df_m.columns[4] if not df_m.empty and len(df_m.columns)>4 else (df_m.columns[-1] if not df_m.empty else ''))
    
    for i, r in df.iterrows():
        sub_full = str(r["SUBSISTEMA"])
        pref = sub_full[:2]
        
        # Criação do Bloco do Subsistema
        bloco_sub = []
        bloco_sub.append(Paragraph(sub_full, h3))
        
        # Parágrafo Explicativo (Insumos)
        desc_insumo = DESC_INSUMOS.get(pref, "Serviços e materiais vinculados a esta etapa construtiva.")
        bloco_sub.append(Paragraph(f"<i><b>Composição Geral:</b> {desc_insumo}</i>", b_n))
        bloco_sub.append(Spacer(1, 8))
        
        # Tabela de Memorial (se houver na planilha)
        t_layout = None
        if not df_m.empty:
            f = df_m[df_m['CODIGO'] == pref]
            if not f.empty:
                md = [[Paragraph("<b>SERVIÇO / COMPONENTE</b>", b_w), Paragraph("<b>OBSERVAÇÕES</b>", b_w)]]
                for _, ir in f.iterrows():
                    item_txt = str(ir.get(col_it, ''))
                    if item_txt != "nan" and item_txt.strip() != "":
                        md.append([Paragraph(item_txt, ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO)), Paragraph(str(ir.get(col_ob, '-')), ParagraphStyle('BN_Left', fontName='Helvetica', fontSize=8.5, textColor=COR_TEXTO))])
                
                if len(md) > 1:
                    tm = Table(md, colWidths=[120, 180])
                    tm.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), COR_SECUNDARIA), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 3)]))
                    
                    # Tentativa de Adicionar Imagem ao Lado
                    img_f = None
                    try:
                        img_path = card_etapa(pref)
                        if img_path: img_f = Image(img_path, width=2.0*inch, height=1.4*inch)
                    except: pass
                    
                    if img_f:
                        lt = Table([[[tm], img_f]], colWidths=[310, 160])
                        lt.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,-1), 'RIGHT')]))
                        bloco_sub.append(lt)
                    else:
                        bloco_sub.append(tm)
        
        bloco_sub.append(Spacer(1, 15))
        elem.append(KeepTogether(bloco_sub))

    doc.build(elem, onFirstPage=lambda c, d: None, onLaterPages=lambda c, d: (c.saveState(), c.setFont('Helvetica-Bold', 8), c.setFillColor(COR_PRIMARIA), c.drawRightString(letter[0]-36, 25, f"Página {d.page}"), c.restoreState()))
    buf.seek(0); return buf.getvalue()

# ==========================================
# 5. INTERFACE STREAMLIT
# ==========================================
with st.sidebar:
    st.write("### AMÂNCIO")
    st.success("Motor Bottom-Up Ativo")

st.write("### 📝 DADOS GERAIS DO PROJETO")
col1, col2, col3 = st.columns(3)
cliente = col1.text_input("NOME DO CLIENTE / PROJETO:", value="RESIDENCIAL SILVA")
local = col2.text_input("LOCAL DA OBRA (CIDADE / UF):", value="JOINVILLE / SC")
area_m2 = col3.number_input("ÁREA CONSTRUÍDA (M²):", value=500.0, step=10.0)

col4, col5 = st.columns(2)
area_fundacao_m2 = col4.number_input("ÁREA FUNDAÇÃO (M²):", value=250.0, step=10.0)
area_cobertura_m2 = col5.number_input("ÁREA COBERTURA (M²):", value=300.0, step=10.0)

st.write("---")
st.write("### 🎛️ ENGENHARIA PARAMÉTRICA (BANCO DE DADOS)")
c_cat1, c_cat2 = st.columns(2)
with c_cat1:
    cat_fund = st.selectbox("1. Fundação e Infraestrutura:", ["Leve / Básica", "Moderada / Padrão", "Pesada / Complexa"], index=1)
    cat_inst = st.selectbox("2. Instalações (Elétrica/Hidro):", ["Leve / Básica", "Moderada / Padrão", "Pesada / Complexa"], index=1)
with c_cat2:
    cat_estr = st.selectbox("3. Estrutura LSF e Cobertura:", ["Leve / Básica", "Moderada / Padrão", "Pesada / Complexa"], index=1)
    cat_acab = st.selectbox("4. Acabamentos:", ["Leve / Básica", "Moderada / Padrão", "Pesada / Complexa"], index=1)

map_niv = {"Leve / Básica": "BAIXO", "Moderada / Padrão": "MEDIO", "Pesada / Complexa": "ALTO"}

st.write("---")
st.write("### 🤝 ESCOPO DE CONTRATO (ITENS FORNECIDOS)")

df_base = carregar_valores(); n_itens = len(df_base)

bc1, bc2, bc3, bc4 = st.columns(4)
bc1.button("✅ Tudo (Mat+M.O.)", on_click=att_status, args=("COMPLETO (MAT + M.O.)",), use_container_width=True)
bc2.button("👷 Só M.O.", on_click=att_status, args=("SÓ MÃO DE OBRA",), use_container_width=True)
bc3.button("🧱 Só Material", on_click=att_status, args=("SÓ MATERIAL",), use_container_width=True)
bc4.button("❌ Zerar Tudo", on_click=att_status, args=("NÃO INCLUSO",), use_container_width=True)

df_opcoes = pd.DataFrame({"SUBSISTEMA": df_base["SUBSISTEMA"], "STATUS DO CONTRATO": st.session_state.escopo_status})
df_ed = st.data_editor(df_opcoes, hide_index=True, use_container_width=True, column_config={"STATUS DO CONTRATO": st.column_config.SelectboxColumn("STATUS DO CONTRATO", options=["COMPLETO (MAT + M.O.)", "SÓ MATERIAL", "SÓ MÃO DE OBRA", "NÃO INCLUSO"])})
st.session_state.escopo_status = df_ed["STATUS DO CONTRATO"].tolist()

st.write("---")
st.write("### ⏱️ CRONOGRAMA DA OBRA (EM SEMANAS)")
st.info("Defina a duração e a sequência das etapas em semanas. O prazo total da obra será calculado matematicamente.")

c_cron1, c_cron2 = st.columns(2)
with c_cron1:
    st.markdown("**1. Canteiro e Gestão**")
    d1 = st.number_input("Duração (Semanas)", 1, 50, 4, key="d1")
    
    st.markdown("**2. Fundação e Infraestrutura**")
    d2 = st.number_input("Duração (Semanas)", 1, 50, 6, key="d2")
    i2 = st.number_input("Semanas após INÍCIO do Canteiro", 0, 50, 2, key="i2")
    
    st.markdown("**3. Estrutura LSF e Telhado**")
    d3 = st.number_input("Duração (Semanas)", 1, 50, 8, key="d3")
    i3 = st.number_input("Semanas após INÍCIO da Fundação", 0, 50, 4, key="i3")

with c_cron2:
    st.markdown("**4. Instalações e Vedações**")
    d4 = st.number_input("Duração (Semanas)", 1, 50, 10, key="d4")
    i4 = st.number_input("Semanas após INÍCIO da Estrutura", 0, 50, 4, key="i4")
    
    st.markdown("**5. Acabamentos**")
    d5 = st.number_input("Duração (Semanas)", 1, 50, 12, key="d5")
    i5 = st.number_input("Semanas após INÍCIO das Instalações", 0, 50, 6, key="i5")
    
dur_semanas = [d1, d2, d3, d4, d5]
inic_semanas = [0, i2, i3, i4, i5]

starts_w = [0]*5
for i in range(1, 5): starts_w[i] = starts_w[i-1] + inic_semanas[i]
max_w = max([starts_w[i] + dur_semanas[i] for i in range(5)])
prazo_meses_global = int(np.ceil(max_w / 4.0))

st.success(f"⏱️ PRAZO TOTAL CALCULADO: **{max_w} semanas** (Aprox. **{prazo_meses_global} meses**)")

st.write("---")
st.write("### 💰 FLUXO DE PAGAMENTO DO CONTRATO")
st.info("Distribua o percentual do valor do contrato que será faturado/cobrado a cada mês.")

if 'old_prazo' not in st.session_state or st.session_state.old_prazo != prazo_meses_global:
    st.session_state.old_prazo = prazo_meses_global
    val_default = round(100.0 / prazo_meses_global, 2) if prazo_meses_global > 0 else 100.0
    st.session_state.perc_pagamento = [val_default] * (prazo_meses_global - 1) + [round(100.0 - (val_default * (prazo_meses_global - 1)), 2)]

perc_pagamento = []
cols_pag = st.columns(min(prazo_meses_global, 6))
for m in range(prazo_meses_global):
    with cols_pag[m % 6]:
        val = st.number_input(f"Mês {m+1} (%)", min_value=0.0, max_value=100.0, value=float(st.session_state.perc_pagamento[m]), step=1.0, key=f"pag_m_{m}")
        perc_pagamento.append(val)

st.session_state.perc_pagamento = perc_pagamento
soma_perc = sum(perc_pagamento)
if abs(soma_perc - 100.0) > 0.01:
    st.warning(f"⚠️ A soma dos percentuais está em **{soma_perc:.2f}%**. Ajuste para fechar exatos 100%.")
else:
    st.success("✅ Soma perfeita: **100%**")

st.write("---")
exibir_graficos = st.checkbox("Incluir Dashboards e Cronogramas (Imagens) no Dossiê", value=True)
bdi = st.slider("MARGEM BDI (%):", 10, 35, 20) / 100.0

if st.button("🚀 CALCULAR E GERAR DOSSIÊ", use_container_width=True, type="primary"):
    with st.spinner("Processando..."):
        nv_fund, nv_estr, nv_inst, nv_acab = map_niv[cat_fund], map_niv[cat_estr], map_niv[cat_inst], map_niv[cat_acab]
        df_mem = carregar_memorial()
        
        c_merc, c_cont, mt_c, mo_c = [], [], [], []
        for i, r in df_base.iterrows():
            sub = str(r["SUBSISTEMA"]).upper(); pref = sub[:2]; c = float(r.get("CONSUMO_MEDIO_M2", 1.0))
            if pref in ['05', '09']: nv = nv_fund; area = area_fundacao_m2
            elif pref in ['06', '08']: nv = nv_estr; area = area_cobertura_m2 if pref == '08' else area_m2
            elif pref in ['07', '10', '11', '12']: nv = nv_inst; area = area_m2
            elif pref in ['13', '14', '15', '16', '17']: nv = nv_acab; area = area_m2
            else: nv = "MEDIO"; area = area_m2
            
            p_mat = float(r.get(f"MAT_{nv}", r.get("MAT_MEDIO", 0)))
            p_mo = float(r.get(f"MO_{nv}", r.get("MO_MEDIO", 0)))
            
            c_mat_tot = c * p_mat * area * (1+bdi)
            c_mo_tot = c * p_mo * area * (1+bdi)
            c_merc.append(c_mat_tot + c_mo_tot)
            
            st_sel = st.session_state.escopo_status[i]
            mat_item = c_mat_tot if "COMPLETO" in st_sel or "MATERIAL" in st_sel else 0.0
            mo_item = c_mo_tot if "COMPLETO" in st_sel or "MÃO" in st_sel else 0.0
            
            mt_c.append(mat_item); mo_c.append(mo_item); c_cont.append(mat_item + mo_item)
            
        df_val = df_base.copy()
        df_val["STATUS"] = st.session_state.escopo_status
        df_val["CUSTO_MERCADO"] = c_merc; df_val["MAT_CONTRATO"] = mt_c; df_val["MO_CONTRATO"] = mo_c; df_val["CUSTO_CONTRATO"] = c_cont
        
        v_mer = sum(c_merc); v_con = sum(c_cont)
        gm = agrupar_macro(df_val, 'CUSTO_MERCADO'); gc = agrupar_macro(df_val, 'CUSTO_CONTRATO')
        
        # Manda exatamente qual chave técnica (BAIXO, MEDIO, ALTO) foi escolhida para a função gerar_pdf pintar de Laranja
        cf = {'fund': nv_fund, 'estr': nv_estr, 'inst': nv_inst, 'acab': nv_acab}
        
        if exibir_graficos:
            buf_gm_r = plot_rosca(gm, v_mer)
            buf_gm_g = plot_gantt(gm, prazo_meses_global, v_mer, dur_semanas, inic_semanas)
            buf_gm_c = plot_curva_s(gm, prazo_meses_global, v_mer, dur_semanas, inic_semanas)
            
            buf_gc_r = plot_rosca(gc, v_con)
            buf_gc_g = plot_gantt(gc, prazo_meses_global, v_con, dur_semanas, inic_semanas)
            buf_gc_c = plot_curva_s(gc, prazo_meses_global, v_con, dur_semanas, inic_semanas)
        else:
            buf_gm_r, buf_gm_g, buf_gm_c = None, None, None
            buf_gc_r, buf_gc_g, buf_gc_c = None, None, None
        
        pdf = gerar_pdf(cliente, local, area_m2, area_fundacao_m2, area_cobertura_m2, prazo_meses_global, max_w, cf, df_val, v_mer, v_con, sum(mt_c), sum(mo_c), buf_gm_r, buf_gm_g, buf_gm_c, buf_gc_r, buf_gc_g, buf_gc_c, df_mem, exibir_graficos, perc_pagamento)
        
        st.success("✅ DOSSIÊ DUPLO GERADO COM SUCESSO!")
        st.download_button("📥 BAIXAR NOVO DOSSIÊ (V8.2)", data=pdf, file_name=f"ORCAMENTO_AMANCIO_{cliente.replace(' ','_')}.pdf", mime="application/pdf", use_container_width=True)
