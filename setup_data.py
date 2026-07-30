import os
import json
import zipfile
import requests
import pickle
import networkx as nx
from collections import defaultdict

DATA_URL = "https://cricsheet.org/downloads/ipl_male_json.zip"
ZIP_FILE = "ipl_data.zip"
EXTRACT_DIR = "ipl_matches"
GRAPH_FILE = "ipl_graph.pkl"

def build_dataset():
    if not os.path.exists(GRAPH_FILE):
        print("Downloading and processing IPL data...")
        
        # User-Agent header is required so Cricsheet doesn't block Streamlit Cloud
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(DATA_URL, headers=headers, stream=True)
        response.raise_for_status() # Ensure request was successful (200 OK)

        with open(ZIP_FILE, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Verify zip file before extracting
        if not zipfile.is_zipfile(ZIP_FILE):
            if os.path.exists(ZIP_FILE):
                os.remove(ZIP_FILE)
            raise ValueError("Downloaded file is corrupt or invalid zip.")

        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)

        G = nx.Graph()
        match_counts = defaultdict(int)

        json_files = [f for f in os.listdir(EXTRACT_DIR) if f.endswith('.json')]
        for file_name in json_files:
            file_path = os.path.join(EXTRACT_DIR, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except Exception:
                    continue
                
                info = data.get('info', {})
                players_dict = info.get('players', {})
                
                for team, players in players_dict.items():
                    for p in players:
                        match_counts[p] += 1
                    
                    for i in range(len(players)):
                        for j in range(i + 1, len(players)):
                            G.add_edge(players[i], players[j])

        for player, count in match_counts.items():
            if player in G:
                G.nodes[player]['mat
