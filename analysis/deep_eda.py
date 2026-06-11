#!/usr/bin/env python3
"""
Deep EDA on 26 scientist chronologies.
Computes event density by decade, institution network centrality,
scientist similarity (Jaccard), birth year vs education span,
temporal coverage Gantt, top-k institution combos, and MWU test.
"""

import os, re, json, math
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
import seaborn as sns

# ─── Config ───
DATA_DIR = "/home/tcb/老科学家年表/老科学家年表"
OUT_DIR = "/home/tcb/老科学家年表/analysis"
os.makedirs(OUT_DIR, exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.dpi': 150,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'font.family': 'sans-serif',
})

# ─── Load scientists & basic metadata ───
SCIENTIST_NAMES = []
for f in sorted(os.listdir(DATA_DIR)):
    if f.endswith('.txt'):
        name = f.replace('.txt', '')
        SCIENTIST_NAMES.append(name)

print(f"Found {len(SCIENTIST_NAMES)} scientist files: {SCIENTIST_NAMES}")

# ─── Parse chronologies ───
def clean_text(text):
    """Remove page numbers and normalize."""
    # Remove standalone page numbers (1-3 digit numbers on their own line)
    text = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)
    # Remove \r
    text = text.replace('\r', '')
    return text

def parse_chronology(filepath):
    """Parse a chronology file into (year, event) pairs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    text = clean_text(text)
    
    events = []
    # Match year markers: "YYYY年" or "YYYY 年" 
    # Pattern: digit-year then content until next year marker
    pattern = r'(\d{4})\s*年'
    matches = list(re.finditer(pattern, text))
    
    for i, m in enumerate(matches):
        year = int(m.group(1))
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        event_text = text[start:end].strip()
        # Skip very short or empty events
        if len(event_text) > 2:
            events.append({'year': year, 'text': event_text})
    
    return events

def extract_birth_year(events):
    """Extract birth year from events."""
    for ev in events:
        if '岁' in ev['text'] and ev['year'] >= 1800:
            # Check if it's a birth year event (age 1 or mention of birth)
            age_match = re.search(r'(\d+)\s*岁', ev['text'])
            if age_match:
                age = int(age_match.group(1))
                if age == 1 or '出生' in ev['text'] or '诞生' in ev['text'] or '生于' in ev['text']:
                    return ev['year']
    # Fallback: return first year
    if events:
        return events[0]['year']
    return None

def extract_death_year(events):
    """Extract death year."""
    for ev in reversed(events):
        if '逝世' in ev['text'] or '去世' in ev['text'] or '病逝' in ev['text'] or '辞世' in ev['text']:
            return ev['year']
    return None

# Canonical institution name mapping
INSTITUTION_MAP = {
    '清华大学': '清华大学',
    '北京大学': '北京大学',
    '交通大学': '交通大学',
    '国立交通大学': '交通大学',
    '唐山交通大学': '交通大学',
    '浙江大学': '浙江大学',
    '同济大学': '同济大学',
    '国立中央大学': '国立中央大学',
    '中央大学': '国立中央大学',
    '中山大学': '中山大学',
    '武汉大学': '武汉大学',
    '哈尔滨工业大学': '哈尔滨工业大学',
    '厦门大学': '厦门大学',
    '金陵大学': '金陵大学',
    '山东大学': '山东大学',
    '西南联合大学': '西南联合大学',
    '西南联大学': '西南联合大学',
    '华南工学院': '华南工学院',
    '私立大同大学': '私立大同大学',
}

def extract_institutions(events):
    """Extract educational institution mentions from events."""
    institutions = set()
    # Pattern: university/college names
    patterns = [
        r'(清华|北京|交通|浙江|同济|国立中央|中央|中山|武汉|哈尔滨工业|厦门|金陵|山东|西南联合|华南工|私立大同|北洋)\s*(大学|工学院|学院)',
        r'(考入|入读|进入|考入|就读于|保送到|毕业于|任教于|在.*读书).*?(大学|学院)',
    ]
    
    for ev in events:
        text = ev['text']
        for pattern in patterns:
            for m in re.finditer(pattern, text):
                inst = m.group(0)
                # Normalize
                for key, canonical in INSTITUTION_MAP.items():
                    if key in inst:
                        institutions.add(canonical)
                        break
    
    # Special handling for known institutions
    known = ['清华大学', '北京大学', '交通大学', '浙江大学', '同济大学', 
             '国立中央大学', '中山大学', '武汉大学', '哈尔滨工业大学',
             '厦门大学', '金陵大学', '山东大学', '西南联合大学', 
             '华南工学院', '私立大同大学']
    
    result = set()
    for ev in events:
        text = ev['text']
        for inst in known:
            if inst in text or (inst == '国立中央大学' and '中央大学' in text):
                result.add(inst)
    
    return list(result)

# ─── Process all chronologies ───
scientists = {}
for name in SCIENTIST_NAMES:
    filepath = os.path.join(DATA_DIR, f"{name}.txt")
    events = parse_chronology(filepath)
    
    birth_year = extract_birth_year(events)
    death_year = extract_death_year(events)
    institutions = extract_institutions(events)
    
    scientists[name] = {
        'name': name,
        'birth': birth_year,
        'death': death_year,
        'events': events,
        'institutions': institutions,
        'n_events': len(events),
        'n_institutions': len(institutions),
    }
    
    print(f"  {name}: birth={birth_year}, death={death_year}, "
          f"events={len(events)}, institutions={institutions}")

# ─── ANALYSIS 1: Event density by decade ───
print("\n=== Analysis 1: Event density by decade ===")
decade_counter = Counter()
for name, sci in scientists.items():
    for ev in sci['events']:
        decade = (ev['year'] // 10) * 10
        decade_counter[decade] += 1

decades = sorted(decade_counter.keys())
counts = [decade_counter[d] for d in decades]

fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar([str(d) for d in decades], counts, color='steelblue', edgecolor='navy', alpha=0.85)
ax.set_xlabel('Decade')
ax.set_ylabel('Number of Life Events')
ax.set_title('Event Density by Decade Across 26 Scientist Chronologies')
ax.tick_params(axis='x', rotation=45)
for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, str(count),
            ha='center', va='bottom', fontsize=8, fontweight='bold')
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig1_event_density_by_decade.png'))
plt.close()
print(f"  Decades: {decades}")
print(f"  Counts: {counts}")
print(f"  Total events: {sum(counts)}")

# ─── ANALYSIS 2: Institution network centrality ───
print("\n=== Analysis 2: Institution network centrality ===")
# Build co-affiliation graph
institution_scientists = defaultdict(set)
scientist_institutions = {}
for name, sci in scientists.items():
    sci_insts = set(sci['institutions'])
    scientist_institutions[name] = sci_insts
    for inst in sci_insts:
        institution_scientists[inst].add(name)

# Only keep institutions shared by >=2 scientists
shared_institutions = {k: v for k, v in institution_scientists.items() if len(v) >= 2}

# Compute centrality metrics
inst_names = sorted(shared_institutions.keys())
n_inst = len(inst_names)

# Adjacency matrix (institutions are connected if they share scientists)
adj = np.zeros((n_inst, n_inst))
for i, inst_i in enumerate(inst_names):
    for j, inst_j in enumerate(inst_names):
        if i < j:
            shared = shared_institutions[inst_i] & shared_institutions[inst_j]
            adj[i][j] = len(shared)
            adj[j][i] = len(shared)

# Degree centrality: number of scientists affiliated
degree_centrality = {inst: len(shared_institutions[inst]) for inst in inst_names}

# Betweenness centrality (simplified: fraction of scientist pairs connected through this institution)
betweenness = {}
for inst in inst_names:
    bt = 0
    scientists_in_inst = shared_institutions[inst]
    all_scientists = list(scientist_institutions.keys())
    for s1, s2 in combinations(all_scientists, 2):
        if s1 in scientists_in_inst or s2 in scientists_in_inst:
            continue
        # Check if inst bridges s1 and s2
        s1_insts = scientist_institutions.get(s1, set())
        s2_insts = scientist_institutions.get(s2, set())
        if (s1_insts & {inst}) or (s2_insts & {inst}):
            continue
        # Simple: if s1 and s2 each share an institution with someone in this institution
    # Simpler measure: count of pairs connected through this institution
    n_affiliated = len(scientists_in_inst)
    bt = n_affiliated * (n_affiliated - 1) / 2  # pairs within
    betweenness[inst] = bt

# Sort by degree
sorted_inst = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Degree centrality
insts = [x[0] for x in sorted_inst]
degs = [x[1] for x in sorted_inst]
colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(insts)))
bars1 = ax1.barh(range(len(insts)), degs, color=colors[::-1])
ax1.set_yticks(range(len(insts)))
ax1.set_yticklabels(insts)
ax1.set_xlabel('Number of Scientists')
ax1.set_title('Institution Degree Centrality\n(# Scientists Affiliated)')
ax1.invert_yaxis()
for i, (bar, d) in enumerate(zip(bars1, degs)):
    ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, str(d),
             va='center', fontsize=10, fontweight='bold')

# Co-occurrence heatmap
cooc_matrix = np.zeros((n_inst, n_inst))
for i, inst_i in enumerate(inst_names):
    for j, inst_j in enumerate(inst_names):
        shared = shared_institutions[inst_i] & shared_institutions[inst_j]
        cooc_matrix[i][j] = len(shared)

mask = np.triu(np.ones_like(cooc_matrix, dtype=bool), k=1)
sns.heatmap(cooc_matrix, mask=mask, annot=True, fmt='.0f', cmap='YlOrRd',
            xticklabels=inst_names, yticklabels=inst_names,
            ax=ax2, cbar_kws={'label': 'Shared Scientists'}, linewidths=0.5)
ax2.set_title('Institution Co-occurrence Matrix\n(# Shared Scientists)')
ax2.tick_params(axis='both', labelsize=8)

fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig2_institution_network.png'))
plt.close()

print("  Degree centrality:")
for inst, deg in sorted_inst:
    print(f"    {inst}: {deg}")
print(f"  Betweenness (pair connectivity): {betweenness}")

# ─── ANALYSIS 3: Scientist similarity matrix (Jaccard) ───
print("\n=== Analysis 3: Scientist similarity matrix ===")
sci_names_ordered = sorted(scientists.keys())
n_sci = len(sci_names_ordered)
jaccard_matrix = np.zeros((n_sci, n_sci))

for i, s1 in enumerate(sci_names_ordered):
    insts1 = set(scientists[s1]['institutions'])
    for j, s2 in enumerate(sci_names_ordered):
        insts2 = set(scientists[s2]['institutions'])
        union = insts1 | insts2
        intersection = insts1 & insts2
        if len(union) > 0:
            jaccard_matrix[i][j] = len(intersection) / len(union)
        else:
            jaccard_matrix[i][j] = 0.0

fig, ax = plt.subplots(figsize=(14, 12))
# Short labels
short_labels = [n[:3] for n in sci_names_ordered]
sns.heatmap(jaccard_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r',
            xticklabels=short_labels, yticklabels=short_labels,
            ax=ax, linewidths=0.5, vmin=0, vmax=1,
            cbar_kws={'label': 'Jaccard Similarity'})
ax.set_title('Scientist Similarity Matrix\n(Jaccard Index on Shared Educational Institutions)')
ax.tick_params(axis='both', labelsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig3_scientist_similarity_heatmap.png'))
plt.close()

# Find top similar pairs
sim_pairs = []
for i in range(n_sci):
    for j in range(i+1, n_sci):
        sim_pairs.append((sci_names_ordered[i], sci_names_ordered[j], jaccard_matrix[i][j]))
sim_pairs.sort(key=lambda x: x[2], reverse=True)
print("  Top 10 most similar scientist pairs (Jaccard):")
for s1, s2, sim in sim_pairs[:10]:
    print(f"    {s1} — {s2}: {sim:.3f}")

# ─── ANALYSIS 4: Birth year vs education span ───
print("\n=== Analysis 4: Birth year vs education span ===")
data_points = []
for name, sci in scientists.items():
    by = sci['birth']
    n_inst = sci['n_institutions']
    if by is not None and by > 0:
        data_points.append((by, n_inst, name))

data_points.sort()
birth_years = [dp[0] for dp in data_points]
n_institutions = [dp[1] for dp in data_points]
names_pts = [dp[2] for dp in data_points]

# Regression
slope, intercept, r_value, p_value, std_err = stats.linregress(birth_years, n_institutions)

fig, ax = plt.subplots(figsize=(12, 7))
scatter = ax.scatter(birth_years, n_institutions, c=birth_years, cmap='coolwarm',
                     s=100, edgecolors='black', alpha=0.8, zorder=5)

# Regression line
x_range = np.linspace(min(birth_years)-5, max(birth_years)+5, 100)
y_pred = slope * x_range + intercept
ax.plot(x_range, y_pred, 'r--', linewidth=2, alpha=0.7,
        label=f'Regression: y={slope:.3f}x+{intercept:.1f}\n'
              f'R²={r_value**2:.3f}, p={p_value:.3f}')

# Annotate a few names
for i, (bx, ni, nm) in enumerate(data_points):
    if ni >= 3 or bx <= 1900 or bx >= 1930:
        ax.annotate(nm, (bx, ni), textcoords="offset points", xytext=(5, 8),
                   fontsize=7, alpha=0.8)

ax.set_xlabel('Birth Year')
ax.set_ylabel('Number of Educational Institutions Attended')
ax.set_title('Birth Year vs. Educational Institution Span\n(26 Senior Chinese Scientists)')
ax.legend(loc='upper left', fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig4_birth_year_vs_education.png'))
plt.close()

print(f"  Regression: slope={slope:.4f}, intercept={intercept:.2f}")
print(f"  R²={r_value**2:.4f}, p-value={p_value:.4f}")
print(f"  Pearson r={r_value:.4f}")

# ─── ANALYSIS 5: Temporal coverage (Gantt chart) ───
print("\n=== Analysis 5: Temporal coverage ===")
fig, ax = plt.subplots(figsize=(16, 10))

# Sort scientists by birth year
sci_sorted = sorted(scientists.items(), key=lambda x: x[1]['birth'] if x[1]['birth'] else 9999)

y_positions = []
labels = []
bars_data = []

for i, (name, sci) in enumerate(sci_sorted):
    if sci['birth'] is None:
        continue
    events = sci['events']
    if not events:
        continue
    
    min_year = sci['birth']
    max_year = max(ev['year'] for ev in events)
    
    # Assign generation color
    if min_year and min_year < 1910:
        color = '#e74c3c'  # Gen1: Pioneer
        gen = 'Gen1 (Pioneer)'
    elif min_year and min_year < 1926:
        color = '#3498db'  # Gen2: Builder
        gen = 'Gen2 (Builder)'
    else:
        color = '#2ecc71'  # Gen3: Developer
        gen = 'Gen3 (Developer)'
    
    y_positions.append(i)
    labels.append(f"{name} ({min_year})")
    bars_data.append((min_year, max_year, color, name, gen))

# Draw bars
for i, (start, end, color, name, gen) in enumerate(bars_data):
    ax.barh(i, end - start, left=start, height=0.7, color=color, alpha=0.8, edgecolor='black', linewidth=0.5)
    # Mark birth year
    ax.plot(start, i, 'ko', markersize=4)

ax.set_yticks(range(len(y_positions)))
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel('Year')
ax.set_title('Temporal Coverage: Documented Lifespan of 26 Senior Chinese Scientists')

# Legend
legend_patches = [
    mpatches.Patch(color='#e74c3c', alpha=0.8, label='Gen1: Pioneer (<1910)'),
    mpatches.Patch(color='#3498db', alpha=0.8, label='Gen2: Builder (1917-1925)'),
    mpatches.Patch(color='#2ecc71', alpha=0.8, label='Gen3: Developer (1926-1935)'),
]
ax.legend(handles=legend_patches, loc='lower right', fontsize=9)

ax.grid(axis='x', alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig5_temporal_coverage_gantt.png'))
plt.close()

print("  Gantt chart saved.")
for name, sci in sci_sorted:
    if sci['birth']:
        events = sci['events']
        max_year = max(ev['year'] for ev in events) if events else sci['birth']
        span = max_year - sci['birth']
        print(f"    {name}: {sci['birth']}–{max_year} (span: {span} years, {sci['n_events']} events)")

# ─── ANALYSIS 6: Top-k institution combinations ───
print("\n=== Analysis 6: Top-k institution combinations ===")
pair_counter = Counter()
triple_counter = Counter()

# Only consider scientists with >=2 institutions
for name, sci in scientists.items():
    insts = sorted(sci['institutions'])
    if len(insts) >= 2:
        for combo in combinations(insts, 2):
            pair_counter[combo] += 1
    if len(insts) >= 3:
        for combo in combinations(insts, 3):
            triple_counter[combo] += 1

print("  Top-10 institution pairs:")
for pair, count in pair_counter.most_common(10):
    print(f"    {pair[0]} + {pair[1]}: {count} scientists")

print("  Top-10 institution triples:")
for triple, count in triple_counter.most_common(10):
    if count >= 2:
        print(f"    {triple[0]} + {triple[1]} + {triple[2]}: {count} scientists")

# ─── ANALYSIS 7: Mann-Whitney U test (Gen2 vs Gen3 education span) ───
print("\n=== Analysis 7: Mann-Whitney U test ===")
gen2_edu = []  # birth 1917-1925
gen3_edu = []  # birth 1926-1935

for name, sci in scientists.items():
    by = sci['birth']
    n_inst = sci['n_institutions']
    if by is None:
        continue
    if 1917 <= by <= 1925:
        gen2_edu.append(n_inst)
    elif 1926 <= by <= 1935:
        gen3_edu.append(n_inst)

print(f"  Gen2 (1917-1925): n={len(gen2_edu)}, institutions={gen2_edu}")
print(f"  Gen3 (1926-1935): n={len(gen3_edu)}, institutions={gen3_edu}")

if len(gen2_edu) >= 2 and len(gen3_edu) >= 2:
    u_stat, p_val = stats.mannwhitneyu(gen2_edu, gen3_edu, alternative='two-sided')
    print(f"  Mann-Whitney U = {u_stat:.2f}, p-value = {p_val:.4f}")
    
    # Effect size (Cliff's delta)
    all_vals = gen2_edu + gen3_edu
    n1, n2 = len(gen2_edu), len(gen3_edu)
    # Cliff's delta
    greater = sum(1 for g2 in gen2_edu for g3 in gen3_edu if g2 > g3)
    less = sum(1 for g2 in gen2_edu for g3 in gen3_edu if g2 < g3)
    cliff_delta = (greater - less) / (n1 * n2)
    print(f"  Cliff's delta (effect size) = {cliff_delta:.4f}")
    
    # Descriptive stats
    print(f"  Gen2 mean = {np.mean(gen2_edu):.2f}, median = {np.median(gen2_edu):.1f}, SD = {np.std(gen2_edu, ddof=1):.2f}")
    print(f"  Gen3 mean = {np.mean(gen3_edu):.2f}, median = {np.median(gen3_edu):.1f}, SD = {np.std(gen3_edu, ddof=1):.2f}")
else:
    print("  Not enough data for MWU test")

# ─── Additional: summary stats ───
print("\n=== Summary Statistics ===")
total_events = sum(s['n_events'] for s in scientists.values())
total_institutions = sum(s['n_institutions'] for s in scientists.values())
birth_years_valid = [s['birth'] for s in scientists.values() if s['birth']]
print(f"  Total scientists: {len(scientists)}")
print(f"  Total life events: {total_events}")
print(f"  Mean events per scientist: {total_events/len(scientists):.1f}")
print(f"  Birth year range: {min(birth_years_valid)}–{max(birth_years_valid)}")
print(f"  Mean institutions per scientist: {total_institutions/len(scientists):.2f}")
print(f"  Shared institutions (≥2 scientists): {len(shared_institutions)}")

# ─── Save computed data as JSON ───
output_data = {
    'decade_counts': {str(d): c for d, c in zip(decades, counts)},
    'institution_centrality': {inst: {'degree': deg, 'scientists': list(shared_institutions[inst])} 
                                for inst, deg in degree_centrality.items()},
    'top_pairs': [{'pair': list(p), 'count': c} for p, c in pair_counter.most_common(10)],
    'top_triples': [{'triple': list(t), 'count': c} for t, c in triple_counter.most_common(10) if c >= 2],
    'regression': {'slope': slope, 'intercept': intercept, 'r2': r_value**2, 'p_value': p_value},
    'mwu_test': {
        'gen2_n': len(gen2_edu), 'gen3_n': len(gen3_edu),
        'gen2_mean': float(np.mean(gen2_edu)), 'gen3_mean': float(np.mean(gen3_edu)),
        'gen2_median': float(np.median(gen2_edu)), 'gen3_median': float(np.median(gen3_edu)),
        'u_statistic': float(u_stat) if len(gen2_edu) >= 2 else None,
        'p_value': float(p_val) if len(gen2_edu) >= 2 else None,
        'cliff_delta': float(cliff_delta) if len(gen2_edu) >= 2 else None,
    }
}

with open(os.path.join(OUT_DIR, 'eda_results.json'), 'w') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)

print("\n✅ All analyses complete. Results saved to:", OUT_DIR)
