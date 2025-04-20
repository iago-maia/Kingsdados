import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Kings League Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Kings League Brasil – Dashboard Interativo")
st.caption("Arquivos encontrados na pasta atual:")
st.text(os.listdir())

# --- FUNÇÃO PARA CARREGAR OS DADOS ---
@st.cache_data
def load_data():
    df_meta = pd.read_csv("players_meta.csv")
    df_stats = pd.read_csv("stats_long.csv")
    return df_meta, df_stats

try:
    df_meta, df_stats = load_data()
    dados_ok = True
except Exception as e:
    st.error("❌ Erro ao carregar os dados:")
    st.text(str(e))
    dados_ok = False

# --- MENU LATERAL ---
st.sidebar.title("🏆 Kings League")
page = st.sidebar.radio("Navegar para:", ["📋 Ranking", "👤 Jogadores", "⚽ Times"])

# --- MAPEAMENTO DE STATS COM PERCENTUAIS CORRESPONDENTES ---
stat_pairs = {
    "GOL-R-ALL": "GOL-R-ALL-X",
    "GOL-R": "GOL-R-X",
    "GOL-D": "GOL-D-X",
    "TIR": "TIR-X",
    "ASS-V": "ASS-X",
    "DRB-R": "DRB-RX",
    "PLP": "PLP-X",
    "DUL-V": "DUL-VX",
    "PAS-CR": "PAS-CRX"
}

# --- FUNÇÃO PARA FORMATAÇÃO AVANÇADA ---
def get_stat_display(row, df_all_stats):
    code = row["stat_code"]
    total = row["stat_total"]
    player_id = row["player_id"]
    
    # Verifica se existe stat percentual correspondente
    if code in stat_pairs:
        percent_code = stat_pairs[code]
        match = df_all_stats[
            (df_all_stats["player_id"] == player_id) &
            (df_all_stats["stat_code"] == percent_code)
        ]
        if not match.empty:
            pct = match.iloc[0]["stat_total"]
            return f"{pct:.0f}% ({int(total)} de {int(total / (pct / 100)) if pct > 0 else 0})"
    return int(total) if pd.notna(total) else "-"

# --- CONTEÚDO DAS PÁGINAS ---
if dados_ok:

    if page == "📋 Ranking":
        st.subheader("📊 Ranking por Estatística")

        # Estatísticas principais primeiro
        all_stats = df_stats["stat_name"].dropna().unique().tolist()
        main_stats_first = [
            "Goals (including tie-breaking shootout)",
            "Assists",
            "MVP",
            "Yellow Cards",
            "Red Cards",
            "Shots",
            "Shots on Target"
        ]
        stat_ordered = main_stats_first + sorted(set(all_stats) - set(main_stats_first))

        selected_stat = st.sidebar.selectbox("Escolha a estatística:", stat_ordered)

        selected_team = st.sidebar.selectbox(
            "Filtrar por time (opcional):",
            options=["Todos"] + sorted(df_stats["team_name"].dropna().unique())
        )

        # Mostrar descrição
        stat_desc = (
            df_stats[df_stats["stat_name"] == selected_stat]["stat_description"]
            .dropna()
            .unique()
        )
        if len(stat_desc) > 0:
            st.markdown(f"📝 **Descrição:** {stat_desc[0]}")
        else:
            st.markdown("📝 **Descrição:** (não disponível)")

        # Filtragem
        filtered = df_stats[df_stats["stat_name"] == selected_stat]
        if selected_team != "Todos":
            filtered = filtered[filtered["team_name"] == selected_team]

        filtered = filtered[filtered["stat_total"].fillna(0) > 0]

        if filtered.empty:
            st.warning("Nenhum jogador registrado com essa estatística.")
        else:
            filtered = filtered.sort_values(by="stat_total", ascending=False)
            merged = filtered.merge(df_meta[["player_id", "image_url"]], on="player_id", how="left")

            for _, row in merged.iterrows():
                stat_display = get_stat_display(row, df_stats)

                cols = st.columns([1, 4, 2, 2])
                with cols[0]:
                    st.image(row["image_url"], width=60)
                with cols[1]:
                    st.markdown(f"**{row['shortName']}**")
                    st.caption(row["team_name"])
                with cols[2]:
                    st.metric("Valor", stat_display)
                with cols[3]:
                    st.caption(f"Ranking geral: {row['stat_ranking']}")
                st.markdown("---")

    elif page == "👤 Jogadores":
        st.subheader("Perfil de Jogadores")
        st.write("Página em desenvolvimento...")

    elif page == "⚽ Times":
        st.subheader("Estatísticas por Time")
        st.write("Página em desenvolvimento...")

else:
    st.warning("⚠️ Verifique se os arquivos 'players_meta.csv' e 'stats_long.csv' estão na mesma pasta do app.")
