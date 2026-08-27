import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

# =============================================================================
# Configuração da página e conexão
# =============================================================================
st.set_page_config(
    page_title="Panorama do mercado estético",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

PG_DATA_USER = os.getenv("PG_DATA_USER", "postgres")
PG_DATA_PASSWORD = os.getenv("PG_DATA_PASSWORD", "postgres")
PG_DATA_DB = os.getenv("PG_DATA_DB", "projeto-ai")
PG_DATA_HOST = os.getenv("PG_DATA_HOST", "localhost")
PG_DATA_PORT = os.getenv("PG_DATA_PORT", "5434")
PG_SCHEMA = "gold"


@st.cache_resource
def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{PG_DATA_USER}:{PG_DATA_PASSWORD}@{PG_DATA_HOST}:{PG_DATA_PORT}/{PG_DATA_DB}"
    )


@st.cache_data(ttl=600)
def carregar_tabelas():
    engine = get_engine()
    nomes = [
        "volume_procedimentos_isaps_pais_ano",
        "volume_procedimentos_isaps_pais_ano_procedimento",
        "procedimentos_reparadores_sus",
        "classificacao_procedimentos_reparadores",
        "contexto_socioeconomico_brasil",
        "procedimentos_x_contexto_brasil",
    ]
    dados = {}
    with engine.connect() as conn:
        for nome in nomes:
            dados[nome] = pd.read_sql(f'SELECT * FROM {PG_SCHEMA}."{nome}"', conn)
    return dados


# =============================================================================
# Estética — CSS e estilo dos gráficos
# =============================================================================
COR_PRIMARIA = "#2E7D6B"     # verde-azulado - estética/saude
COR_SECUNDARIA = "#C97B63"   # terracota suave - contraste quente
COR_DESTAQUE = "#B23A48"     # rosa-queimado - alerta/queda
COR_TEXTO = "#2B2B2B"
COR_TEXTO_SUAVE = "#6B6B6B"
COR_FUNDO_CARD = "#FFFFFF"
COR_FUNDO_PAGINA = "#F7F5F2"

PALETA_CATEGORICA = [
    "#2E7D6B", "#C97B63", "#4A7A96", "#B23A48", "#8C7A3E",
    "#6A5A8C", "#3E8C6E", "#A65D2E", "#5E6B8C", "#8C4E5E",
]

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {COR_FUNDO_PAGINA};
    }}
    html, body, [class*="css"] {{
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        color: {COR_TEXTO};
    }}
    h1, h2, h3, h4 {{
        font-weight: 600;
        letter-spacing: -0.01em;
        color: {COR_TEXTO};
    }}
    h1 {{
        font-size: 2.4rem !important;
    }}
    .subtitulo {{
        color: {COR_TEXTO_SUAVE};
        font-size: 1.05rem;
        margin-top: -0.6rem;
        margin-bottom: 1.8rem;
    }}
    .card {{
        background-color: {COR_FUNDO_CARD};
        border-radius: 14px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.4rem;
        border: 1px solid #EAE6E0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }}
    .tag {{
        display: inline-block;
        background-color: {COR_PRIMARIA}1A;
        color: {COR_PRIMARIA};
        border-radius: 999px;
        padding: 0.15rem 0.75rem;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }}
    .conclusao-box {{
        background-color: #F1F7F4;
        border-left: 4px solid {COR_PRIMARIA};
        border-radius: 6px;
        padding: 0.9rem 1.2rem;
        margin-top: 0.6rem;
        font-size: 0.95rem;
        line-height: 1.55;
    }}
    .lacuna-box {{
        background-color: #FBF1EC;
        border-left: 4px solid {COR_SECUNDARIA};
        border-radius: 6px;
        padding: 1.2rem 1.4rem;
        margin: 1rem 0 1.6rem 0;
        line-height: 1.6;
    }}
    .fonte-nota {{
        color: {COR_TEXTO_SUAVE};
        font-size: 0.82rem;
        margin-top: 0.3rem;
    }}
    hr {{
        border: none;
        border-top: 1px solid #E4DFD8;
        margin: 2.2rem 0;
    }}
    .stButton > button {{
        background-color: transparent;
        border: 1px solid {COR_PRIMARIA};
        color: {COR_PRIMARIA};
        border-radius: 8px;
        padding: 0.25rem 0.9rem;
        font-size: 0.85rem;
    }}
    .stButton > button:hover {{
        background-color: {COR_PRIMARIA};
        color: white;
        border: 1px solid {COR_PRIMARIA};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

plt.rcParams.update({
    "font.family": "Segoe UI",
    "axes.edgecolor": "#D8D3CB",
    "axes.labelcolor": COR_TEXTO,
    "text.color": COR_TEXTO,
    "xtick.color": COR_TEXTO_SUAVE,
    "ytick.color": COR_TEXTO_SUAVE,
    "axes.titlecolor": COR_TEXTO,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
    "savefig.facecolor": "none",
    "grid.color": "#E4DFD8",
    "grid.alpha": 0.6,
})


def estilizar(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D8D3CB")
    ax.spines["bottom"].set_color("#D8D3CB")
    return ax


def grafico_com_conclusao(fig, conclusao_html, chave, fonte=None):
    """Renderiza um grafico e, ao lado, um botao que alterna a exibicao da conclusao."""
    col_grafico, col_botao = st.columns([9, 1])
    with col_grafico:
        st.pyplot(fig, use_container_width=True)
        if fonte:
            st.markdown(f'<div class="fonte-nota">{fonte}</div>', unsafe_allow_html=True)
    with col_botao:
        st.write("")
        st.write("")
        clicado = st.button("💡 Conclusão", key=f"btn_{chave}")
    if clicado:
        st.session_state[f"mostrar_{chave}"] = not st.session_state.get(f"mostrar_{chave}", False)
    if st.session_state.get(f"mostrar_{chave}", False):
        st.markdown(f'<div class="conclusao-box">{conclusao_html}</div>', unsafe_allow_html=True)
    plt.close(fig)


# =============================================================================
# Carregamento dos dados
# =============================================================================
try:
    dados = carregar_tabelas()
except Exception as e:
    st.error(
        "Não foi possível conectar ao Postgres (schema `gold`). "
        "Confirme se o container `postgres-data` está no ar e se as tabelas Gold já foram geradas pelos notebooks.\n\n"
        f"Detalhe técnico: {e}"
    )
    st.stop()

vol_pais_ano = dados["volume_procedimentos_isaps_pais_ano"]
vol_pais_ano_proc = dados["volume_procedimentos_isaps_pais_ano_procedimento"]
reparadores = dados["procedimentos_reparadores_sus"]
classificacao = dados["classificacao_procedimentos_reparadores"]
contexto = dados["contexto_socioeconomico_brasil"]
proc_contexto = dados["procedimentos_x_contexto_brasil"]

ANO_MIN_ISAPS, ANO_MAX_ISAPS = int(vol_pais_ano["ano"].min()), int(vol_pais_ano["ano"].max())

# =============================================================================
# Cabeçalho
# =============================================================================
st.title("Panorama do mercado estético")
st.markdown(
    '<div class="subtitulo">Procedimentos estéticos cirúrgicos e não cirúrgicos no Brasil e no mundo — '
    'mercado privado (ISAPS), sistema público (DATASUS) e contexto socioeconômico (IBGE), 2018-2024.</div>',
    unsafe_allow_html=True,
)

# =============================================================================
# Sobre o projeto
# =============================================================================
st.header("Sobre este relatório")

col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown(
        f"""
<div class="card">

Este relatório reúne os dados tratados ao longo de um pipeline completo de engenharia de dados —
da coleta bruta até a análise final — para responder a uma pergunta central: **como se comporta o
mercado de procedimentos estéticos, no Brasil e no mundo, e o que o cerca?**

O trabalho seguiu a arquitetura em camadas (medalhão):

- **Raw** — arquivos originais (PDF, CSV) carregados sem nenhuma transformação.
- **Bronze** — extração estruturada (tabular) desses arquivos, ainda sem limpeza.
- **Silver** — dados tratados: deduplicados, com nulos avaliados caso a caso, nomes de país/procedimento
  normalizados, traduzidos onde fazia sentido, e validados contra um schema (`pandera`).
- **Gold** — tabelas prontas para análise, publicadas também no Postgres, de onde este relatório lê os dados em tempo real.

</div>
""",
        unsafe_allow_html=True,
    )

with col_b:
    st.markdown(
        f"""
<div class="card">
<span class="tag">Fontes de dados</span>

- **ISAPS** (International Society of Aesthetic Plastic Surgery) — relatórios anuais em PDF,
  2018-2024, com o volume de procedimentos estéticos por país.
- **IBGE** (SIDRA) — escolaridade, população e renda do Brasil, via CSV.
- **DATASUS** (TabNet) — procedimentos hospitalares (SIH/SUS) e ambulatoriais (SIA/SUS) do sistema público.

<span class="tag">Ferramentas</span>

Python (pandas, pdfplumber, pandera), MinIO (data lake local), PostgreSQL, Jupyter Notebook e Streamlit.

</div>
""",
        unsafe_allow_html=True,
    )

with st.expander("Limitações encontradas ao longo do tratamento dos dados"):
    st.markdown(
        """
- **PDFs de 2016 e 2017 do ISAPS foram descartados na Bronze** — usam um layout de tabela incompatível
  com o parser genérico (2016 fragmenta os dados em mini-tabelas com valores conflitantes; 2017 não tem
  tabela país x procedimento, só texto corrido).
- **Encoding divergente entre fontes**: os CSV do IBGE vêm em UTF-8 com BOM; os do DATASUS, em Latin-1
  (padrão de exports legados do TabNet). Um encoding errado não gera erro — corrompe acentos silenciosamente.
- **Nomes de país inconsistentes entre edições do relatório ISAPS** (`USA`/`US`, `UK`/`UNITED KINGDOM`,
  `TURKEY`/`TURKIYE`) — normalizados na Silver, mas exigiram checagem manual.
- **Nomes de procedimento fragmentados entre anos** (ex.: variações de grafia para o mesmo procedimento)
  — traduzidos para o mesmo termo em português, mas as linhas não foram fundidas, o que reduz a cobertura
  do gráfico de crescimento por procedimento (bloco ISAPS) a quem tem dado nos dois anos-ponta.
- **Sem população para os demais países ISAPS**: só o Brasil tem dados de população (IBGE) — os rankings
  entre países comparam volume bruto, não uma taxa per capita.
- **O SUS não cobre cirurgia estética** — só procedimentos reparadores/funcionais. A análise do setor
  público não é comparável 1:1 ao volume do ISAPS; são mercados adjacentes, não a mesma coisa.
- **Lacunas temporais reais não foram preenchidas** — por exemplo, a série de renda do IBGE não tem 2021
  (pesquisa suspensa na pandemia); esses vazios aparecem como ausência de dado, não como zero.
- **Correlações entre volume de procedimentos e indicadores socioeconômicos são temporais, não causais**
  — comparam médias nacionais ano a ano (poucos pontos no tempo), não dados individuais.
        """
    )

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================================================================
# Bloco 1 — ISAPS: Brasil x demais países
# =============================================================================
st.header("Mercado privado — Brasil x demais países (ISAPS)")
st.caption(
    "Volume de procedimentos estéticos reportados à ISAPS por país, "
    f"{ANO_MIN_ISAPS}-{ANO_MAX_ISAPS}. Comparação por volume bruto, não per capita."
)

# --- 1.1 Ranking -------------------------------------------------------
ranking_acumulado = vol_pais_ano.groupby("pais")["quantidade_total"].sum().sort_values(ascending=False)
top15 = ranking_acumulado.head(15).sort_values()
cores_top15 = [COR_PRIMARIA if p == "BRAZIL" else "#B7C4C0" for p in top15.index]

fig1, ax1 = plt.subplots(figsize=(9, 6.5))
ax1.barh(top15.index, top15.values, color=cores_top15)
estilizar(ax1)
ax1.set_xlabel("Quantidade total de procedimentos")
ax1.set_title(f"Top 15 países por volume total, acumulado {ANO_MIN_ISAPS}-{ANO_MAX_ISAPS}")
fig1.tight_layout()

posicao_brasil = int(ranking_acumulado.index.get_loc("BRAZIL")) + 1
lider = ranking_acumulado.index[0]
grafico_com_conclusao(
    fig1,
    f"""O Brasil ocupa a <b>{posicao_brasil}ª posição</b> no volume acumulado de procedimentos estéticos
    entre {ANO_MIN_ISAPS} e {ANO_MAX_ISAPS}, atrás apenas dos <b>{lider}</b>. É uma comparação por volume
    bruto — os dois países também têm população grande, então parte da diferença para os demais reflete
    isso, não necessariamente uma "demanda relativa" maior.""",
    "isaps_ranking",
)

# --- 1.2 Evolução -------------------------------------------------------
top5_paises = ranking_acumulado.head(5).index.tolist()
if "BRAZIL" not in top5_paises:
    top5_paises.append("BRAZIL")
evolucao = vol_pais_ano[vol_pais_ano["pais"].isin(top5_paises)].pivot(index="ano", columns="pais", values="quantidade_total")

fig2, ax2 = plt.subplots(figsize=(9, 5.5))
for i, pais in enumerate(evolucao.columns):
    if pais == "BRAZIL":
        ax2.plot(evolucao.index, evolucao[pais], label=pais, linewidth=3, marker="o", color=COR_PRIMARIA, zorder=5)
    else:
        ax2.plot(evolucao.index, evolucao[pais], label=pais, linewidth=1.4, marker=".", alpha=0.7, color=PALETA_CATEGORICA[i + 2])
estilizar(ax2)
ax2.set_xlabel("Ano")
ax2.set_ylabel("Quantidade total de procedimentos")
ax2.set_title("Evolução do volume total — Brasil x top 5 países")
ax2.legend(frameon=False, fontsize=9)
fig2.tight_layout()

crescimento_brasil_total = (
    (vol_pais_ano[(vol_pais_ano["pais"] == "BRAZIL") & (vol_pais_ano["ano"] == ANO_MAX_ISAPS)]["quantidade_total"].values[0]
     / vol_pais_ano[(vol_pais_ano["pais"] == "BRAZIL") & (vol_pais_ano["ano"] == ANO_MIN_ISAPS)]["quantidade_total"].values[0] - 1) * 100
)
grafico_com_conclusao(
    fig2,
    f"""O volume total do Brasil cresceu <b>{crescimento_brasil_total:.0f}%</b> entre {ANO_MIN_ISAPS} e
    {ANO_MAX_ISAPS} (com uma queda visível em 2020, coerente com a pandemia). A distância para o país líder
    oscila, mas o Brasil se mantém estável na segunda posição ao longo de toda a série.""",
    "isaps_evolucao",
)

# --- 1.3 Ranking do Brasil por procedimento -----------------------------
st.subheader("Brasil por procedimento específico")

brasil_ultimo_ano = vol_pais_ano_proc[
    (vol_pais_ano_proc["pais"] == "BRAZIL") & (vol_pais_ano_proc["ano"] == ANO_MAX_ISAPS)
].sort_values("ranking_no_ano_procedimento", ascending=False)

lideres_ultimo_ano = vol_pais_ano_proc[
    (vol_pais_ano_proc["ano"] == ANO_MAX_ISAPS) & (vol_pais_ano_proc["ranking_no_ano_procedimento"] == 1)
][["procedimento_pt", "pais"]].rename(columns={"pais": "pais_lider"})
brasil_ultimo_ano = brasil_ultimo_ano.merge(lideres_ultimo_ano, on="procedimento_pt", how="left")

cores_rank = [COR_PRIMARIA if r == 1 else "#B7C4C0" for r in brasil_ultimo_ano["ranking_no_ano_procedimento"]]

fig3, ax3 = plt.subplots(figsize=(9, 12))
barras3 = ax3.barh(brasil_ultimo_ano["procedimento_pt"], brasil_ultimo_ano["ranking_no_ano_procedimento"], color=cores_rank)
for barra, rank, pais_lider in zip(barras3, brasil_ultimo_ano["ranking_no_ano_procedimento"], brasil_ultimo_ano["pais_lider"]):
    if rank > 1:
        ax3.text(barra.get_width() + 0.15, barra.get_y() + barra.get_height() / 2, pais_lider,
                  va="center", ha="left", fontsize=8, color=COR_TEXTO_SUAVE)
estilizar(ax3)
ax3.set_xlim(0, brasil_ultimo_ano["ranking_no_ano_procedimento"].max() + 2.5)
ax3.set_xlabel(f"Posição no ranking mundial daquele procedimento em {ANO_MAX_ISAPS} (1 = líder mundial)")
ax3.set_title(f"Brasil: posição no ranking mundial por procedimento específico ({ANO_MAX_ISAPS})")
fig3.tight_layout()

n_lideranca = int((brasil_ultimo_ano["ranking_no_ano_procedimento"] == 1).sum())
top_procedimento_brasil = vol_pais_ano_proc[
    (vol_pais_ano_proc["pais"] == "BRAZIL") & (vol_pais_ano_proc["ano"] == ANO_MAX_ISAPS)
].sort_values("quantidade", ascending=False).iloc[0]["procedimento_pt"]
grafico_com_conclusao(
    fig3,
    f"""O volume total esconde uma informação relevante: em {ANO_MAX_ISAPS}, o Brasil é <b>líder mundial
    em {n_lideranca} procedimentos específicos</b> (barras verdes) — incluindo o seu procedimento de maior
    volume, <b>{top_procedimento_brasil}</b> — mesmo estando em 2º lugar no total geral. Nos demais, o rótulo
    cinza mostra qual país lidera aquele procedimento específico.""",
    "isaps_ranking_procedimento",
)

# --- 1.4 Brasil x líder -------------------------------------------------
paises_comparar = ["BRAZIL", "USA"]
comparativo = vol_pais_ano_proc[
    (vol_pais_ano_proc["ano"] == ANO_MAX_ISAPS) & (vol_pais_ano_proc["pais"].isin(paises_comparar))
]
pivot_comparativo = comparativo.pivot_table(index="procedimento_pt", columns="pais", values="quantidade", aggfunc="sum").dropna()
top10_proc = pivot_comparativo.sum(axis=1).sort_values(ascending=False).head(10).index
pivot_comparativo = pivot_comparativo.loc[top10_proc].sort_values("BRAZIL")

fig4, ax4 = plt.subplots(figsize=(9, 6.5))
largura = 0.38
y_pos = range(len(pivot_comparativo))
ax4.barh([y + largura / 2 for y in y_pos], pivot_comparativo["BRAZIL"], height=largura, label="BRAZIL", color=COR_PRIMARIA)
ax4.barh([y - largura / 2 for y in y_pos], pivot_comparativo["USA"], height=largura, label="USA", color=COR_SECUNDARIA)
ax4.set_yticks(list(y_pos))
ax4.set_yticklabels(pivot_comparativo.index)
estilizar(ax4)
ax4.set_xlabel("Quantidade")
ax4.set_title(f"Brasil x EUA — top 10 procedimentos por volume combinado ({ANO_MAX_ISAPS})")
ax4.legend(frameon=False)
fig4.tight_layout()

grafico_com_conclusao(
    fig4,
    """A comparação direta com os EUA (líder do volume total) mostra que a liderança americana se concentra
    fortemente em <b>procedimentos não cirúrgicos</b> (toxina botulínica, preenchimentos) — volume muito
    maior que o do Brasil nessas categorias — enquanto o Brasil se aproxima ou ultrapassa em procedimentos
    <b>cirúrgicos</b> específicos, como os de mama e corpo.""",
    "isaps_brasil_eua",
)

# --- 1.5 Crescimento por procedimento ------------------------------------
individuais_col = "procedimento_pt"
q_ini = vol_pais_ano_proc[(vol_pais_ano_proc["pais"] == "BRAZIL") & (vol_pais_ano_proc["ano"] == ANO_MIN_ISAPS)].set_index(individuais_col)["quantidade"]
q_fim = vol_pais_ano_proc[(vol_pais_ano_proc["pais"] == "BRAZIL") & (vol_pais_ano_proc["ano"] == ANO_MAX_ISAPS)].set_index(individuais_col)["quantidade"]
crescimento = pd.DataFrame({"inicio": q_ini, "fim": q_fim}).dropna()
crescimento["crescimento_pct"] = ((crescimento["fim"] - crescimento["inicio"]) / crescimento["inicio"] * 100).round(1)
crescimento = crescimento.sort_values("crescimento_pct")

cores_cresc = [COR_DESTAQUE if v < 0 else COR_PRIMARIA for v in crescimento["crescimento_pct"]]

fig5, ax5 = plt.subplots(figsize=(9, 11))
ax5.barh(crescimento.index, crescimento["crescimento_pct"], color=cores_cresc)
ax5.axvline(0, color="#8C8880", linewidth=0.8)
estilizar(ax5)
ax5.set_xlabel(f"Variação percentual de quantidade, {ANO_MIN_ISAPS} -> {ANO_MAX_ISAPS}")
ax5.set_title(f"Brasil: crescimento de cada procedimento, {ANO_MIN_ISAPS} -> {ANO_MAX_ISAPS}")
fig5.tight_layout()

maior_alta = crescimento["crescimento_pct"].idxmax()
maior_queda = crescimento["crescimento_pct"].idxmin()
grafico_com_conclusao(
    fig5,
    f"""Entre os {len(crescimento)} procedimentos com dado nos dois anos-ponta, <b>{maior_alta}</b> teve o
    maior crescimento ({crescimento.loc[maior_alta, 'crescimento_pct']:.0f}%) e <b>{maior_queda}</b> a maior
    queda ({crescimento.loc[maior_queda, 'crescimento_pct']:.0f}%). Isso já começa a responder "o que está
    ganhando ou perdendo popularidade" — mas só para o Brasil (ver a seção sobre a lacuna de análise, abaixo).""",
    "isaps_crescimento",
    fonte="Só procedimentos reportados pelo Brasil nos dois anos-ponta; variantes de grafia entre anos podem sub-representar alguns procedimentos.",
)

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================================================================
# Bloco 2 — SUS: procedimentos reparadores
# =============================================================================
st.header("Mercado público — procedimentos reparadores do SUS")
st.caption(
    "O SUS não cobre cirurgia estética — só procedimentos reparadores/funcionais adjacentes "
    "(reconstrução mamária, pós-bariátrica, craniofacial, queimaduras, entre outros). Não é comparável "
    "1:1 ao volume ISAPS; é o retrato de como o sistema público atua nesse espaço."
)

hospitalar_rep = reparadores[reparadores["origem"] == "hospitalar"]
ambulatorial_rep = reparadores[reparadores["origem"] == "ambulatorial"]

# --- 2.1 Volume total por ano --------------------------------------------
volume_total_ano_rep = reparadores.groupby("ano")["quantidade"].sum()
fig6, ax6 = plt.subplots(figsize=(9, 5))
ax6.plot(volume_total_ano_rep.index, volume_total_ano_rep.values, marker="o", color=COR_PRIMARIA, linewidth=2.2)
estilizar(ax6)
ax6.set_xlabel("Ano")
ax6.set_ylabel("Quantidade (hospitalar + ambulatorial)")
ax6.set_title("Volume total de procedimentos reparadores no SUS, por ano")
fig6.tight_layout()

var_reparadores = (volume_total_ano_rep.iloc[-1] / volume_total_ano_rep.iloc[0] - 1) * 100
grafico_com_conclusao(
    fig6,
    f"""O volume de procedimentos reparadores no SUS variou <b>{var_reparadores:+.0f}%</b> entre
    {int(volume_total_ano_rep.index.min())} e {int(volume_total_ano_rep.index.max())}.""",
    "sus_volume_total",
)

# --- 2.2 Por categoria -----------------------------------------------------
volume_categoria_rep = reparadores.groupby(["categoria", "ano"])["quantidade"].sum().unstack("categoria")
fig7, ax7 = plt.subplots(figsize=(9, 6))
for i, cat in enumerate(volume_categoria_rep.columns):
    ax7.plot(volume_categoria_rep.index, volume_categoria_rep[cat], marker="o", label=cat, color=PALETA_CATEGORICA[i % len(PALETA_CATEGORICA)])
estilizar(ax7)
ax7.set_yscale("log")
ax7.set_xlabel("Ano")
ax7.set_ylabel("Quantidade (escala log)")
ax7.set_title("Volume por categoria reparadora, por ano")
ax7.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8, frameon=False)
fig7.tight_layout()

maior_categoria = reparadores.groupby("categoria")["quantidade"].sum().idxmax()
grafico_com_conclusao(
    fig7,
    f"""<b>{maior_categoria}</b> é a categoria de maior volume acumulado no período — a escala logarítmica
    é necessária porque as categorias têm volumes muito diferentes (de dezenas a centenas de milhares por ano).""",
    "sus_categoria",
)

# --- 2.3 Composição percentual --------------------------------------------
composicao_rep = volume_categoria_rep.div(volume_categoria_rep.sum(axis=1), axis=0) * 100
fig8, ax8 = plt.subplots(figsize=(9, 6))
composicao_rep.plot(kind="bar", stacked=True, ax=ax8, color=PALETA_CATEGORICA[: len(composicao_rep.columns)])
estilizar(ax8)
ax8.set_xlabel("Ano")
ax8.set_ylabel("% do total de procedimentos reparadores")
ax8.set_title("Participação percentual de cada categoria, por ano")
ax8.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8, frameon=False)
fig8.tight_layout()

grafico_com_conclusao(
    fig8,
    """A composição por categoria se mantém relativamente estável ao longo dos anos — não há uma categoria
    ganhando participação de forma acentuada às custas de outra, o que sugere prioridades clínicas estáveis
    dentro do recorte reparador do SUS.""",
    "sus_composicao",
)

# --- 2.4 Hospitalar x Ambulatorial -----------------------------------------
hosp_x_amb = reparadores.groupby(["categoria", "origem"])["quantidade"].sum().unstack("origem")
fig9, ax9 = plt.subplots(figsize=(9, 6))
hosp_x_amb.plot(kind="bar", ax=ax9, color=[COR_PRIMARIA, COR_SECUNDARIA])
estilizar(ax9)
ax9.set_yscale("log")
ax9.set_xlabel("Categoria")
ax9.set_ylabel("Quantidade (escala log)")
ax9.set_title(f"Hospitalar x ambulatorial por categoria, acumulado {int(reparadores['ano'].min())}-{int(reparadores['ano'].max())}")
plt.setp(ax9.get_xticklabels(), rotation=40, ha="right")
fig9.tight_layout()

grafico_com_conclusao(
    fig9,
    """Categorias como Mama e Craniofacial concentram a maior parte do volume no lado <b>hospitalar</b>
    (procedimentos que exigem internação), enquanto o acompanhamento e procedimentos mais simples aparecem
    no lado ambulatorial — refletindo a complexidade clínica típica de cada categoria.""",
    "sus_hosp_amb",
)

# --- 2.5 Custo médio --------------------------------------------------------
custo_medio_rep = hospitalar_rep.copy()
custo_medio_rep["custo_medio_reais"] = custo_medio_rep["valor_total_reais"] / custo_medio_rep["quantidade"]
custo_medio_pivot = custo_medio_rep.pivot(index="ano", columns="categoria", values="custo_medio_reais")

fig10, ax10 = plt.subplots(figsize=(9, 6))
for i, cat in enumerate(custo_medio_pivot.columns):
    ax10.plot(custo_medio_pivot.index, custo_medio_pivot[cat], marker="o", label=cat, color=PALETA_CATEGORICA[i % len(PALETA_CATEGORICA)])
estilizar(ax10)
ax10.set_xlabel("Ano")
ax10.set_ylabel("R$ por procedimento")
ax10.set_title("Custo médio por procedimento hospitalar, por categoria e ano")
ax10.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=8, frameon=False)
fig10.tight_layout()

grafico_com_conclusao(
    fig10,
    """O custo médio por procedimento varia bastante entre categorias — categorias craniofaciais e de
    queimaduras tendem a ter custo unitário mais alto, coerente com procedimentos mais longos e complexos,
    enquanto categorias como pálpebra e ginecomastia ficam na ponta mais barata.""",
    "sus_custo_medio",
    fonte="Só a tabela hospitalar tem valor monetário associado — ambulatorial não entra neste gráfico.",
)

# --- 2.6 Ranking valor -------------------------------------------------------
valor_por_categoria_rep = hospitalar_rep.groupby("categoria")["valor_total_reais"].sum().sort_values()
fig11, ax11 = plt.subplots(figsize=(9, 5.5))
ax11.barh(valor_por_categoria_rep.index, valor_por_categoria_rep.values, color=COR_PRIMARIA)
estilizar(ax11)
ax11.set_xlabel("R$")
ax11.set_title(f"Valor total investido por categoria, acumulado {int(reparadores['ano'].min())}-{int(reparadores['ano'].max())}")
fig11.tight_layout()

top_valor = valor_por_categoria_rep.idxmax()
grafico_com_conclusao(
    fig11,
    f"""<b>{top_valor}</b> concentra o maior investimento público acumulado no recorte reparador — o
    ranking por valor não é idêntico ao ranking por volume (uma categoria pode ter menos casos, mas ser
    proporcionalmente mais cara).""",
    "sus_ranking_valor",
)

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================================================================
# Bloco 3 — Contexto socioeconômico x volume ISAPS (Brasil)
# =============================================================================
st.header("Contexto socioeconômico x volume de procedimentos (Brasil)")
st.caption("Cruzamento do volume total ISAPS do Brasil com população, escolaridade e renda, por ano.")

fig13, ax13 = plt.subplots(figsize=(9, 5))
ax13.plot(proc_contexto["ano"], proc_contexto["quantidade_total"], marker="o", color=COR_PRIMARIA, linewidth=2.2)
estilizar(ax13)
ax13.set_xlabel("Ano")
ax13.set_ylabel("Quantidade total de procedimentos")
ax13.set_title("Volume total de procedimentos estéticos no Brasil, por ano")
fig13.tight_layout()

grafico_com_conclusao(
    fig13,
    """Mesma série de volume total do Brasil já vista no bloco ISAPS, aqui como referência para os três
    cruzamentos socioeconômicos a seguir.""",
    "contexto_volume",
)


def grafico_eixo_duplo(coluna, cor, rotulo_eixo, titulo):
    fig, ax_a = plt.subplots(figsize=(9, 5))
    ax_a.plot(proc_contexto["ano"], proc_contexto["quantidade_total"], marker="o", color=COR_PRIMARIA, label="Volume de procedimentos")
    ax_a.set_xlabel("Ano")
    ax_a.set_ylabel("Quantidade de procedimentos", color=COR_PRIMARIA)
    ax_a.tick_params(axis="y", labelcolor=COR_PRIMARIA)
    estilizar(ax_a)

    ax_b = ax_a.twinx()
    ax_b.plot(proc_contexto["ano"], proc_contexto[coluna], marker="s", color=cor, label=rotulo_eixo)
    ax_b.set_ylabel(rotulo_eixo, color=cor)
    ax_b.tick_params(axis="y", labelcolor=cor)
    ax_b.spines["top"].set_visible(False)

    ax_a.set_title(titulo)
    fig.tight_layout()
    return fig


fig14 = grafico_eixo_duplo("renda_media_reais", COR_SECUNDARIA, "Renda média mensal (R$)",
                            "Volume de procedimentos x renda média — sobreposição temporal, não causal")
grafico_com_conclusao(
    fig14,
    """As duas curvas seguem uma tendência de alta parecida, com queda conjunta em 2020 — coerente com o
    impacto da pandemia tanto na renda quanto na demanda por procedimentos eletivos. De novo, sobreposição
    temporal, não uma prova de relação causal.""",
    "contexto_renda",
)

fig15 = grafico_eixo_duplo("escolaridade_superior_pct", "#6A5A8C", "% com ensino superior completo",
                            "Volume de procedimentos x escolaridade superior — sobreposição temporal, não causal")
grafico_com_conclusao(
    fig15,
    """O percentual da população com ensino superior completo cresce de forma constante ano a ano — mais
    linear que o volume de procedimentos, que tem mais oscilação (inclusive a queda de 2020).""",
    "contexto_escolaridade",
)

fig16 = grafico_eixo_duplo("populacao_total_mil", "#8C7A3E", "População total (mil pessoas)",
                            "Volume de procedimentos x população total — sobreposição temporal, não causal")
grafico_com_conclusao(
    fig16,
    """A população brasileira cresce de forma suave e previsível no período — o crescimento do volume de
    procedimentos é bem mais acentuado que o crescimento populacional, ou seja, não se explica só por "mais
    gente"; há um componente de aumento de demanda por pessoa que este gráfico sozinho não isola.""",
    "contexto_populacao",
)

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================================================================
# Conclusão final
# =============================================================================
st.header("Conclusão final — principais insights")

st.markdown(
    f"""
<div class="card">

1. **O Brasil é a 2ª maior economia de procedimentos estéticos do mundo em volume bruto**, atrás dos EUA,
   posição estável em todos os {int(vol_pais_ano['ano'].nunique())} anos analisados — mas essa posição
   esconde uma liderança mais específica: o Brasil é **líder mundial em {n_lideranca} procedimentos
   individuais** em {ANO_MAX_ISAPS}, incluindo o seu próprio procedimento de maior volume.

2. **Público e privado atuam em espaços diferentes, não concorrentes.** O SUS não compete com o mercado
   ISAPS — atua num recorte reparador/funcional adjacente, com sua própria dinâmica de volume, custo e
   composição por categoria, sem grande oscilação de prioridade entre categorias ao longo do período.

3. **O volume de procedimentos estéticos cresce mais rápido que a população e acompanha, ainda que sem
   relação causal comprovada, a trajetória de renda e escolaridade** — as três séries caem juntas em 2020 e
   sobem depois, um padrão consistente com o efeito da pandemia sobre a economia e sobre a demanda por
   procedimentos eletivos.

4. **No Brasil, entre {ANO_MIN_ISAPS} e {ANO_MAX_ISAPS}, dá para apontar o que ganhou e o que perdeu
   espaço**: **{maior_alta}** foi o procedimento que mais cresceu ({crescimento.loc[maior_alta, 'crescimento_pct']:.0f}%)
   e **{maior_queda}** o que mais recuou ({crescimento.loc[maior_queda, 'crescimento_pct']:.0f}%) — ver o
   gráfico de crescimento por procedimento, no bloco ISAPS.

</div>
""",
    unsafe_allow_html=True,
)

st.caption(
    "Relatório gerado a partir das tabelas Gold no Postgres (schema `gold`), construídas pelos notebooks "
    "de extração, tratamento e agregação deste projeto."
)
