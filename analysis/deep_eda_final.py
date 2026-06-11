#!/usr/bin/env python3
"""
Deep EDA on 26 scientist chronologies - using corrected metadata.
"""
import os, re, json
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import seaborn as sns

DATA_DIR = "/home/tcb/老科学家年表/老科学家年表"
OUT_DIR = "/home/tcb/老科学家年表/analysis"
os.makedirs(OUT_DIR, exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams.update({
    'font.size': 10, 'axes.titlesize': 13, 'axes.labelsize': 11,
    'figure.dpi': 150, 'savefig.dpi': 200, 'savefig.bbox': 'tight',
})

# ─── Verified metadata (birth, death, institutions) ───
SCIENTISTS = {
    '谢家荣': {'birth': 1898, 'death': 1966, 
               'insts': ['北京大学', '清华大学', '中山大学', '国立中央大学', '西南联合大学', '浙江大学']},
    '王金陵': {'birth': 1917, 'death': 2013,
               'insts': ['武汉大学', '金陵大学']},
    '王翰章': {'birth': 1919, 'death': 2017,
               'insts': ['四川大学', '北京大学', '清华大学']},
    '沈克琦': {'birth': 1921, 'death': 2015,
               'insts': ['北京大学', '清华大学', '西南联合大学', '武汉大学', '浙江大学']},
    '钟香崇': {'birth': 1921, 'death': 2015,
               'insts': ['中山大学', '交通大学']},
    '冯端': {'birth': 1923, 'death': None,
             'insts': ['国立中央大学', '金陵大学', '北京大学', '同济大学', '浙江大学']},
    '胡含': {'birth': 1924, 'death': None,
             'insts': ['清华大学']},
    '黄旭华': {'birth': 1924, 'death': None,
               'insts': ['交通大学']},
    '梁思礼': {'birth': 1924, 'death': 2016,
               'insts': ['清华大学', '北京大学']},
    '陈志恺': {'birth': 1926, 'death': 2013,
               'insts': ['交通大学', '同济大学', '私立大同大学']},
    '潘家铮': {'birth': 1927, 'death': 2012,
               'insts': ['浙江大学', '清华大学']},
    '王德滋': {'birth': 1927, 'death': None,
               'insts': ['厦门大学', '国立中央大学', '浙江大学']},
    '王文兴': {'birth': 1927, 'death': None,
               'insts': ['山东大学']},
    '高守一': {'birth': 1927, 'death': 2011,
               'insts': ['沈阳医学院']},
    '冯纯伯': {'birth': 1928, 'death': 2010,
               'insts': ['交通大学', '厦门大学', '同济大学', '哈尔滨工业大学', '浙江大学', '清华大学']},
    '戴元本': {'birth': 1928, 'death': 2020,
               'insts': ['中山大学', '北京大学']},
    '涂铭旌': {'birth': 1928, 'death': 2019,
               'insts': ['交通大学', '同济大学', '哈尔滨工业大学']},
    '蒋亦元': {'birth': 1928, 'death': 2020,
               'insts': ['金陵大学']},
    '钟训正': {'birth': 1928, 'death': None,
               'insts': ['同济大学', '国立中央大学', '武汉大学', '浙江大学']},
    '刘振兴': {'birth': 1929, 'death': 2016,
               'insts': ['山东大学']},
    '吴征镒': {'birth': 1916, 'death': 2013,
               'insts': ['清华大学', '北京大学', '西南联合大学', '中山大学']},
    '唐明述': {'birth': 1929, 'death': None,
               'insts': ['交通大学', '北京大学', '清华大学']},
    '张本仁': {'birth': 1929, 'death': 2016,
               'insts': ['哈尔滨工业大学', '国立中央大学']},
    '沈志云': {'birth': 1929, 'death': None,
               'insts': ['交通大学', '武汉大学', '清华大学']},
    '陆钟武': {'birth': 1929, 'death': 2017,
               'insts': ['哈尔滨工业大学', '国立中央大学']},
    '张炳炎': {'birth': 1934, 'death': 2012,
               'insts': ['交通大学', '华南工学院']},
}

# ─── Parse chronologies for year-event data ───
def parse_chronology(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)
    text = text.replace('\r', '')
    events = []
    for m in re.finditer(r'(\d{4})\s*年', text):
        year = int(m.group(1))
        if year < 1800: continue
        start = m.end()
        # Find next year marker
        next_match = re.search(r'\d{4}\s*年', text[start:])
        end = start + next_match.start() if next_match else len(text)
        event_text = text[start:end].strip()
        if len(event_text) > 3:
            events.append({'year': year, 'text': event_text})
    return events

print("Parsing chronologies...")
for name in SCIENTISTS:
    filepath = os.path.join(DATA_DIR, f"{name}.txt")
    events = parse_chronology(filepath)
    SCIENTISTS[name]['events'] = events
    SCIENTISTS[name]['n_events'] = len(events)
    SCIENTISTS[name]['n_insts'] = len(SCIENTISTS[name]['insts'])
    print(f"  {name}: {len(events)} events")

# ═══════════════════════════════════════════
# ANALYSIS 1: Event Density by Decade
# ═══════════════════════════════════════════
print("\n=== 1. Event Density by Decade ===")
decade_counter = Counter()
for sci in SCIENTISTS.values():
    for ev in sci['events']:
        decade = (ev['year'] // 10) * 10
        decade_counter[decade] += 1

valid = [(d, c) for d, c in sorted(decade_counter.items()) if 1890 <= d <= 2020]
decades, counts = zip(*valid)

fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar([str(d) for d in decades], counts, color='steelblue', edgecolor='navy', alpha=0.85)
ax.set_xlabel('Decade', fontsize=12)
ax.set_ylabel('Number of Life Events', fontsize=12)
ax.set_title('Fig 1: Event Density by Decade (26 Scientist Chronologies)', fontsize=14)
ax.tick_params(axis='x', rotation=45)
peak_idx = counts.index(max(counts))
for i, (bar, c) in enumerate(zip(bars, counts)):
    color = 'darkred' if i == peak_idx else 'black'
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, str(c),
            ha='center', va='bottom', fontsize=8, fontweight='bold', color=color)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig1_event_density_by_decade.png'))
plt.close()
print(f"  Peak: {decades[peak_idx]}s ({counts[peak_idx]} events)")
print(f"  Total: {sum(counts)} events")

# ═══════════════════════════════════════════
# ANALYSIS 2: Institution Network Centrality
# ═══════════════════════════════════════════
print("\n=== 2. Institution Network Centrality ===")
inst_scientists = defaultdict(set)
for name, sci in SCIENTISTS.items():
    for inst in sci['insts']:
        inst_scientists[inst].add(name)

shared = {k: v for k, v in inst_scientists.items() if len(v) >= 2}
inst_names = sorted(shared.keys())

# Degree centrality
deg_cent = {inst: len(shared[inst]) for inst in inst_names}
sorted_deg = sorted(deg_cent.items(), key=lambda x: x[1], reverse=True)

# Betweenness (pairs connected through this institution)
betw = {inst: len(shared[inst]) * (len(shared[inst]) - 1) / 2 for inst in inst_names}

# Co-occurrence matrix
cooc = np.zeros((len(inst_names), len(inst_names)))
idx_map = {inst: i for i, inst in enumerate(inst_names)}
for sci in SCIENTISTS.values():
    for i1, i2 in combinations(sci['insts'], 2):
        if i1 in idx_map and i2 in idx_map:
            cooc[idx_map[i1]][idx_map[i2]] += 1
            cooc[idx_map[i2]][idx_map[i1]] += 1

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

short = {
    '清华大学': 'Tsinghua', '北京大学': 'Peking', '交通大学': 'Jiaotong',
    '浙江大学': 'Zhejiang', '同济大学': 'Tongji', '国立中央大学': 'Natl Central U',
    '中山大学': 'Sun Yat-sen', '武汉大学': 'Wuhan', '哈尔滨工业大学': 'HIT',
    '厦门大学': 'Xiamen', '金陵大学': 'Jinling', '山东大学': 'Shandong',
    '西南联合大学': 'SW-Assoc U', '华南工学院': 'S.China Tech', '私立大同大学': 'Datong',
    '四川大学': 'Sichuan', '沈阳医学院': 'Shenyang Med'
}
labels = [f"{short.get(n, n)}\n{n}" for n in [x[0] for x in sorted_deg]]
vals = [x[1] for x in sorted_deg]
colors_bar = plt.cm.viridis(np.linspace(0.15, 0.9, len(vals)))
bars1 = ax1.barh(range(len(vals)), vals, color=colors_bar[::-1])
ax1.set_yticks(range(len(vals)))
ax1.set_yticklabels(labels, fontsize=7)
ax1.set_xlabel('Scientists', fontsize=11)
ax1.set_title('Degree Centrality', fontsize=13)
ax1.invert_yaxis()
for bar, v in zip(bars1, vals):
    ax1.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2, str(v),
             va='center', fontsize=10, fontweight='bold')

mask = np.triu(np.ones_like(cooc, dtype=bool), k=1)
sns.heatmap(cooc, mask=mask, annot=True, fmt='.0f', cmap='YlOrRd',
            xticklabels=[short.get(n, n) for n in inst_names],
            yticklabels=[short.get(n, n) for n in inst_names],
            ax=ax2, cbar_kws={'label': 'Shared Scientists'}, linewidths=0.5)
ax2.set_title('Co-occurrence Matrix', fontsize=13)
ax2.tick_params(axis='both', labelsize=7)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig2_institution_network.png'))
plt.close()

print("  Degree centrality:")
for inst, deg in sorted_deg:
    print(f"    {inst}: {deg} scientists, betweenness={betw[inst]:.0f}")

# ═══════════════════════════════════════════
# ANALYSIS 3: Scientist Similarity Matrix
# ═══════════════════════════════════════════
print("\n=== 3. Scientist Similarity Matrix ===")
names = sorted(SCIENTISTS.keys())
n = len(names)
jacc = np.zeros((n, n))

for i, s1 in enumerate(names):
    for j, s2 in enumerate(names):
        i1 = set(SCIENTISTS[s1]['insts'])
        i2 = set(SCIENTISTS[s2]['insts'])
        u = len(i1 | i2)
        inter = len(i1 & i2)
        jacc[i][j] = inter / u if u > 0 else 0.0

fig, ax = plt.subplots(figsize=(14, 12))
short_n = {nm: nm[:3] for nm in names}
sns.heatmap(jacc, annot=True, fmt='.2f', cmap='RdYlBu_r',
            xticklabels=[short_n[nm] for nm in names],
            yticklabels=[short_n[nm] for nm in names],
            ax=ax, linewidths=0.5, vmin=0, vmax=1,
            cbar_kws={'label': 'Jaccard Similarity'})
ax.set_title('Fig 3: Scientist Similarity (Jaccard on Shared Institutions)', fontsize=14)
ax.tick_params(axis='both', labelsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig3_scientist_similarity_heatmap.png'))
plt.close()

pairs = []
for i in range(n):
    for j in range(i+1, n):
        if jacc[i][j] > 0:
            shared_set = set(SCIENTISTS[names[i]]['insts']) & set(SCIENTISTS[names[j]]['insts'])
            pairs.append((names[i], names[j], jacc[i][j], shared_set))
pairs.sort(key=lambda x: x[2], reverse=True)
print("  Top 10 similar pairs:")
for s1, s2, sim, shared_set in pairs[:10]:
    print(f"    {s1} — {s2}: J={sim:.3f}, shared={shared_set}")

# ═══════════════════════════════════════════
# ANALYSIS 4: Birth Year vs Education Span
# ═══════════════════════════════════════════
print("\n=== 4. Birth Year vs Education Span ===")
pts = [(SCIENTISTS[name]['birth'], SCIENTISTS[name]['n_insts'], name)
       for name in names if SCIENTISTS[name]['birth'] is not None]
pts.sort()
bys = [p[0] for p in pts]
nis = [p[1] for p in pts]
pnames = [p[2] for p in pts]

slope, intercept, r, p_val, _ = stats.linregress(bys, nis)

fig, ax = plt.subplots(figsize=(12, 7))
sc = ax.scatter(bys, nis, c=bys, cmap='coolwarm', s=150, edgecolors='black', alpha=0.85, zorder=5)
xr = np.linspace(min(bys)-5, max(bys)+5, 100)
ax.plot(xr, slope*xr + intercept, 'r--', lw=2, alpha=0.7,
        label=f'y={slope:.3f}x+{intercept:.1f}, R²={r**2:.3f}, p={p_val:.3f}')
for bx, ni, nm in pts:
    if ni >= 4 or bx <= 1910 or bx >= 1930:
        ax.annotate(nm, (bx, ni), textcoords="offset points", xytext=(6, 8), fontsize=7, alpha=0.8)
ax.set_xlabel('Birth Year', fontsize=12)
ax.set_ylabel('Number of Institutions Attended', fontsize=12)
ax.set_title('Fig 4: Birth Year vs. Educational Institution Span', fontsize=14)
ax.legend(loc='upper left', fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig4_birth_year_vs_education.png'))
plt.close()
print(f"  Slope={slope:.4f}, Pearson r={r:.4f}, R²={r**2:.4f}, p={p_val:.4f}")

# ═══════════════════════════════════════════
# ANALYSIS 5: Temporal Coverage (Gantt)
# ═══════════════════════════════════════════
print("\n=== 5. Temporal Coverage ===")
fig, ax = plt.subplots(figsize=(16, 11))
sorted_sci = sorted(SCIENTISTS.items(), key=lambda x: x[1]['birth'] or 9999)

bar_data = []
for i, (name, sci) in enumerate(sorted_sci):
    if sci['birth'] is None: continue
    evs = sci['events']
    if not evs: continue
    min_y = sci['birth']
    max_y = max(ev['year'] for ev in evs)
    if sci['death'] and sci['death'] > max_y:
        max_y = sci['death']
    
    by = sci['birth']
    if by < 1910:
        color, gen = '#e74c3c', 'Gen1'
    elif by < 1926:
        color, gen = '#3498db', 'Gen2'
    else:
        color, gen = '#2ecc71', 'Gen3'
    
    bar_data.append((i, min_y, max_y, color, name, gen, by))

for i, mn, mx, color, name, gen, by in bar_data:
    ax.barh(i, mx - mn, left=mn, height=0.7, color=color, alpha=0.85, edgecolor='black', lw=0.3)
    ax.plot(mn, i, 'ko', markersize=3)

ax.set_yticks([b[0] for b in bar_data])
ax.set_yticklabels([f"{b[4]} ({b[6]})" for b in bar_data], fontsize=7)
ax.set_xlabel('Year', fontsize=11)
ax.set_title('Fig 5: Temporal Coverage — Documented Lifespan of 26 Scientists', fontsize=14)
ax.legend(handles=[
    mpatches.Patch(color='#e74c3c', alpha=0.85, label='Gen1: Pioneer (<1910)'),
    mpatches.Patch(color='#3498db', alpha=0.85, label='Gen2: Builder (1917–1925)'),
    mpatches.Patch(color='#2ecc71', alpha=0.85, label='Gen3: Developer (1926–1935)'),
], loc='lower right', fontsize=9)
ax.grid(axis='x', alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig5_temporal_coverage_gantt.png'))
plt.close()

for name, sci in sorted_sci:
    if sci['birth']:
        evs = sci['events']
        mx = max(ev['year'] for ev in evs) if evs else sci['birth']
        if sci['death'] and sci['death'] > mx: mx = sci['death']
        g = 'G1' if sci['birth'] < 1910 else ('G2' if sci['birth'] < 1926 else 'G3')
        print(f"  [{g}] {name}: {sci['birth']}–{mx} ({mx-sci['birth']}yr)")

# ═══════════════════════════════════════════
# ANALYSIS 6: Top-k Institution Combinations
# ═══════════════════════════════════════════
print("\n=== 6. Top-k Institution Combinations ===")
pair_ctr = Counter()
triple_ctr = Counter()
for sci in SCIENTISTS.values():
    insts = sorted(sci['insts'])
    if len(insts) >= 2:
        for c in combinations(insts, 2):
            pair_ctr[c] += 1
    if len(insts) >= 3:
        for c in combinations(insts, 3):
            triple_ctr[c] += 1

print("  Pairs:")
for p, c in pair_ctr.most_common(12):
    print(f"    {p[0]} + {p[1]}: {c}")
print("  Triples (count≥2):")
for t, c in triple_ctr.most_common(10):
    if c >= 2:
        print(f"    {t[0]} + {t[1]} + {t[2]}: {c}")

# ═══════════════════════════════════════════
# ANALYSIS 7: Mann-Whitney U Test
# ═══════════════════════════════════════════
print("\n=== 7. MWU Test: Gen2 vs Gen3 ===")
g2 = []
g3 = []
g2n = []
g3n = []
for name, sci in SCIENTISTS.items():
    by = sci['birth']
    ni = sci['n_insts']
    if by is None: continue
    if 1917 <= by <= 1925:
        g2.append(ni); g2n.append(name)
    elif 1926 <= by <= 1935:
        g3.append(ni); g3n.append(name)

print(f"  Gen2 (1917–1925): n={len(g2)}, insts={g2}")
print(f"    {g2n}")
print(f"  Gen3 (1926–1935): n={len(g3)}, insts={g3}")
print(f"    {g3n}")

if len(g2) >= 2 and len(g3) >= 2:
    U, p = stats.mannwhitneyu(g2, g3, alternative='two-sided')
    n1, n2 = len(g2), len(g3)
    gr = sum(1 for a in g2 for b in g3 if a > b)
    ls = sum(1 for a in g2 for b in g3 if a < b)
    cd = (gr - ls) / (n1 * n2)
    print(f"  U = {U:.2f}, p = {p:.4f}")
    print(f"  Cliff's delta = {cd:.4f}")
    print(f"  Gen2: mean={np.mean(g2):.2f}, median={np.median(g2):.1f}, SD={np.std(g2, ddof=1):.2f}")
    print(f"  Gen3: mean={np.mean(g3):.2f}, median={np.median(g3):.1f}, SD={np.std(g3, ddof=1):.2f}")

# ─── Summary ───
print("\n=== Summary ===")
te = sum(s['n_events'] for s in SCIENTISTS.values())
ti = sum(s['n_insts'] for s in SCIENTISTS.values())
bz = [s['birth'] for s in SCIENTISTS.values() if s['birth']]
print(f"  Scientists: {len(SCIENTISTS)}")
print(f"  Total events: {te}, Mean: {te/len(SCIENTISTS):.1f}")
print(f"  Birth range: {min(bz)}–{max(bz)}")
print(f"  Mean institutions: {ti/len(SCIENTISTS):.2f}")
print(f"  Shared institutions: {len(shared)}")

# ─── Save JSON ───
output = {
    'decade_counts': {str(d): int(c) for d, c in zip(decades, counts)},
    'institution_centrality': {i: {'degree': d, 'betweenness': betw[i]} for i, d in deg_cent.items()},
    'top_pairs': [{'pair': list(p), 'count': c} for p, c in pair_ctr.most_common(15)],
    'top_triples': [{'triple': list(t), 'count': c} for t, c in triple_ctr.most_common(10) if c >= 2],
    'regression': {'slope': float(slope), 'intercept': float(intercept),
                   'r_squared': float(r**2), 'pearson_r': float(r), 'p_value': float(p_val)},
    'mwu_test': {
        'gen2_n': len(g2), 'gen3_n': len(g3),
        'gen2_mean': float(np.mean(g2)), 'gen3_mean': float(np.mean(g3)),
        'gen2_median': float(np.median(g2)), 'gen3_median': float(np.median(g3)),
        'gen2_SD': float(np.std(g2, ddof=1)), 'gen3_SD': float(np.std(g3, ddof=1)),
        'u_statistic': float(U), 'p_value': float(p), 'cliff_delta': float(cd),
    },
    'summary': {
        'n_scientists': len(SCIENTISTS), 'total_events': te,
        'mean_events': te/len(SCIENTISTS), 'birth_range': [min(bz), max(bz)],
        'mean_institutions': ti/len(SCIENTISTS), 'shared_institutions': len(shared),
    }
}
with open(os.path.join(OUT_DIR, 'eda_results.json'), 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n✅ Done. Files saved to:", OUT_DIR)
