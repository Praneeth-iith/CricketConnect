import streamlit as st
import pickle
import random
import networkx as nx

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Cricket Connect — IPL Teammate Graph",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CLASSY CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Streamlit default chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Background styling */
    .stApp {
        background-color: #0b0f17;
        color: #e2e8f0;
    }

    /* Main Header */
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        text-align: center;
    }

    .brand-subtitle {
        font-size: 0.9rem;
        font-weight: 400;
        color: #64748b;
        text-align: center;
        margin-bottom: 36px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* Cards */
    .node-card {
        background: linear-gradient(180deg, #161e2e 0%, #0f172a 100%);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .node-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 6px;
    }

    .node-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.01em;
    }

    /* Connection Pillar */
    .connector {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #334155;
        font-weight: 300;
        font-size: 1.5rem;
    }

    /* Status Alert Cards */
    .alert-card {
        padding: 16px 20px;
        border-radius: 10px;
        margin-top: 24px;
        font-size: 0.9rem;
        font-weight: 500;
        line-height: 1.5;
    }

    .alert-success {
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
    }

    .alert-warning {
        background-color: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        color: #fbbf24;
    }

    .alert-danger {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #f87171;
    }

    /* Customizing Streamlit Controls */
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
    }

    /* Primary Button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: none !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }

    /* Secondary Button */
    div.stButton > button[kind="secondary"] {
        background-color: #1e293b !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background-color: #334155 !important;
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

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
    st.session_state.feedback = None

# --- HEADER ---
st.markdown('<div class="brand-title">CricketConnect</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">IPL Teammate Path Analysis</div>', unsafe_allow_html=True)

# --- NODES DISPLAY ---
col_a, col_mid, col_b = st.columns([5, 1, 5])

with col_a:
    st.markdown(f'''
        <div class="node-card">
            <div class="node-label">Origin Node</div>
            <div class="node-value">{st.session_state.player_a}</div>
        </div>
    ''', unsafe_allow_html=True)

with col_mid:
    st.markdown('<div class="connector">&rarr;</div>', unsafe_allow_html=True)

with col_b:
    st.markdown(f'''
        <div class="node-card">
            <div class="node-label">Target Node</div>
            <div class="node-value">{st.session_state.player_b}</div>
        </div>
    ''', unsafe_allow_html=True)

st.write("")
st.write("")

# --- FORM & INPUT ---
available_options = [p for p in all_players if p not in [st.session_state.player_a, st.session_state.player_b]]

selected_intermediates = st.multiselect(
    "Select intermediate teammates in sequential order:",
    options=available_options,
    key="path_select",
    placeholder="Search player database..."
)

st.write("")

col_btn1, col_btn2 = st.columns([2, 1])

with col_btn1:
    submit_button = st.button(
        "Evaluate Connection",
        type="primary",
        use_container_width=True,
        disabled=(st.session_state.game_status != "PLAYING")
    )

with col_btn2:
    if st.button("Reset Session", type="secondary", use_container_width=True):
        a, b, dist = generate_new_pair()
        st.session_state.player_a = a
        st.session_state.player_b = b
        st.session_state.min_edges = dist
        st.session_state.attempts_left = 2
        st.session_state.game_status = "PLAYING"
        st.session_state.feedback = None
        st.rerun()

# --- GAME LOGIC & EVALUATION ---
if submit_button:
    full_path = [st.session_state.player_a] + selected_intermediates + [st.session_state.player_b]
    
    valid_chain = True
    invalid_pair = ()
    
    for i in range(len(full_path) - 1):
        u, v = full_path[i], full_path[i + 1]
        if not G.has_edge(u, v):
            valid_chain = False
            invalid_pair = (u, v)
            break
            
    if not valid_chain:
        st.session_state.feedback = {
            "type": "danger",
            "message": f"Edge Disconnection: <b>{invalid_pair[0]}</b> and <b>{invalid_pair[1]}</b> have never appeared in the same playing XI."
        }
    else:
        user_edge_count = len(full_path) - 1
        
        if user_edge_count == st.session_state.min_edges:
            st.session_state.feedback = {
                "type": "success",
                "message": f"Optimal Path Confirmed. You completed the connection in <b>{user_edge_count} edges</b> (Minimum possible)."
            }
            st.session_state.game_status = "WON"
        else:
            st.session_state.attempts_left -= 1
            if st.session_state.attempts_left > 0:
                st.session_state.feedback = {
                    "type": "warning",
                    "message": f"Valid path constructed ({user_edge_count} edges), but shorter connections exist. <b>1 attempt remaining.</b>"
                }
            else:
                st.session_state.feedback = {
                    "type": "danger",
                    "message": "Maximum evaluation limit reached. Minimal connection path was not achieved."
                }
                st.session_state.game_status = "LOST"

# --- DISPLAY FEEDBACK ---
if st.session_state.feedback:
    fb = st.session_state.feedback
    st.markdown(f'<div class="alert-card alert-{fb["type"]}">{fb["message"]}</div>', unsafe_allow_html=True)
