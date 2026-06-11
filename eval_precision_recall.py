#!/usr/bin/env python3
"""Full precision/recall evaluation on all 26 scientists."""

import json, os, re
from collections import defaultdict

CORPUS_DIR = "/home/tcb/老科学家年表/老科学家年表"
LLM_DIR = "/home/tcb/老科学家年表/analysis/llm_comparison"

# Load all LLM extractions
llm_data = {}
for f in sorted(os.listdir(LLM_DIR)):
    if f.endswith('_llm.json') and f != 'all_scientists_llm.json':
        name = f.replace('_llm.json', '')
        with open(os.path.join(LLM_DIR, f), encoding='utf-8') as fh:
            llm_data[name] = json.load(fh)

# ============================================================
# KNOWN INSTITUTION LIST (for regex-based ground truth)
# ============================================================
INSTITUTIONS = [
    "清华大学", "北京大学", "交通大学", "浙江大学", "同济大学", "中央大学", "国立中央大学",
    "中山大学", "武汉大学", "哈尔滨工业大学", "金陵大学", "西南联合大学", "厦门大学",
    "南京大学", "复旦大学", "南开大学", "北京航空学院", "北京钢铁学院",
    "中国科学技术大学", "唐山交通大学", "北洋大学", "东北大学", "重庆大学",
    "华中工学院", "华南工学院", "上海交通大学", "西安交通大学", "北京医学院",
    "华东师范大学", "北京师范大学", "兰州大学", "山东大学", "四川大学",
    "大连工学院", "东北工学院", "桂林中学", "聿怀中学", "苏州中学",
    "中国地质大学", "北京地质学院", "长春地质学院"
]

# Award patterns
AWARD_PATTERNS = [
    r'(国家(?:自然)?科学(?:技术)?(?:进步)?[奖等][奖等]?)',
    r'(全国科学大会奖)',
    r'(何梁何利[基基金]+[奖奖])',
    r'(中国工程院院士)',
    r'(中国科学院院士)',
    r'(全国[先优][进秀][工作者]+)',
    r'([^\s]{2,6}[省部][级]*[科科技][学技][进步奖]+)',
]

def normalize_inst(name):
    """Normalize institution names."""
    aliases = {
        "国立交通大学": "交通大学", "交通大学": "交通大学",
        "上海交通大学": "交通大学", "西安交通大学": "交通大学",
        "国立中央大学": "中央大学", "南京大学": "南京大学",
        "西南联合大学": "西南联合大学", "西南联大": "西南联合大学",
    }
    return aliases.get(name, name)

def check_precision(text, llm_entry):
    """Check how many LLM-extracted facts are actually in the text."""
    results = {}
    
    # 1. Education institutions
    edu_extracted = []
    for edu in llm_entry.get("education", []):
        inst = edu.get("institution", "")
        if inst and edu.get("status") != "declined":
            edu_extracted.append(inst)
    
    edu_correct = 0
    edu_incorrect = []
    for inst in edu_extracted:
        # Search for institution in text (fuzzy)
        key = inst[:4] if len(inst) >= 4 else inst
        if key in text:
            edu_correct += 1
        else:
            # Try alternate forms
            normed = normalize_inst(inst)
            if normed[:3] in text:
                edu_correct += 1
            else:
                edu_incorrect.append(inst)
    
    results["edu_precision"] = edu_correct / max(len(edu_extracted), 1)
    results["edu_correct"] = edu_correct
    results["edu_total"] = len(edu_extracted)
    results["edu_incorrect"] = edu_incorrect
    
    # 2. Awards
    awards_extracted = [a.get("name", "") for a in llm_entry.get("awards", []) if a.get("name")]
    awards_correct = 0
    for award in awards_extracted:
        key = award[:6] if len(award) >= 6 else award
        if key in text:
            awards_correct += 1
    
    results["award_precision"] = awards_correct / max(len(awards_extracted), 1)
    results["award_correct"] = awards_correct
    results["award_total"] = len(awards_extracted)
    
    # 3. Birth year
    birth_year = llm_entry.get("person", {}).get("birth", {}).get("year")
    death_year = llm_entry.get("person", {}).get("death", {}).get("year") if llm_entry.get("person", {}).get("death") else None
    
    # Find birth year in text
    birth_patterns = [
        rf'{birth_year}年.*?出[生诞]',
        rf'出[生诞].*?{birth_year}年',
        rf'生于{birth_year}年',
        rf'({birth_year})年\d月.*?生',
    ]
    birth_found = False
    for p in birth_patterns:
        if re.search(p, text):
            birth_found = True
            break
    
    results["birth_correct"] = birth_found
    results["birth_year"] = birth_year
    
    return results

def check_recall(text, llm_entry):
    """Check how many regex-extractable facts the LLM captured."""
    results = {}
    
    # 1. Education recall: regex-extract institutions, check if LLM got them
    regex_insts = set()
    for inst in INSTITUTIONS:
        if inst in text:
            regex_insts.add(normalize_inst(inst))
    
    llm_insts = set()
    for edu in llm_entry.get("education", []):
        inst = edu.get("institution", "")
        if inst and edu.get("status") != "declined":
            llm_insts.add(normalize_inst(inst))
    
    if regex_insts:
        captured = regex_insts & llm_insts
        results["edu_recall"] = len(captured) / len(regex_insts)
        results["edu_regex_count"] = len(regex_insts)
        results["edu_captured"] = len(captured)
        results["edu_missed"] = list(regex_insts - llm_insts)
    else:
        results["edu_recall"] = None
        results["edu_regex_count"] = 0
    
    # 2. Award recall
    regex_awards = set()
    for pattern in AWARD_PATTERNS:
        for m in re.finditer(pattern, text):
            regex_awards.add(m.group(1))
    
    llm_awards = set()
    for a in llm_entry.get("awards", []):
        name = a.get("name", "")
        if name:
            llm_awards.add(name)
    
    if regex_awards:
        # Fuzzy match awards
        captured = 0
        for ra in regex_awards:
            key = ra[:4]
            for la in llm_awards:
                if key in la or ra in la:
                    captured += 1
                    break
        results["award_recall"] = captured / len(regex_awards)
        results["award_regex_count"] = len(regex_awards)
        results["award_captured"] = captured
    else:
        results["award_recall"] = None
        results["award_regex_count"] = 0
    
    return results

# ============================================================
# RUN EVALUATION
# ============================================================
print("=" * 70)
print("FULL PRECISION/RECALL EVALUATION ON ALL 26 SCIENTISTS")
print("=" * 70)

all_precision = []
all_recall = []

for name in sorted(llm_data.keys()):
    txt_path = os.path.join(CORPUS_DIR, f"{name}.txt")
    with open(txt_path, encoding='utf-8') as f:
        text = f.read()
    
    entry = llm_data[name]
    if "error" in entry:
        continue
    
    prec = check_precision(text, entry)
    rec = check_recall(text, entry)
    
    all_precision.append((name, prec))
    all_recall.append((name, rec))

# ============================================================
# AGGREGATE RESULTS
# ============================================================

# Precision aggregates
edu_precisions = [p["edu_precision"] for _, p in all_precision]
award_precisions = [p["award_precision"] for _, p in all_precision]
birth_correct = sum(1 for _, p in all_precision if p["birth_correct"])

# Total correct/total
total_edu_correct = sum(p["edu_correct"] for _, p in all_precision)
total_edu_extracted = sum(p["edu_total"] for _, p in all_precision)
total_award_correct = sum(p["award_correct"] for _, p in all_precision)
total_award_extracted = sum(p["award_total"] for _, p in all_precision)

print(f"\n{'='*70}")
print(f"PRECISION (Is LLM output factual?)")
print(f"{'='*70}")
print(f"  Education institutions: {total_edu_correct}/{total_edu_extracted} = {total_edu_correct/max(total_edu_extracted,1)*100:.1f}%")
print(f"  Awards: {total_award_correct}/{total_award_extracted} = {total_award_correct/max(total_award_extracted,1)*100:.1f}%")
print(f"  Birth year: {birth_correct}/26 = {birth_correct/26*100:.1f}%")

overall_prec = (total_edu_correct + total_award_correct + birth_correct) / max(total_edu_extracted + total_award_extracted + 26, 1)
print(f"  OVERALL PRECISION: {overall_prec*100:.1f}%")

# Per-scientist distribution
import numpy as np
print(f"\n  Education precision distribution:")
print(f"    Mean: {np.mean(edu_precisions):.3f}, Median: {np.median(edu_precisions):.3f}")
print(f"    Min: {min(edu_precisions):.3f}, Max: {max(edu_precisions):.3f}")
print(f"    Perfect (1.0): {sum(1 for p in edu_precisions if p == 1.0)}/26")
print(f"    <0.8: {sum(1 for p in edu_precisions if p < 0.8)}/26")

# Recall aggregates (only for scientists with regex-ground-truth)
edu_recalls = [r["edu_recall"] for _, r in all_recall if r["edu_recall"] is not None]
award_recalls = [r["award_recall"] for _, r in all_recall if r["award_recall"] is not None]

if edu_recalls:
    print(f"\n{'='*70}")
    print(f"RECALL (Did LLM capture regex-extractable facts?)")
    print(f"{'='*70}")
    print(f"  Education recall: mean={np.mean(edu_recalls):.3f}, median={np.median(edu_recalls):.3f}")
    print(f"    Perfect (1.0): {sum(1 for r in edu_recalls if r == 1.0)}/{len(edu_recalls)}")
    print(f"    <0.5: {sum(1 for r in edu_recalls if r < 0.5)}/{len(edu_recalls)}")

if award_recalls:
    print(f"  Award recall: mean={np.mean(award_recalls):.3f}, median={np.median(award_recalls):.3f}")
    print(f"    Perfect (1.0): {sum(1 for r in award_recalls if r == 1.0)}/{len(award_recalls)}")

# F1 scores
if edu_recalls and edu_precisions:
    # Only for scientists with both precision and recall
    f1_scores = []
    for (name, prec), (_, rec) in zip(all_precision, all_recall):
        p = prec["edu_precision"]
        r = rec["edu_recall"]
        if r is not None and p + r > 0:
            f1 = 2 * p * r / (p + r)
            f1_scores.append((name, f1))
    
    f1_vals = [f for _, f in f1_scores]
    print(f"\n  Education F1: mean={np.mean(f1_vals):.3f}, median={np.median(f1_vals):.3f}")
    
    # Bottom performers
    f1_scores.sort(key=lambda x: x[1])
    print(f"  Bottom 3 F1: {' | '.join(f'{n}:{f:.2f}' for n, f in f1_scores[:3])}")

# Incorrect extractions
print(f"\n{'='*70}")
print(f"INCORRECT EXTRACTIONS (Precision failures)")
print(f"{'='*70}")
for name, prec in all_precision:
    if prec["edu_incorrect"]:
        print(f"  {name}: {prec['edu_incorrect']}")

# Save
out = {
    "precision": {
        "education": f"{total_edu_correct/max(total_edu_extracted,1)*100:.1f}%",
        "awards": f"{total_award_correct/max(total_award_extracted,1)*100:.1f}%",
        "birth_year": f"{birth_correct/26*100:.1f}%",
        "overall": f"{overall_prec*100:.1f}%"
    },
    "recall": {
        "education_mean": f"{np.mean(edu_recalls):.3f}" if edu_recalls else "N/A",
        "award_mean": f"{np.mean(award_recalls):.3f}" if award_recalls else "N/A"
    }
}
with open("/home/tcb/老科学家年表/analysis/precision_recall.json", 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"\nSaved to: /home/tcb/老科学家年表/analysis/precision_recall.json")
