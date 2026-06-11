#!/usr/bin/env python3
"""Oral History Experiments 1-3: Uncertainty Quantification, Memory Bias, Cross-Validation."""

import json, os, re, sys
from collections import defaultdict, Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from scipy import stats

# Font setup
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

CORPUS_DIR = "/home/tcb/老科学家年表/老科学家年表"
LLM_DATA = "/home/tcb/老科学家年表/analysis/llm_comparison/all_scientists_llm.json"
OUTDIR = "/home/tcb/老科学家年表/analysis"
os.makedirs(OUTDIR, exist_ok=True)

# ============================================================
# EXPERIMENT 1: Uncertainty Quantification
# ============================================================

UNCERTAINTY_CATEGORIES = {
    "approximation": ["大概", "大约", "约", "左右", "前后", "上下", "许", "余"],
    "hedging": ["可能", "或许", "也许", "似乎", "好像", "仿佛", "恐怕", "未必", "不一定"],
    "memory_uncertainty": ["记得", "回忆", "据回忆", "据称", "据说", "据悉", "传闻"],
    "vagueness": ["不清楚", "不详", "不明", "未知", "待考", "存疑", "待查"],
    "inference": ["应", "当", "估计", "推测", "推断", "猜测"],
    "contradiction": ["说法不一", "另说", "或谓", "一说", "另一说"],
}

def count_uncertainty_markers(text):
    """Count uncertainty markers in text, returning category counts and positions."""
    results = {}
    for category, markers in UNCERTAINTY_CATEGORIES.items():
        count = 0
        positions = []
        for marker in markers:
            for m in re.finditer(re.escape(marker), text):
                count += 1
                positions.append(m.start())
        results[category] = {"count": count, "density": count / (len(text) / 1000)}  # per 1K chars
    return results

def analyze_uncertainty():
    """Analyze uncertainty markers across all 26 scientists."""
    print("=" * 60)
    print("EXPERIMENT 1: Uncertainty Quantification")
    print("=" * 60)
    
    txt_files = sorted([f for f in os.listdir(CORPUS_DIR) if f.endswith('.txt')])
    all_results = {}
    
    totals = defaultdict(int)
    total_chars = 0
    
    for fname in txt_files:
        name = fname.replace('.txt', '')
        filepath = os.path.join(CORPUS_DIR, fname)
        with open(filepath, encoding='utf-8') as f:
            text = f.read()
        
        result = count_uncertainty_markers(text)
        result["total_chars"] = len(text)
        result["total_markers"] = sum(v["count"] for v in result.values() if isinstance(v, dict))
        all_results[name] = result
        
        total_chars += len(text)
        for cat in UNCERTAINTY_CATEGORIES:
            totals[cat] += result[cat]["count"]
    
    # Summary stats
    print(f"\nTotal characters processed: {total_chars:,}")
    print(f"Total uncertainty markers found: {sum(totals.values()):,}")
    print(f"Overall density: {sum(totals.values()) / (total_chars/1000):.1f} per 1K chars")
    print("\nBy category:")
    for cat in UNCERTAINTY_CATEGORIES:
        print(f"  {cat}: {totals[cat]:4d} markers, density={totals[cat]/(total_chars/1000):.2f}/1K chars")
    
    # Per-scientist uncertainty density ranking
    densities = [(name, r["total_markers"] / (r["total_chars"]/1000)) 
                 for name, r in all_results.items()]
    densities.sort(key=lambda x: -x[1])
    
    print("\nTop 5 most uncertain (markers/1K chars):")
    for name, d in densities[:5]:
        print(f"  {name}: {d:.2f}")
    print("Top 5 most certain (fewest markers/1K chars):")
    for name, d in densities[-5:]:
        print(f"  {name}: {d:.2f}")
    
    return all_results, totals, total_chars

def plot_uncertainty(all_results, totals, total_chars):
    """Generate uncertainty heatmap and category distribution."""
    
    # Figure 1: Uncertainty density per scientist (horizontal bar)
    fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=150)
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    names = []
    densities = []
    for name, r in sorted(all_results.items(), key=lambda x: -x[1]["total_markers"]/max(x[1]["total_chars"]/1000, 1)):
        names.append(name)
        densities.append(r["total_markers"] / max(r["total_chars"]/1000, 1))
    
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(densities)))
    bars = ax.barh(range(len(names)), densities, color=colors, alpha=0.85)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=9, color='white')
    ax.set_xlabel('Uncertainty Markers per 1,000 Characters', color='white', fontsize=12)
    ax.set_title('Oral History Uncertainty Density by Scientist', 
                color='white', fontsize=14, pad=15, fontweight='bold')
    ax.tick_params(colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.invert_yaxis()
    
    plt.tight_layout()
    outpath = os.path.join(OUTDIR, "fig10_uncertainty_density.png")
    plt.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"  Saved: {outpath}")
    
    # Figure 2: Category breakdown (stacked bar top 10)
    fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=150)
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    categories = list(UNCERTAINTY_CATEGORIES.keys())
    cat_labels = ['Approximation', 'Hedging', 'Memory Unc.', 'Vagueness', 'Inference', 'Contradiction']
    colors_cat = ['#e94560', '#0f3460', '#533483', '#00b4d8', '#90e0ef', '#ff6b6b']
    
    # Use the sorted names from the earlier loop
    sorted_names = [name for name, _ in sorted(all_results.items(), 
                   key=lambda x: -x[1]["total_markers"]/max(x[1]["total_chars"]/1000, 1))][:10]
    
    x = np.arange(len(sorted_names))
    width = 0.12
    
    for i, (cat, clabel) in enumerate(zip(categories, cat_labels)):
        vals = [all_results[name][cat]["count"] for name in sorted_names]
        offset = i * width
        ax.bar(x + offset, vals, width, label=clabel, color=colors_cat[i], alpha=0.85)
    
    ax.set_xticks(x + width * 2.5)
    ax.set_xticklabels(sorted_names, fontsize=9, color='white', rotation=45, ha='right')
    ax.set_ylabel('Marker Count', color='white', fontsize=12)
    ax.set_title('Uncertainty Marker Categories (Top 10 Scientists)', 
                color='white', fontsize=14, pad=15, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
    ax.tick_params(colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    
    plt.tight_layout()
    outpath = os.path.join(OUTDIR, "fig11_uncertainty_categories.png")
    plt.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"  Saved: {outpath}")
    
    return all_results

# ============================================================
# EXPERIMENT 2: Memory Bias Detection
# ============================================================

def analyze_memory_bias(all_uncertainty):
    """Analyze memory bias via chi-square event density and uncertainty correlation."""
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Memory Bias Detection")
    print("=" * 60)
    
    # Load LLM extraction data for event years
    with open(LLM_DATA, encoding='utf-8') as f:
        llm_data = json.load(f)
    
    # Collect events by decade
    decade_events = defaultdict(int)
    decade_uncertainty = defaultdict(int)
    scientist_decades = defaultdict(lambda: defaultdict(int))
    
    for name, data in llm_data.items():
        if "error" in data:
            continue
        
        # From key_events
        for ev in data.get("key_events", []):
            year = ev.get("year", 0)
            if year and isinstance(year, int) and 1890 <= year <= 2020:
                decade = (year // 10) * 10
                decade_events[decade] += 1
                scientist_decades[name][decade] += 1
        
        # From education entries
        for edu in data.get("education", []):
            period = edu.get("period", "")
            years = re.findall(r'\d{4}', period)
            for y in years:
                year = int(y)
                if 1890 <= year <= 2020:
                    decade = (year // 10) * 10
                    decade_events[decade] += 1
    
    # Also count uncertainty by decade (using raw text segments near events)
    # For now, count all uncertainty markers and normalize
    
    decades = sorted(decade_events.keys())
    total_events = sum(decade_events.values())
    
    print(f"\nTotal events with dates: {total_events}")
    print(f"Decade range: {decades[0]}s–{decades[-1]}s")
    
    # Expected uniform distribution
    n_decades = len(decades)
    expected_per_decade = total_events / n_decades
    
    # Chi-square test
    observed = np.array([decade_events[d] for d in decades])
    expected = np.full(n_decades, expected_per_decade)
    chi2, p_value = stats.chisquare(observed, expected)
    
    print(f"\nChi-square test (uniform expectation):")
    print(f"  χ² = {chi2:.1f}, p = {p_value:.2e}")
    
    # Identify significantly over/under-represented decades
    print("\nSignificant deviations (z-score > 2):")
    z_scores = {}
    for d in decades:
        o = decade_events[d]
        e = expected_per_decade
        if e > 0:
            z = (o - e) / np.sqrt(e)
            z_scores[d] = z
            if abs(z) > 2:
                direction = "OVER" if z > 0 else "UNDER"
                print(f"  {d}s: {o} events (expected {e:.0f}), z={z:.1f} → {direction}-REPRESENTED")
    
    # Reminiscence bump analysis (15-30 age range → approx 1940s-1960s for this cohort)
    bump_decades = [1940, 1950, 1960]
    bump_events = sum(decade_events.get(d, 0) for d in bump_decades)
    non_bump_events = total_events - bump_events
    bump_pct = bump_events / total_events * 100
    print(f"\nReminiscence Bump (1940s-1960s = ages 15-30):")
    print(f"  Events in bump period: {bump_events} ({bump_pct:.1f}%)")
    print(f"  Events outside bump: {non_bump_events} ({100-bump_pct:.1f}%)")
    
    return decades, decade_events, p_value, z_scores, bump_pct

def plot_memory_bias(decades, decade_events, p_value, z_scores):
    """Plot memory bias: event density by decade with z-score annotation."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 7), dpi=150)
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    x = np.arange(len(decades))
    values = [decade_events[d] for d in decades]
    z_vals = [z_scores.get(d, 0) for d in decades]
    
    # Color bars by z-score
    colors = []
    for z in z_vals:
        if z > 2:
            colors.append('#e94560')  # Red = over-represented
        elif z < -2:
            colors.append('#0f3460')  # Blue = under-represented
        else:
            colors.append('#533483')  # Purple = normal
    
    ax.bar(x, values, color=colors, alpha=0.85, edgecolor='#333', linewidth=0.5)
    
    # Add significance markers
    for i, (d, z) in enumerate(zip(decades, z_vals)):
        if abs(z) > 2:
            marker = '***' if abs(z) > 3 else '**'
            ax.annotate(marker, (i, values[i]), textcoords="offset points", 
                       xytext=(0, 8), ha='center', color='yellow', fontsize=12, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels([f"{d}s" for d in decades], fontsize=10, color='white')
    ax.set_ylabel('Event Count', color='white', fontsize=12)
    ax.set_title(f'Memory Bias: Event Density by Decade (χ² p={p_value:.1e})', 
                color='white', fontsize=14, pad=15, fontweight='bold')
    ax.tick_params(colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#e94560', alpha=0.85, label='Over-represented (z>2)'),
        Patch(facecolor='#0f3460', alpha=0.85, label='Under-represented (z<-2)'),
        Patch(facecolor='#533483', alpha=0.85, label='Expected range'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, 
             facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
    
    plt.tight_layout()
    outpath = os.path.join(OUTDIR, "fig12_memory_bias.png")
    plt.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"  Saved: {outpath}")

# ============================================================
# EXPERIMENT 3: Cross-Nianbiao Fact Verification
# ============================================================

def analyze_cross_validation():
    """Cross-validate facts between scientists' chronologies."""
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Cross-Nianbiao Fact Verification")
    print("=" * 60)
    
    with open(LLM_DATA, encoding='utf-8') as f:
        llm_data = json.load(f)
    
    # Extract career orgs, collaborators, education per scientist
    scientist_career = {}
    scientist_collaborators = {}
    scientist_education = {}
    
    for name, data in llm_data.items():
        if "error" in data:
            continue
        
        scientist_career[name] = set()
        for c in data.get("career", []):
            org = c.get("organization", "")
            period = c.get("period", "")
            if org:
                scientist_career[name].add((org, period))
        
        scientist_collaborators[name] = set()
        for c in data.get("collaborators", []):
            cname = c.get("name", "")
            context = c.get("context", "")
            if cname:
                scientist_collaborators[name].add((cname, context))
        
        scientist_education[name] = set()
        for e in data.get("education", []):
            inst = e.get("institution", "")
            period = e.get("period", "")
            if inst and e.get("status") != "declined":
                scientist_education[name].add((inst, period))
    
    names = list(scientist_career.keys())
    
    # Find overlapping career orgs
    print(f"\nCareer Organization Overlaps (pairs sharing ≥1 org):")
    career_overlaps = []
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            n1, n2 = names[i], names[j]
            shared = scientist_career[n1] & scientist_career[n2]
            if shared:
                career_overlaps.append((n1, n2, len(shared), list(shared)[:3]))
    
    career_overlaps.sort(key=lambda x: -x[2])
    for n1, n2, cnt, examples in career_overlaps[:10]:
        print(f"  {n1} ↔ {n2}: {cnt} shared orgs — {examples[0][0] if examples else ''}")
    
    # Find collaborator cross-references
    print(f"\nCollaborator Cross-References (scientist A lists scientist B as collaborator):")
    cross_refs = []
    for name_a in names:
        collabs = {c[0] for c in scientist_collaborators[name_a]}
        for name_b in names:
            if name_a != name_b and name_b in collabs:
                cross_refs.append((name_a, name_b))
    
    for a, b in cross_refs:
        # Check if B also lists A (reciprocal)
        reciprocal = b in {c[0] for c in scientist_collaborators.get(a, set())}
        b_collabs = {c[0] for c in scientist_collaborators.get(b, set())}
        confirmed = a in b_collabs
        print(f"  {a} → {b} {'[CONFIRMED]' if confirmed else '[UNILATERAL]'}")
    
    # Education overlaps
    print(f"\nEducational Institution Overlaps:")
    edu_overlaps = []
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            n1, n2 = names[i], names[j]
            shared = scientist_education[n1] & scientist_education[n2]
            if shared:
                edu_overlaps.append((n1, n2, len(shared), list(shared)))
    
    edu_overlaps.sort(key=lambda x: -x[2])
    for n1, n2, cnt, examples in edu_overlaps[:10]:
        insts = set(e[0] for e in examples)
        print(f"  {n1} ↔ {n2}: {cnt} shared institutions: {', '.join(list(insts)[:3])}")
    
    # Compute confirmation rate
    total_cross_refs = len(cross_refs)
    confirmed = sum(1 for a, b in cross_refs 
                   if a in {c[0] for c in scientist_collaborators.get(b, set())})
    
    print(f"\nCross-Reference Verification Summary:")
    print(f"  Total cross-references: {total_cross_refs}")
    print(f"  Reciprocally confirmed: {confirmed}")
    print(f"  Unilateral claims: {total_cross_refs - confirmed}")
    print(f"  Confirmation rate: {confirmed/max(total_cross_refs,1)*100:.1f}%")
    
    return career_overlaps, cross_refs, confirmed, total_cross_refs

# ============================================================
# MAIN
# ============================================================

def main():
    # Experiment 1
    all_uncertainty, totals, total_chars = analyze_uncertainty()
    plot_uncertainty(all_uncertainty, totals, total_chars)
    
    # Experiment 2
    decades, decade_events, p_value, z_scores, bump_pct = analyze_memory_bias(all_uncertainty)
    plot_memory_bias(decades, decade_events, p_value, z_scores)
    
    # Experiment 3
    career_overlaps, cross_refs, confirmed, total_cross_refs = analyze_cross_validation()
    
    # Save results
    results = {
        "exp1_uncertainty": {
            "total_markers": sum(totals.values()),
            "total_chars": total_chars,
            "overall_density": sum(totals.values()) / (total_chars/1000),
            "category_totals": dict(totals),
            "per_scientist": {n: {
                "markers": r["total_markers"],
                "density": r["total_markers"] / (r["total_chars"]/1000),
                "categories": {c: r[c]["count"] for c in UNCERTAINTY_CATEGORIES}
            } for n, r in all_uncertainty.items()}
        },
        "exp2_memory_bias": {
            "chi2": float(stats.chisquare(
                np.array([decade_events[d] for d in sorted(decade_events)]),
                np.full(len(decade_events), sum(decade_events.values())/len(decade_events))
            )[0]),
            "p_value": float(p_value),
            "bump_pct": bump_pct,
            "decade_events": {str(d): decade_events[d] for d in sorted(decade_events)},
            "z_scores": {str(d): round(z, 2) for d, z in z_scores.items()}
        },
        "exp3_cross_validation": {
            "total_cross_refs": total_cross_refs,
            "confirmed": confirmed,
            "confirmation_rate": confirmed/max(total_cross_refs,1)*100,
            "career_overlaps": len(career_overlaps),
            "cross_references": [{"from": a, "to": b} for a, b in cross_refs]
        }
    }
    
    outpath = os.path.join(OUTDIR, "oral_history_experiments.json")
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {outpath}")
    
    print("\n" + "=" * 60)
    print("EXPERIMENTS 1-3 COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
