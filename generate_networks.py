#!/usr/bin/env python3
"""Generate multi-relational network graphs from LLM extraction data."""

import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import networkx as nx
from collections import Counter, defaultdict

# Font setup
font_paths = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
]
font_path = None
for fp in font_paths:
    if os.path.exists(fp):
        font_path = fp
        break
if font_path:
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['font.sans-serif'] = [prop.get_name()]
plt.rcParams['axes.unicode_minus'] = False

INPUT = "/home/tcb/老科学家年表/analysis/llm_comparison/all_scientists_llm.json"
OUTDIR = "/home/tcb/老科学家年表/analysis"
os.makedirs(OUTDIR, exist_ok=True)

def load_data():
    with open(INPUT, encoding='utf-8') as f:
        return json.load(f)

def build_networks(data):
    """Build multi-relational graphs from LLM extraction data."""
    G_edu = nx.Graph()        # Education network
    G_career = nx.Graph()     # Career co-location network
    G_mentor = nx.DiGraph()   # Mentorship network (directed)
    G_collab = nx.Graph()     # Collaboration network
    
    scientist_institutions = defaultdict(set)
    scientist_career_orgs = defaultdict(set)
    
    for name, entry in data.items():
        if "error" in entry:
            continue
        
        # Education
        for edu in entry.get("education", []):
            inst = edu.get("institution", "")
            if inst and edu.get("status") != "declined":
                scientist_institutions[name].add(inst)
                G_edu.add_node(inst, type="institution")
                G_edu.add_node(name, type="scientist")
                G_edu.add_edge(name, inst, relation="educated_at")
        
        # Career
        for career in entry.get("career", []):
            org = career.get("organization", "")
            if org:
                scientist_career_orgs[name].add(org)
                G_career.add_node(org, type="organization")
                G_career.add_node(name, type="scientist")
                G_career.add_edge(name, org, relation="worked_at")
        
        # Mentors
        for mentor in entry.get("mentors", []):
            mname = mentor.get("name", "")
            if mname:
                G_mentor.add_node(mname, type="person")
                G_mentor.add_node(name, type="scientist")
                G_mentor.add_edge(mname, name, relation="mentored")
        
        # Collaborators
        for collab in entry.get("collaborators", []):
            cname = collab.get("name", "")
            if cname:
                G_collab.add_node(cname, type="person")
                G_collab.add_node(name, type="scientist")
                G_collab.add_edge(name, cname, relation="collaborated")
    
    return G_edu, G_career, G_mentor, G_collab

def plot_mentorship_network(G, outpath):
    """Plot mentorship network."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12), dpi=150)
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    scientist_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'scientist']
    mentor_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'person']
    
    nx.draw_networkx_nodes(G, pos, nodelist=scientist_nodes, 
                          node_color='#e94560', node_size=400, alpha=0.9, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=mentor_nodes,
                          node_color='#0f3460', node_size=200, alpha=0.7, ax=ax)
    
    edges = list(G.edges())
    nx.draw_networkx_edges(G, pos, edgelist=edges, 
                          edge_color='#533483', width=1.5, alpha=0.6,
                          arrows=True, arrowsize=12, ax=ax)
    
    labels = {n: n for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=6, 
                           font_color='white', ax=ax,
                           font_family=prop.get_name() if font_path else None)
    
    ax.set_title('Mentorship Network of Chinese Scientists', 
                color='white', fontsize=16, pad=20, fontweight='bold')
    ax.set_axis_off()
    
    plt.tight_layout()
    plt.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"  Saved: {outpath}")

def plot_collaboration_network(G, outpath):
    """Plot collaboration network."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12), dpi=150)
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    scientist_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'scientist']
    collab_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'person']
    
    nx.draw_networkx_nodes(G, pos, nodelist=scientist_nodes,
                          node_color='#00b4d8', node_size=400, alpha=0.9, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=collab_nodes,
                          node_color='#90e0ef', node_size=150, alpha=0.7, ax=ax)
    
    edges = list(G.edges())
    nx.draw_networkx_edges(G, pos, edgelist=edges,
                          edge_color='#0077b6', width=1.2, alpha=0.5, ax=ax)
    
    labels = {n: n for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=6,
                           font_color='white', ax=ax,
                           font_family=prop.get_name() if font_path else None)
    
    ax.set_title('Professional Collaboration Network',
                color='white', fontsize=16, pad=20, fontweight='bold')
    ax.set_axis_off()
    
    plt.tight_layout()
    plt.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"  Saved: {outpath}")

def print_stats(G_edu, G_career, G_mentor, G_collab, data):
    """Print network statistics."""
    print("\n=== Multi-Relational Network Statistics ===")
    print(f"Education network: {G_edu.number_of_nodes()} nodes, {G_edu.number_of_edges()} edges")
    print(f"Career network: {G_career.number_of_nodes()} nodes, {G_career.number_of_edges()} edges")
    print(f"Mentorship network: {G_mentor.number_of_nodes()} nodes, {G_mentor.number_of_edges()} edges")
    print(f"Collaboration network: {G_collab.number_of_nodes()} nodes, {G_collab.number_of_edges()} edges")
    
    # Total entities
    total_edu = sum(len(e.get('education',[])) for e in data.values() if 'error' not in e)
    total_career = sum(len(e.get('career',[])) for e in data.values() if 'error' not in e)
    total_collab = sum(len(e.get('collaborators',[])) for e in data.values() if 'error' not in e)
    total_mentors = sum(len(e.get('mentors',[])) for e in data.values() if 'error' not in e)
    total_students = sum(len(e.get('students',[])) for e in data.values() if 'error' not in e)
    total_events = sum(len(e.get('key_events',[])) for e in data.values() if 'error' not in e)
    total_awards = sum(len(e.get('awards',[])) for e in data.values() if 'error' not in e)
    
    print(f"\n=== Extraction Totals ===")
    print(f"Education entries: {total_edu}")
    print(f"Career entries: {total_career}")
    print(f"Collaborators: {total_collab}")
    print(f"Mentors: {total_mentors}")
    print(f"Students: {total_students}")
    print(f"Key events: {total_events}")
    print(f"Awards: {total_awards}")

def main():
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} scientists")
    
    print("Building networks...")
    G_edu, G_career, G_mentor, G_collab = build_networks(data)
    
    print_stats(G_edu, G_career, G_mentor, G_collab, data)
    
    print("\nGenerating figures...")
    plot_mentorship_network(G_mentor, os.path.join(OUTDIR, "fig8_mentorship_network.png"))
    plot_collaboration_network(G_collab, os.path.join(OUTDIR, "fig9_collaboration_network.png"))
    
    print("\nDone!")

if __name__ == "__main__":
    main()
