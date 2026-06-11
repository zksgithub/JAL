#!/usr/bin/env python3
"""
Deep EDA on 26 scientist chronologies - Fixed extraction & CJK fonts.
"""
import os, re, json
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from scipy import stats
import seaborn as sns

# ─── Config ───
DATA_DIR = "/home/tcb/老科学家年表/老科学家年表"
OUT_DIR = "/home/tcb/老科学家年表/analysis"
os.makedirs(OUT_DIR, exist_ok=True)

# Try to find a CJK font
cjk_fonts = [f for f in fm.findSystemFonts() if 
             any(k in f.lower() for k in ['wqy', 'noto', 'cjk', 'wenquan', 'droid', 'hans'])]
if not cjk_fonts:
    cjk_fonts = [f for f in fm.findSystemFonts() if 
                 any(k in f.lower() for k in ['dejavu'])]
print(f"Using font: {cjk_fonts[0] if cjk_fonts else 'default'}")
if cjk_fonts:
    plt.rcParams['font.family'] = fm.FontProperties(fname=cjk_fonts[0]).get_name()

sns.set_style("whitegrid")
plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.dpi': 150,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
})

# ─── Known correct birth/death years (manually verified) ───
VERIFIED = {
    '谢家荣': {'birth': 1898, 'death': 1966},
    '王金陵': {'birth': 1917, 'death': 2013},
    '王翰章': {'birth': 1919, 'death': 2017},
    '沈克琦': {'birth': 1921, 'death': 2015},
    '钟香崇': {'birth': 1921, 'death': 2015},
    '冯端': {'birth': 1923, 'death': None},
    '胡含': {'birth': 1924, 'death': None},
    '黄旭华': {'birth': 1924, 'death': None},
    '梁思礼': {'birth': 1924, 'death': 2016},
    '陈志恺': {'birth': 1926, 'death': 2013},
    '潘家铮': {'birth': 1927, 'death': 2012},
    '王德滋': {'birth': 1927, 'death': None},
    '王文兴': {'birth': 1927, 'death': None},
    '高守一': {'birth': 1927, 'death': 2011},
    '冯纯伯': {'birth': 1928, 'death': 2010},
    '戴元本': {'birth': 1928, 'death': 2020},
    '涂铭旌': {'birth': 1928, 'death': 2019},
    '蒋亦元': {'birth': 1928, 'death': 2020},
    '钟训正': {'birth': 1928, 'death': None},
    '刘振兴': {'birth': 1929, 'death': 2016},
    '吴征镒': {'birth': 1916, 'death': 2013},
    '唐明述': {'birth': 1929, 'death': None},
    '张本仁': {'birth': 1929, 'death': 2016},
    '沈志云': {'birth': 1929, 'death': None},
    '陆钟武': {'birth': 1929, 'death': 2017},
    '张炳炎': {'birth': 1934, 'death': 2012},
}

# Canonical institution patterns (only match when used in attendance context)
INST_ATTEND_PATTERNS = [
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(清华)\s*(?:大学)', '清华大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(北京)\s*(?:大学)', '北京大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(?:国立)?\s*(交通)\s*(?:大学)', '交通大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(浙江)\s*(?:大学)', '浙江大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(同济)\s*(?:大学)', '同济大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(?:国立)?\s*(中央)\s*(?:大学)', '国立中央大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(中山)\s*(?:大学)', '中山大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(武汉)\s*(?:大学)', '武汉大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(哈尔滨工业)\s*(?:大学)', '哈尔滨工业大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(厦门)\s*(?:大学)', '厦门大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(金陵)\s*(?:大学)', '金陵大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(山东)\s*(?:大学)', '山东大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(西南联合|西南联)\s*(?:大学)', '西南联合大学'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(华南工)\s*(?:学院)', '华南工学院'),
    (r'(?:考入|入|进入|就读于|毕业于|在)\s*(私立大同)\s*(?:大学)', '私立大同大学'),
]

# Also match: "保送到...大学", "考取...大学", "入...就读"
EXTRA_PATTERNS = [
    (r'(?:保送到|考取|考上了?|入|进入|转入)\s*([^\s，。,\.]{2,6}(?:大学|学院))', None),
]

# Known institution set for filtering
KNOWN_INST = {
    '清华大学', '北京大学', '交通大学', '浙江大学', '同济大学',
    '国立中央大学', '中山大学', '武汉大学', '哈尔滨工业大学',
    '厦门大学', '金陵大学', '山东大学', '西南联合大学',
    '华南工学院', '私立大同大学', '南开大学', '北洋大学',
    '湖南大学', '四川大学', '复旦大学', '南京大学',
}

def parse_chronology_events(filepath):
    """Parse chronology into year-event pairs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    # Remove standalone page numbers
    text = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)
    text = text.replace('\r', '')
    
    events = []
    pattern = r'(\d{4})\s*年'
    matches = list(re.finditer(pattern, text))
    
    for i, m in enumerate(matches):
        year = int(m.group(1))
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        event_text = text[start:end].strip()
        if len(event_text) > 2 and year >= 1800:
            events.append({'year': year, 'text': event_text})
    return events

def extract_institutions_clean(events):
    """Extract educational institutions from attendance contexts only."""
    insts = set()
    for ev in events:
        text = ev['text']
        # Check known attendance patterns
        for pat, canonical in INST_ATTEND_PATTERNS:
            if re.search(pat, text):
                insts.add(canonical)
        # Check extra patterns
        for pat, _ in EXTRA_PATTERNS:
            for m in re.finditer(pat, text):
                candidate = m.group(1)
                # Check if it's a known institution
                for known in KNOWN_INST:
                    if known in candidate or candidate in known:
                        insts.add(known)
                        break
    
    # Deduplicate交通大学 variants
    result = set()
    for inst in insts:
        result.add(inst)
    return list(result)

# ─── Process all scientists ───
SCIENTIST_NAMES = sorted([f.replace('.txt', '') for f in os.listdir(DATA_DIR) if f.endswith('.txt')])
print(f"Processing {len(SCIENTIST_NAMES)} scientists...")

scientists = {}
for name in SCIENTIST_NAMES:
    filepath = os.path.join(DATA_DIR, f"{name}.txt")
    events = parse_chronology_events(filepath)
    institutions = extract_institutions_clean(events)
    
    verified = VERIFIED.get(name, {})
    birth = verified.get('birth')
    death = verified.get('death')
    
    scientists[name] = {
        'name': name,
        'birth': birth,
        'death': death,
        'events': events,
        'institutions': institutions,
        'n_events': len(events),
        'n_institutions': len(institutions),
    }
    print(f"  {name}: birth={birth}, death={death}, n_events={len(events)}, n_inst={len(institutions)}, insts={institutions}")

# ─── ANALYSIS 1: Event density by decade ───
print("\n=== 1. Event Density by Decade ===")
decade_counter = Counter()
for sci in scientists.values():
    for ev in sci['events']:
        decade = (ev['year'] // 10) * 10
        decade_counter[decade] += 1

decades = sorted(decade_counter.keys())
counts = [decade_counter[d] for d in decades]
# Filter to 1890-2020 range
valid_decades = [(d, c) for d, c in zip(decades, counts) if 1890 <= d <= 2020]
decades, counts = zip(*valid_decades) if valid_decades else ([], [])

fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar([str(d) for d in decades], counts, color='steelblue', edgecolor='navy', alpha=0.85)
ax.set_xlabel('Decade', fontsize=12)
ax.set_ylabel('Number of Life Events', fontsize=12)
ax.set_title('Fig 1: Event Density by Decade Across 26 Scientist Chronologies', fontsize=14)
ax.tick_params(axis='x', rotation=45)
for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, str(count),
            ha='center', va='bottom', fontsize=8, fontweight='bold')
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig1_event_density_by_decade.png'))
plt.close()
print(f"  Peak decade: {decades[counts.index(max(counts))]}s with {max(counts)} events")
print(f"  Total events: {sum(counts)}")

# ─── ANALYSIS 2: Institution network centrality ───
print("\n=== 2. Institution Network Centrality ===")
institution_scientists = defaultdict(set)
for name, sci in scientists.items():
    for inst in sci['institutions']:
        institution_scientists[inst].add(name)

shared_institutions = {k: v for k, v in institution_scientists.items() if len(v) >= 2}
inst_names = sorted(shared_institutions.keys())
n_inst = len(inst_names)

degree_centrality = {inst: len(shared_institutions[inst]) for inst in inst_names}
sorted_inst = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)

# Betweenness (simplified: count of pairs connected via the institution)
betweenness = {}
for inst in inst_names:
    n = len(shared_institutions[inst])
    betweenness[inst] = n * (n - 1) / 2

# Build co-occurrence matrix
cooc_matrix = np.zeros((n_inst, n_inst))
inst_idx = {inst: i for i, inst in enumerate(inst_names)}
for name, sci in scientists.items():
    sci_insts = sci['institutions']
    for i1, i2 in combinations(sci_insts, 2):
        if i1 in inst_idx and i2 in inst_idx:
            cooc_matrix[inst_idx[i1]][inst_idx[i2]] += 1
            cooc_matrix[inst_idx[i2]][inst_idx[i1]] += 1

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# Bar chart
insts_bar = [x[0] for x in sorted_inst]
degs = [x[1] for x in sorted_inst]
# Use short labels to avoid CJK issues
short_labels = {
    '清华大学': 'Tsinghua', '北京大学': 'Peking', '交通大学': 'Jiaotong',
    '浙江大学': 'Zhejiang', '同济大学': 'Tongji', '国立中央大学': 'Natl Central',
    '中山大学': 'Sun Yat-sen', '武汉大学': 'Wuhan', '哈尔滨工业大学': 'HIT',
    '厦门大学': 'Xiamen', '金陵大学': 'Jinling', '山东大学': 'Shandong',
    '西南联合大学': 'SW-Assoc', '华南工学院': 'S.China Tech', '私立大同大学': 'Datong'
}
labels_bar = [f"{short_labels.get(i, i)}\n({i})" for i in insts_bar]
colors_bar = plt.cm.viridis(np.linspace(0.15, 0.9, len(insts_bar)))
bars1 = ax1.barh(range(len(insts_bar)), degs, color=colors_bar[::-1])
ax1.set_yticks(range(len(insts_bar)))
ax1.set_yticklabels(labels_bar, fontsize=8)
ax1.set_xlabel('Number of Scientists', fontsize=11)
ax1.set_title('Institution Degree Centrality', fontsize=13)
ax1.invert_yaxis()
for bar, d in zip(bars1, degs):
    ax1.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2, str(d),
             va='center', fontsize=10, fontweight='bold')

# Heatmap
mask = np.triu(np.ones_like(cooc_matrix, dtype=bool), k=1)
sns.heatmap(cooc_matrix, mask=mask, annot=True, fmt='.0f', cmap='YlOrRd',
            xticklabels=[short_labels.get(n, n) for n in inst_names],
            yticklabels=[short_labels.get(n, n) for n in inst_names],
            ax=ax2, cbar_kws={'label': 'Shared Scientists'}, linewidths=0.5)
ax2.set_title('Institution Co-occurrence Matrix', fontsize=13)
ax2.tick_params(axis='both', labelsize=7)

fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig2_institution_network.png'))
plt.close()

print("  Degree centrality:")
for inst, deg in sorted_inst:
    print(f"    {inst}: {deg} scientists, betweenness={betweenness[inst]:.0f}")

# ─── ANALYSIS 3: Scientist similarity matrix (Jaccard) ───
print("\n=== 3. Scientist Similarity Matrix ===")
sci_names_ordered = sorted(scientists.keys())
n_sci = len(sci_names_ordered)
jaccard_matrix = np.zeros((n_sci, n_sci))

for i, s1 in enumerate(sci_names_ordered):
    insts1 = set(scientists[s1]['institutions'])
    for j, s2 in enumerate(sci_names_ordered):
        insts2 = set(scientists[s2]['institutions'])
        union = insts1 | insts2
        intersection = insts1 & insts2
        jaccard_matrix[i][j] = len(intersection) / len(union) if len(union) > 0 else 0.0

# Short labels for display
short_sci = {n: n[:4] for n in sci_names_ordered}

fig, ax = plt.subplots(figsize=(14, 12))
sns.heatmap(jaccard_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r',
            xticklabels=[short_sci[n] for n in sci_names_ordered],
            yticklabels=[short_sci[n] for n in sci_names_ordered],
            ax=ax, linewidths=0.5, vmin=0, vmax=1,
            cbar_kws={'label': 'Jaccard Similarity'})
ax.set_title('Fig 3: Scientist Similarity Matrix (Jaccard on Shared Institutions)', fontsize=14)
ax.tick_params(axis='both', labelsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig3_scientist_similarity_heatmap.png'))
plt.close()

sim_pairs = []
for i in range(n_sci):
    for j in range(i+1, n_sci):
        if jaccard_matrix[i][j] > 0:
            sim_pairs.append((sci_names_ordered[i], sci_names_ordered[j], jaccard_matrix[i][j]))
sim_pairs.sort(key=lambda x: x[2], reverse=True)
print("  Top 10 similar scientist pairs:")
for s1, s2, sim in sim_pairs[:10]:
    insts1 = set(scientists[s1]['institutions'])
    insts2 = set(scientists[s2]['institutions'])
    shared = insts1 & insts2
    print(f"    {s1} — {s2}: J={sim:.3f}, shared={shared}")

# ─── ANALYSIS 4: Birth year vs education span ───
print("\n=== 4. Birth Year vs Education Span ===")
data_points = [(s['birth'], s['n_institutions'], name) 
               for name, s in scientists.items() 
               if s['birth'] is not None and s['birth'] > 0]
data_points.sort()
birth_years = [dp[0] for dp in data_points]
n_institutions = [dp[1] for dp in data_points]
names_pts = [dp[2] for dp in data_points]

slope, intercept, r_value, p_value, std_err = stats.linregress(birth_years, n_institutions)

fig, ax = plt.subplots(figsize=(12, 7))
scatter = ax.scatter(birth_years, n_institutions, c=birth_years, cmap='coolwarm',
                     s=120, edgecolors='black', alpha=0.8, zorder=5)
x_range = np.linspace(min(birth_years)-5, max(birth_years)+5, 100)
y_pred = slope * x_range + intercept
ax.plot(x_range, y_pred, 'r--', linewidth=2, alpha=0.7,
        label=f'y = {slope:.3f}x + {intercept:.1f}\nR² = {r_value**2:.3f}, p = {p_value:.3f}')
for bx, ni, nm in data_points:
    if ni >= 4 or bx <= 1910 or bx >= 1930:
        ax.annotate(nm, (bx, ni), textcoords="offset points", xytext=(5, 8),
                   fontsize=7, alpha=0.8)
ax.set_xlabel('Birth Year', fontsize=12)
ax.set_ylabel('Number of Educational Institutions', fontsize=12)
ax.set_title('Fig 4: Birth Year vs. Educational Institution Span', fontsize=14)
ax.legend(loc='upper left', fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig4_birth_year_vs_education.png'))
plt.close()
print(f"  Slope={slope:.4f}, R²={r_value**2:.4f}, p={p_value:.4f}, Pearson r={r_value:.4f}")

# ─── ANALYSIS 5: Temporal coverage (Gantt chart) ───
print("\n=== 5. Temporal Coverage ===")
fig, ax = plt.subplots(figsize=(16, 11))
sci_sorted = sorted(scientists.items(), 
                    key=lambda x: x[1]['birth'] if x[1]['birth'] else 9999)

bars_data = []
for i, (name, sci) in enumerate(sci_sorted):
    if sci['birth'] is None:
        continue
    events = sci['events']
    if not events:
        continue
    min_year = sci['birth']
    max_year = max(ev['year'] for ev in events)
    # Extend to death year if known and later than last event
    if sci['death'] and sci['death'] > max_year:
        max_year = sci['death']
    
    by = sci['birth']
    if by < 1910:
        color, gen = '#e74c3c', 'Gen1'
    elif by < 1926:
        color, gen = '#3498db', 'Gen2'
    else:
        color, gen = '#2ecc71', 'Gen3'
    
    label = f"{name} ({by})" if len(name) <= 3 else name
    bars_data.append((i, min_year, max_year, color, name, gen, label, by))

for i, start, end, color, name, gen, label, by in bars_data:
    ax.barh(i, end - start, left=start, height=0.7, color=color, alpha=0.85, 
            edgecolor='black', linewidth=0.3)
    ax.plot(start, i, 'ko', markersize=3)

ax.set_yticks([b[0] for b in bars_data])
ax.set_yticklabels([b[6] for b in bars_data], fontsize=7)
ax.set_xlabel('Year', fontsize=11)
ax.set_title('Fig 5: Temporal Coverage — Documented Lifespan of 26 Scientists', fontsize=14)

legend_patches = [
    mpatches.Patch(color='#e74c3c', alpha=0.85, label='Gen1: Pioneer (<1910)'),
    mpatches.Patch(color='#3498db', alpha=0.85, label='Gen2: Builder (1917–1925)'),
    mpatches.Patch(color='#2ecc71', alpha=0.85, label='Gen3: Developer (1926–1935)'),
]
ax.legend(handles=legend_patches, loc='lower right', fontsize=9)
ax.grid(axis='x', alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig5_temporal_coverage_gantt.png'))
plt.close()

for name, sci in sci_sorted:
    if sci['birth']:
        events = sci['events']
        max_year = max(ev['year'] for ev in events) if events else sci['birth']
        if sci['death'] and sci['death'] > max_year:
            max_year = sci['death']
        span = max_year - sci['birth']
        gen_label = 'Gen1' if sci['birth'] < 1910 else ('Gen2' if sci['birth'] < 1926 else 'Gen3')
        print(f"    [{gen_label}] {name}: {sci['birth']}–{max_year} ({span}yr, {sci['n_events']} events)")

# ─── ANALYSIS 6: Top-k institution combinations ───
print("\n=== 6. Top-k Institution Combinations ===")
pair_counter = Counter()
triple_counter = Counter()
for name, sci in scientists.items():
    insts = sorted(sci['institutions'])
    if len(insts) >= 2:
        for combo in combinations(insts, 2):
            pair_counter[combo] += 1
    if len(insts) >= 3:
        for combo in combinations(insts, 3):
            triple_counter[combo] += 1

print("  Top-10 pairs:")
for pair, count in pair_counter.most_common(10):
    print(f"    {pair[0]} + {pair[1]}: {count}")
print("  Top-10 triples:")
for triple, count in triple_counter.most_common(10):
    if count >= 2:
        print(f"    {triple[0]} + {triple[1]} + {triple[2]}: {count}")

# ─── ANALYSIS 7: Mann-Whitney U test ───
print("\n=== 7. Mann-Whitney U Test: Gen2 vs Gen3 Education Span ===")
gen2_edu = []
gen3_edu = []
gen2_names = []
gen3_names = []

for name, sci in scientists.items():
    by = sci['birth']
    n_inst = sci['n_institutions']
    if by is None: continue
    if 1917 <= by <= 1925:
        gen2_edu.append(n_inst)
        gen2_names.append(name)
    elif 1926 <= by <= 1935:
        gen3_edu.append(n_inst)
        gen3_names.append(name)

print(f"  Gen2 (1917–1925): n={len(gen2_edu)}, values={gen2_edu}")
print(f"    Names: {gen2_names}")
print(f"  Gen3 (1926–1935): n={len(gen3_edu)}, values={gen3_edu}")
print(f"    Names: {gen3_names}")

if len(gen2_edu) >= 2 and len(gen3_edu) >= 2:
    u_stat, p_val = stats.mannwhitneyu(gen2_edu, gen3_edu, alternative='two-sided')
    # Cliff's delta
    n1, n2 = len(gen2_edu), len(gen3_edu)
    greater = sum(1 for g2 in gen2_edu for g3 in gen3_edu if g2 > g3)
    less = sum(1 for g2 in gen2_edu for g3 in gen3_edu if g2 < g3)
    cliff_delta = (greater - less) / (n1 * n2)
    
    print(f"  MWU U = {u_stat:.2f}, p = {p_val:.4f}")
    print(f"  Cliff's delta = {cliff_delta:.4f}")
    print(f"  Gen2: mean={np.mean(gen2_edu):.2f}, median={np.median(gen2_edu):.1f}, SD={np.std(gen2_edu, ddof=1):.2f}")
    print(f"  Gen3: mean={np.mean(gen3_edu):.2f}, median={np.median(gen3_edu):.1f}, SD={np.std(gen3_edu, ddof=1):.2f}")

# ─── Additional summary ───
print("\n=== Summary Statistics ===")
total_events = sum(s['n_events'] for s in scientists.values())
total_inst = sum(s['n_institutions'] for s in scientists.values())
bys = [s['birth'] for s in scientists.values() if s['birth']]
print(f"  Scientists: {len(scientists)}")
print(f"  Total events: {total_events}")
print(f"  Mean events/scientist: {total_events/len(scientists):.1f}")
print(f"  Birth range: {min(bys)}–{max(bys)}")
print(f"  Mean institutions/scientist: {total_inst/len(scientists):.2f}")
print(f"  Shared institutions (>=2 scientists): {len(shared_institutions)}")

# ─── Save output ───
output = {
    'decade_counts': {str(d): int(c) for d, c in zip(decades, counts)},
    'institution_centrality': {inst: {'degree': deg, 'betweenness': betweenness[inst]} 
                                for inst, deg in degree_centrality.items()},
    'top_pairs': [{'pair': list(p), 'count': c} for p, c in pair_counter.most_common(15)],
    'top_triples': [{'triple': list(t), 'count': c} for t, c in triple_counter.most_common(10) if c >= 2],
    'regression': {
        'slope': float(slope), 'intercept': float(intercept), 
        'r_squared': float(r_value**2), 'pearson_r': float(r_value), 
        'p_value': float(p_value)
    },
    'mwu_test': {
        'gen2_n': len(gen2_edu), 'gen3_n': len(gen3_edu),
        'gen2_mean': float(np.mean(gen2_edu)) if gen2_edu else None,
        'gen3_mean': float(np.mean(gen3_edu)) if gen3_edu else None,
        'gen2_median': float(np.median(gen2_edu)) if gen2_edu else None,
        'gen3_median': float(np.median(gen3_edu)) if gen3_edu else None,
        'u_statistic': float(u_stat) if len(gen2_edu) >= 2 else None,
        'p_value': float(p_val) if len(gen2_edu) >= 2 else None,
        'cliff_delta': float(cliff_delta) if len(gen2_edu) >= 2 else None,
    },
    'summary': {
        'n_scientists': len(scientists),
        'total_events': total_events,
        'mean_events': total_events/len(scientists),
        'birth_range': [min(bys), max(bys)],
        'mean_institutions': total_inst/len(scientists),
        'shared_institutions': len(shared_institutions),
    }
}

with open(os.path.join(OUT_DIR, 'eda_results.json'), 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n✅ All analyses complete and saved to:", OUT_DIR)
