#!/usr/bin/env python3
"""Generate narrative arc visualization."""

import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

font_path = None
for fp in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
           '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
           '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc']:
    if os.path.exists(fp):
        font_path = fp
        break
if font_path:
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

OUTDIR = "/home/tcb/老科学家年表/analysis"
arcs_path = os.path.join(OUTDIR, "narrative_arcs.json")
with open(arcs_path, encoding='utf-8') as f:
    arcs = json.load(f)

# Plot: Narrative arc type distribution (pie + bar)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
fig.patch.set_facecolor('#1a1a2e')

# Pie chart
types = {}
for a in arcs:
    t = a["arc_type"]
    types[t] = types.get(t, 0) + 1

colors_pie = {'TRIUMPH': '#e94560', 'STEADY': '#0f3460', 'RESILIENCE': '#533483', 'ASCETIC': '#00b4d8'}
labels = ['TRIUMPH\n(n=15)', 'STEADY\n(n=6)', 'RESILIENCE\n(n=5)']
sizes = [types['TRIUMPH'], types['STEADY'], types['RESILIENCE']]
colors = [colors_pie['TRIUMPH'], colors_pie['STEADY'], colors_pie['RESILIENCE']]
explode = (0.05, 0, 0)

wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
                                     autopct='%1.0f%%', startangle=90,
                                     textprops={'color': 'white', 'fontsize': 11})
for at in autotexts:
    at.set_fontweight('bold')
ax1.set_title('Narrative Arc Distribution', color='white', fontsize=14, pad=15, fontweight='bold')
ax1.set_facecolor('#1a1a2e')

# Tone bar chart
names = [a["name"] for a in arcs]
pos_vals = [a.get("tone_positive", 0) for a in arcs]
neg_vals = [a.get("tone_negative", 0) for a in arcs]
neu_vals = [a.get("tone_neutral", 0) for a in arcs]

y = np.arange(len(names))
height = 0.25

ax2.barh(y + height, pos_vals, height, label='Positive', color='#e94560', alpha=0.85)
ax2.barh(y, neg_vals, height, label='Negative', color='#0f3460', alpha=0.85)
ax2.barh(y - height, neu_vals, height, label='Neutral', color='#533483', alpha=0.85)

ax2.set_yticks(y)
ax2.set_yticklabels(names, fontsize=8, color='white')
ax2.set_xlabel('Tone Score', color='white', fontsize=12)
ax2.set_title('Narrative Tone by Scientist', color='white', fontsize=14, pad=15, fontweight='bold')
ax2.legend(loc='lower right', fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
ax2.set_facecolor('#1a1a2e')
ax2.tick_params(colors='white')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_color('#444')
ax2.spines['left'].set_color('#444')

plt.tight_layout()
outpath = os.path.join(OUTDIR, "fig13_narrative_arcs.png")
plt.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print(f"Saved: {outpath}")
