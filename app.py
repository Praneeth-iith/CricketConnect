import streamlit as st
import pickle
import random
import networkx as nx

st.set_page_config(page_title="IPL Player Path Game", page_icon="🏏", layout="centered")

GRAPH_FILE = "ipl_graph.pkl"

@st.cache_resource
def load_game_data():
    with open(GRAPH_FILE, "rb") as f:
        data = pickle.load(f)
    return data['graph'], data['match_counts']

G, match_counts = load_game_data()
all_players = sorted(list(G.nodes()))

def generate_new_pair():
    players = list(G.nodes())
    weights = [match_counts[p] for p in players]

    while True:
        p_a, p_b = random.choices(players, weights=weights, k=2)
        if p_a != p_b and nx.has_path(G, p_a, p_b):
            min_dist = nx.shortest_path_length(G, p_a, p_b)
            if min_dist >= 2:
                return p_a, p_b, min_dist

if 'player_a' not in st.session_state:
    a, b, dist = generate_new_pair()
    st.session_state.player_a = a
    st.session_state.player_b = b
    st.session_state.min_edges = dist
    st.session_state.attempts_left = 2
    st.session_state.game_status = "PLAYING"

st.title("🏏 IPL Teammate Path Game")
st.markdown("Connect **Start Player** to **Target Player** using common teammates!")

st.info(f"### 🚩 **{st.session_state.player_a}**   ➡️   ❓   ➡️   🎯 **{st.session_state.player_b}**")

st.subheader("Build your path:")
st.caption("Select intermediate players in order. (Start and End players are added automatically).")

available_options = [p for p in all_players if p not in [st.session_state.player_a, st.session_state.player_b]]

selected_intermediates = st.multiselect(
    "Search & select intermediate players:",
    options=available_options,
    key="path_select"
)

col1, col2 = st.columns([1, 1])

with col1:
    submit_button = st.button("Submit Path 🚀", use_container_width=True, disabled=(st.session_state.game_status != "PLAYING"))

with col2:
    if st.button("New Challenge 🔄", use_container_width=True):
        a, b, dist = generate_new_pair()
        st.session_state.player_a = a
        st.session_state.player_b = b
        st.session_state.min_edges = dist
        st.session_state.attempts_left = 2
        st.session_state.game_status = "PLAYING"
        st.rerun()

if submit_button:
    full_path = [st.session_state.player_a] + selected_intermediates + [st.session_state.player_b]
    
    valid_chain = True
    invalid_link = ""
    for i in range(len(full_path) - 1):
        u = full_path[i]
        v = full_path[i + 1]
        if not G.has_edge(u, v):
            valid_chain = False
            invalid_link = f"❌ '{u}' and '{v}' never played in an IPL match together!"
            break
            
    if not valid_chain:
        st.error(invalid_link)
    else:
        user_edge_count = len(full_path) - 1
        
        if user_edge_count == st.session_state.min_edges:
            st.success(f"🎉 **CONGRATS!** You found the path with the LEAST number of edges ({user_edge_count} edges)!")
            st.balloons()
            st.session_state.game_status = "WON"
        else:
            st.session_state.attempts_left -= 1
            if st.session_state.attempts_left > 0:
                st.warning(f"⚠️ Valid path ({user_edge_count} edges), but **NOT** the least number of edges! You have **1 chance remaining**.")
            else:
                st.error("❌ Out of chances! You didn't find the minimum edge path.")
                st.session_state.game_status = "LOST"
