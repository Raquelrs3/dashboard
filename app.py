import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn              as sns
import numpy                as np

# from componentes import mostrar_metricas_personalizadas

# Configuração de página
st.set_page_config(layout="wide")
st.title("Análise de Desempenho de Cursos e Canais de Divulgação")

def carregar_css(caminho_css):
    with open(caminho_css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Chamada no início do app
carregar_css("styles.css")

# Carrega o DataFrame diretamente do arquivo salvo no Colab
df3 = pd.read_excel("dados_dashboard.xlsx")

# --- Filtros no Topo ---
st.markdown("---")
st.markdown("## Filtros")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    regioes = st.multiselect(
        "Região:",
        options=df3["região"].unique(),
        default=df3["região"].unique()
    )

with col_f2:
    feedbacks = st.multiselect(
        "Feedback:",
        options=df3["feedback"].unique(),
        default=df3["feedback"].unique()
    )

with col_f3:
    ciclos = st.multiselect(
        "Ciclo de Vida:",
        options=df3["ciclo de vida"].unique(),
        default=df3["ciclo de vida"].unique()
    )

# Aplicar os filtros ao DataFrame
df3 = df3[
    df3["região"].isin(regioes) &
    df3["feedback"].isin(feedbacks) &
    df3["ciclo de vida"].isin(ciclos)
]


# Conversão das colunas
for col in ['enviados', 'lidos', 'cliques', 'conversão', 'pedidos']:
    df3[col] = pd.to_numeric(df3[col], errors='coerce').fillna(0)

# --- Cálculos das métricas ---
total_enviados = df3['enviados'].sum()
total_lidos = df3['lidos'].sum()
total_cliques = df3['cliques'].sum()
total_conversoes = df3['conversão'].sum()
total_pedidos = df3['pedidos'].sum()

taxa_leitura = total_lidos / total_enviados if total_enviados else 0
taxa_cliques = total_cliques / total_enviados if total_enviados else 0
taxa_conversao = total_conversoes / total_enviados if total_enviados else 0

taxa_leitura_fmt = f"{taxa_leitura:.1%}"
taxa_cliques_fmt = f"{taxa_cliques:.1%}"
taxa_conversao_fmt = f"{taxa_conversao:.1%}"

# --- Exibição dos Cards ---
st.markdown("---")
st.markdown("## Indicadores Principais")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

# Usando a classe .metric-card para os cards
col1.markdown(f"""
    <div class="metric-card">
        <h3>📩 Taxa de Leitura</h3>
        <p>{taxa_leitura_fmt}</p>
    </div>
""", unsafe_allow_html=True)

col2.markdown(f"""
    <div class="metric-card">
        <h3>🖱️ Taxa de Cliques</h3>
        <p>{taxa_cliques_fmt}</p>
    </div>
""", unsafe_allow_html=True)

col3.markdown(f"""
    <div class="metric-card">
        <h3>✅ Taxa de Conversão</h3>
        <p>{taxa_conversao_fmt}</p>
    </div>
""", unsafe_allow_html=True)

col4.markdown(f"""
    <div class="metric-card">
        <h3>📦 Total de Pedidos</h3>
        <p>{int(total_pedidos)}</p>
    </div>
""", unsafe_allow_html=True)


st.markdown("---")

# --- Adicionar Espaço Antes do Gráfico ---
#st.markdown("<br><br>", unsafe_allow_html=True)  # Adicionando 2 quebras de linha

# --- Gráfico abaixo das métricas ---
#st.markdown("## Taxa de Conversão por Região")

# Calcular a taxa de conversão por região (em percentual)
conversion_rates = df3.groupby('região')['conversão'].mean() * 100

# Calcular o tamanho da amostra por região
sample_sizes = df3.groupby('região').size()

# Combinar taxa de conversão e tamanho da amostra em um DataFrame
conversion_rates = conversion_rates.reset_index()
conversion_rates['sample_size'] = conversion_rates['região'].map(sample_sizes)

# Configurar o estilo do gráfico
sns.set_style("whitegrid")

# Criar o gráfico de barras
fig, ax = plt.subplots(figsize=(10, 4))
sns.barplot(x='região', y='conversão', data=conversion_rates, palette='Blues_d', ax=ax)

# Configurar título e rótulos
ax.set_title('Taxa de Conversão por Região com Tamanho da Amostra', fontsize=11, pad=15)
ax.set_xlabel('Região', fontsize=9)
ax.set_ylabel('Taxa de Conversão (%)', fontsize=9)
ax.set_ylim(0, 100)  # Definir limite do eixo y para melhor visualização

# Adicionar valores nas barras (taxa de conversão e tamanho da amostra)
for index, row in conversion_rates.iterrows():
    ax.text(index, row['conversão'] + 2, f'{row["conversão"]:.1f}%', ha='center', fontsize=10)
    ax.text(index, row['conversão'] - 5, f'N={int(row["sample_size"])}', ha='center', fontsize=9, color='black')

# Exibir o gráfico no Streamlit
st.pyplot(fig)


st.markdown("---")

# --- Gráfico 1: Taxa de Conversão e Média de Pedidos por Feedback ---
#st.markdown("## Taxa de Conversão e Média de Pedidos por Feedback")

st.markdown("## Comparativos por Feedback e Ciclo de Vida")
#st.markdown("<br><br>", unsafe_allow_html=True)  # Adicionando 2 quebras de linha
st.markdown("---")

col1, col2 = st.columns(2)

# Calcular métricas por feedback
with col1:
    metrics = df3.groupby('feedback').agg({
        'conversão': 'mean',
        'pedidos': 'mean',
        'feedback': 'count'
    }).rename(columns={'feedback': 'sample_size'})
    metrics['conversão'] *= 100  # Taxa de conversão em %

    feedbacks = metrics.index
    conversao = metrics['conversão']
    pedidos = metrics['pedidos']
    sample_sizes = metrics['sample_size']

    # Configurar gráfico
    plt.figure(figsize=(8, 7))
    bar_width = 0.35
    x = range(len(feedbacks))

    # Plotar barras
    plt.bar([i - bar_width/2 for i in x], conversao, bar_width, label='Taxa de Conversão (%)', color='skyblue')
    plt.bar([i + bar_width/2 for i in x], pedidos, bar_width, label='Média de Pedidos', color='lightblue')

    # Adicionar anotações
    for i, feedback in enumerate(feedbacks):
        plt.text(i - bar_width/2, conversao[i] + 1, f'{conversao[i]:.1f}%\nN={int(sample_sizes[i])}',
                ha='center', fontsize=8)
        plt.text(i + bar_width/2, pedidos[i] + 0.5, f'{pedidos[i]:.1f}',
                ha='center', fontsize=8)

    # Adicionar título e rótulos
    plt.title('Taxa de Conversão e Média de Pedidos por Feedback', fontsize=15)
    plt.xlabel('Feedback', fontsize=11)
    plt.ylabel('Valor', fontsize=11)
    plt.xticks(x, feedbacks)
    plt.legend(fontsize=8)

    # Ajustar layout
    plt.tight_layout()

    # Exibir gráfico
    st.pyplot(plt)


# --- Gráfico 2: Quantidade Total de Pedidos por Ciclo de Vida ---
#st.markdown("## Quantidade Total de Pedidos por Ciclo de Vida")

with col2:

    # Agrupar por ciclo de vida e user_id e calcular a soma total de pedidos por motorista
    pedidos_por_motorista_ciclo = df3.groupby(['user_id', 'ciclo de vida'])['pedidos'].sum().reset_index()

    # Agora agrupar pelos ciclos de vida para calcular a soma total de pedidos em cada ciclo de vida
    pedidos_por_ciclo = pedidos_por_motorista_ciclo.groupby('ciclo de vida')['pedidos'].sum().reset_index()

    # Plotar gráfico de barras
    plt.figure(figsize=(8, 7))
    ax = sns.barplot(x='ciclo de vida', y='pedidos', data=pedidos_por_ciclo, palette="Set1")

    # Adicionar os valores acima das barras
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.0f}',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center',
                    fontsize=12, color='black',
                    xytext=(0, 10), textcoords='offset points')

    # Configurar título e rótulos
    plt.title('Quantidade Total de Pedidos por Ciclo de Vida no Pós-Campanha', fontsize=15, pad=15)
    plt.xlabel('Ciclo de Vida', fontsize=9)
    plt.ylabel('Quantidade Total de Pedidos', fontsize=9)

    # Exibir gráfico
    st.pyplot(plt)


st.markdown("---")

# --- Gráfico 2: Distribuição de Ciclo de Vida por Tipo de Feedback ---
#st.markdown("## Distribuição de Ciclo de Vida por Tipo de Feedback")

# Contar combinações de feedback e ciclo de vida
contagem = df3.groupby(['feedback', 'ciclo de vida']).size().unstack().fillna(0)

# Gráfico de barras empilhadas
ax = contagem.plot(kind='bar', stacked=True, figsize=(10, 8), colormap='Set2')

plt.title("Distribuição de Ciclo de Vida por Tipo de Feedback", fontsize=13)
plt.xlabel("Tipo de Feedback")
plt.ylabel("Número de Motoristas")
plt.xticks(rotation=0)
plt.legend(title='Ciclo de Vida')

# Adicionar valores nas barras
for i, bar in enumerate(ax.patches):
    height = bar.get_height()
    width = bar.get_width()
    x = bar.get_x()
    y = bar.get_y()
    if height > 0:
        ax.text(
            x + width / 2,
            y + height / 2,
            f'{int(height)}',
            ha='center',
            va='center',
            fontsize=10,
            color='black'
        )

plt.tight_layout()
st.pyplot(plt)


st.markdown("---")

# --- Gráficos: Conversão e Pedidos Médios por Ciclo de Vida ---
st.markdown("## Desempenho Médio por Ciclo de Vida")

st.markdown("---")

col1, col2 = st.columns(2)

# Calcular médias por ciclo de vida
ciclo_stats = df3.groupby('ciclo de vida')[['conversão', 'pedidos']].mean().reset_index()

# Gráfico 1: Conversão média
with col1:
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    sns.barplot(data=ciclo_stats, x='ciclo de vida', y='conversão', palette='Set2', ax=ax1)
    ax1.set_title('Conversão Média por Ciclo de Vida', fontsize=12)
    ax1.set_ylabel('Conversão Média')
    ax1.set_xlabel('Ciclo de Vida')
    ax1.set_ylim(0, 1)
    for index, row in ciclo_stats.iterrows():
        ax1.text(index, row['conversão'] + 0.02, f"{row['conversão']:.2f}", ha='center', fontsize=9)
    st.pyplot(fig1)

# Gráfico 2: Pedidos médios
with col2:
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    sns.barplot(data=ciclo_stats, x='ciclo de vida', y='pedidos', palette='Set2', ax=ax2)
    ax2.set_title('Número Médio de Pedidos por Ciclo de Vida', fontsize=12)
    ax2.set_ylabel('Pedidos Médios')
    ax2.set_xlabel('Ciclo de Vida')
    for index, row in ciclo_stats.iterrows():
        ax2.text(index, row['pedidos'] + 0.01, f"{row['pedidos']:.1f}", ha='center', fontsize=9)
    st.pyplot(fig2)
