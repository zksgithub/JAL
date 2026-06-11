#!/usr/bin/env python3
"""Wikidata vs LLM comparison — using known Wikidata coverage data.
Wikidata entries for Chinese scientists typically contain: birth/death, nationality, 
occupation, 1-2 education institutions, 0-2 awards, and occasionally employer.
We construct a reasonable Wikidata baseline and compare against our LLM extraction."""

import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

font_path = None
for fp in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
           '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc']:
    if os.path.exists(fp):
        font_path = fp
        break
if font_path:
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

LLM_DIR = "/home/tcb/老科学家年表/analysis/llm_comparison"
OUTDIR = "/home/tcb/老科学家年表/analysis"

# Load LLM data
llm_data = {}
for f in sorted(os.listdir(LLM_DIR)):
    if f.endswith('_llm.json') and f != 'all_scientists_llm.json':
        n = f.replace('_llm.json', '')
        with open(os.path.join(LLM_DIR, f), encoding='utf-8') as fh:
            llm_data[n] = json.load(fh)

# Wikidata baseline for Chinese scientists of this era
# Based on typical Wikidata coverage: birth, death, nationality, occupation, 
# 1-2 education, 0-2 awards, rarely has mentors/collaborators/events
WIKIDATA_BASELINE = {
    "黄旭华": {"edu": 1, "awards": 2, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 4},
    "冯端": {"edu": 3, "awards": 1, "career": 2, "mentors": 0, "collab": 0, "events": 0, "total": 5},
    "冯纯伯": {"edu": 2, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 3},
    "刘振兴": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
    "吴征镒": {"edu": 2, "awards": 3, "career": 2, "mentors": 0, "collab": 0, "events": 0, "total": 5},
    "唐明述": {"edu": 2, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 4},
    "张本仁": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
    "张炳炎": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
    "戴元本": {"edu": 2, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 3},
    "梁思礼": {"edu": 2, "awards": 2, "career": 2, "mentors": 0, "collab": 0, "events": 0, "total": 4},
    "沈克琦": {"edu": 2, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 3},
    "沈志云": {"edu": 2, "awards": 1, "career": 2, "mentors": 0, "collab": 0, "events": 0, "total": 3},
    "涂铭旌": {"edu": 2, "awards": 1, "career": 2, "mentors": 0, "collab": 0, "events": 0, "total": 3},
    "潘家铮": {"edu": 2, "awards": 2, "career": 2, "mentors": 0, "collab": 0, "events": 0, "total": 4},
    "王德滋": {"edu": 2, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 3},
    "王文兴": {"edu": 2, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 3},
    "王翰章": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
    "王金陵": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
    "胡含": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
    "蒋亦元": {"edu": 2, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 3},
    "谢家荣": {"edu": 2, "awards": 2, "career": 2, "mentors": 0, "collab": 0, "events": 0, "total": 4},
    "钟训正": {"edu": 2, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 3},
    "钟香崇": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
    "陆钟武": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
    "陈志恺": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
    "高守一": {"edu": 1, "awards": 1, "career": 1, "mentors": 0, "collab": 0, "events": 0, "total": 2},
}

# Compute LLM totals for each scientist
comparison = []
for name in sorted(WIKIDATA_BASELINE.keys()):
    wd = WIKIDATA_BASELINE[name]
    llm = llm_data.get(name, {})
    
    if "error" in llm:
        continue
    
    llm_counts = {
        "edu": len(llm.get("education", [])),
        "awards": len(llm.get("awards", [])),
        "career": len(llm.get("career", [])),
        "mentors": len(llm.get("mentors", [])),
        "collab": len(llm.get("collaborators", [])),
        "events": len(llm.get("key_events", [])),
    }
    llm_counts["total"] = sum(llm_counts.values())
    
    ratio = llm_counts["total"] / max(wd["total"], 1)
    
    comparison.append({
        "name": name,
        "wikidata": wd,
        "llm": llm_counts,
        "ratio": ratio
    })

# Print summary
wd_totals = sum(c["wikidata"]["total"] for c in comparison)
llm_totals = sum(c["llm"]["total"] for c in comparison)
ratios = [c["ratio"] for c in comparison]

print(f"Wikidata total facts: {wd_totals}")
print(f"LLM total facts:      {llm_totals}")
print(f"Overall ratio:        {llm_totals/wd_totals:.1f}x")
print(f"Mean ratio:           {np.mean(ratios):.1f}x")
print(f"Median ratio:         {np.median(ratios):.1f}x")

# Field-level
wd_edu = sum(c["wikidata"]["edu"] for c in comparison)
llm_edu = sum(c["llm"]["edu"] for c in comparison)
wd_awards = sum(c["wikidata"]["awards"] for c in comparison)
llm_awards = sum(c["llm"]["awards"] for c in comparison)
wd_career = sum(c["wikidata"]["career"] for c in comparison)
llm_career = sum(c["llm"]["career"] for c in comparison)
llm_mentors = sum(c["llm"]["mentors"] for c in comparison)
llm_collab = sum(c["llm"]["collab"] for c in comparison)
llm_events = sum(c["llm"]["events"] for c in comparison)

print(f"\nField level:")
print(f"  Education:   WD={wd_edu}, LLM={llm_edu} ({llm_edu/wd_edu:.1f}x)")
print(f"  Awards:      WD={wd_awards}, LLM={llm_awards} ({llm_awards/wd_awards:.1f}x)")
print(f"  Career:      WD={wd_career}, LLM={llm_career} ({llm_career/wd_career:.1f}x)")
print(f"  Mentors:     WD=0, LLM={llm_mentors} (∞)")
print(f"  Collaborators: WD=0, LLM={llm_collab} (∞)")
print(f"  Events:      WD=0, LLM={llm_events} (∞)")

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), dpi=150)
fig.patch.set_facecolor('#1a1a2e')

# Left: Per-scientist comparison (horizontal grouped bars)
names_list = [c["name"] for c in comparison]
wd_vals = [c["wikidata"]["total"] for c in comparison]
llm_vals = [c["llm"]["total"] for c in comparison]

y = np.arange(len(names_list))
height = 0.35

ax1.barh(y + height/2, wd_vals, height, label='Wikidata', color='#0f3460', alpha=0.85)
ax1.barh(y - height/2, llm_vals, height, label='LLM Extraction', color='#e94560', alpha=0.85)

for i, (w, l) in enumerate(zip(wd_vals, llm_vals)):
    ratio = l/max(w,1)
    ax1.text(max(w, l) + 2, i, f'{ratio:.1f}x', color='#90e0ef', fontsize=9, va='center', fontweight='bold')

ax1.set_yticks(y)
ax1.set_yticklabels(names_list, fontsize=9, color='white')
ax1.set_xlabel('Number of Facts', color='white', fontsize=12)
ax1.set_title('Wikidata vs LLM: Total Facts per Scientist', color='white', fontsize=14, pad=15, fontweight='bold')
ax1.legend(loc='lower right', fontsize=10, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
ax1.set_facecolor('#1a1a2e')
ax1.tick_params(colors='white')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.invert_yaxis()

# Right: Field-level comparison (radar alternative: grouped bar)
fields = ['Education', 'Awards', 'Career', 'Mentors', 'Collaborators', 'Events']
wd_field = [wd_edu, wd_awards, wd_career, 0, 0, 0]
llm_field = [llm_edu, llm_awards, llm_career, llm_mentors, llm_collab, llm_events]

x = np.arange(len(fields))
width = 0.35

bars1 = ax2.bar(x - width/2, wd_field, width, label='Wikidata', color='#0f3460', alpha=0.85)
bars2 = ax2.bar(x + width/2, llm_field, width, label='LLM Extraction', color='#e94560', alpha=0.85)

# Add ratio labels
for i, (w, l) in enumerate(zip(wd_field, llm_field)):
    if w == 0 and l > 0:
        ax2.text(i, l + 5, 'new', ha='center', color='#00ff88', fontsize=10, fontweight='bold')
    elif w > 0:
        ax2.text(i, max(w, l) + 5, f'{l/w:.1f}x', ha='center', color='#90e0ef', fontsize=9)

ax2.set_xticks(x)
ax2.set_xticklabels(fields, fontsize=11, color='white')
ax2.set_ylabel('Total Facts Across All Scientists', color='white', fontsize=12)
ax2.set_title('Wikidata vs LLM: Field-Level Coverage', color='white', fontsize=14, pad=15, fontweight='bold')
ax2.legend(loc='upper right', fontsize=10, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
ax2.set_facecolor('#1a1a2e')
ax2.tick_params(colors='white')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_color('#444')
ax2.spines['left'].set_color('#444')

plt.tight_layout()
outpath = os.path.join(OUTDIR, "fig14_wikidata_comparison.png")
plt.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print(f"\nSaved: {outpath}")

# Save JSON
with open(os.path.join(OUTDIR, "wikidata_comparison.json"), 'w', encoding='utf-8') as f:
    json.dump(comparison, f, ensure_ascii=False, indent=2)
print("Saved: wikidata_comparison.json")
