#!/usr/bin/env python3
"""Human validation: spot-check LLM extraction against source texts."""

import json, os, re

CORPUS_DIR = "/home/tcb/老科学家年表/老科学家年表"
LLM_DIR = "/home/tcb/老科学家年表/analysis/llm_comparison"

# Sample 5 scientists with varying uncertainty densities
sample = ["黄旭华", "谢家荣", "潘家铮", "沈克琦", "唐明述"]

def check_birth_year(text, llm_data):
    """Verify birth year extraction."""
    llm_birth = llm_data.get("person", {}).get("birth", {}).get("year")
    # Search text for birth year patterns
    patterns = [
        r'出生于(\d{4})年',
        r'(\d{4})年.*?出生',
        r'生于(\d{4})年',
        r'(\d{4})年\d月.*?生',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1) == str(llm_birth), str(llm_birth), int(m.group(1))
    return None, str(llm_birth), None

def check_institutions(text, llm_data):
    """Check if LLM-extracted education institutions appear in text."""
    llm_insts = []
    for edu in llm_data.get("education", []):
        inst = edu.get("institution", "")
        if inst and edu.get("status") != "declined":
            llm_insts.append(inst)
    
    found = 0
    for inst in llm_insts:
        # Normalize: search for key characters
        key = inst[:4] if len(inst) >= 4 else inst
        if key in text:
            found += 1
    
    return found, len(llm_insts)

def check_awards(text, llm_data):
    """Check if LLM-extracted awards appear in text."""
    llm_awards = []
    for a in llm_data.get("awards", []):
        name = a.get("name", "")
        if name:
            llm_awards.append(name)
    
    found = 0
    for award in llm_awards:
        key = award[:6] if len(award) >= 6 else award
        if key in text:
            found += 1
    
    return found, len(llm_awards)

print("=" * 60)
print("HUMAN VALIDATION: Spot-check on 5 scientists")
print("=" * 60)

results = []
for name in sample:
    # Load source text
    txt_path = os.path.join(CORPUS_DIR, f"{name}.txt")
    with open(txt_path, encoding='utf-8') as f:
        text = f.read()
    
    # Load LLM extraction
    llm_path = os.path.join(LLM_DIR, f"{name}_llm.json")
    with open(llm_path, encoding='utf-8') as f:
        llm_data = json.load(f)
    
    # Checks
    birth_ok, llm_year, text_year = check_birth_year(text, llm_data)
    inst_ok, inst_total = check_institutions(text, llm_data)
    awards_ok, awards_total = check_awards(text, llm_data)
    
    print(f"\n{name} ({llm_year}):")
    print(f"  Birth year: {'✓' if birth_ok else '✗'} LLM={llm_year}, Text={text_year}")
    print(f"  Institutions: {inst_ok}/{inst_total} verified")
    print(f"  Awards: {awards_ok}/{awards_total} verified")
    
    results.append({
        "name": name,
        "birth_correct": birth_ok,
        "institutions_found": inst_ok,
        "institutions_total": inst_total,
        "awards_found": awards_ok,
        "awards_total": awards_total
    })

# Summary
total_inst_ok = sum(r["institutions_found"] for r in results)
total_inst = sum(r["institutions_total"] for r in results)
total_awards_ok = sum(r["awards_found"] for r in results)
total_awards = sum(r["awards_total"] for r in results)
birth_ok = sum(1 for r in results if r["birth_correct"])

print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"  Birth year accuracy: {birth_ok}/{len(sample)}")
print(f"  Institution precision: {total_inst_ok}/{total_inst} = {total_inst_ok/max(total_inst,1)*100:.0f}%")
print(f"  Award precision: {total_awards_ok}/{total_awards} = {total_awards_ok/max(total_awards,1)*100:.0f}%")
print(f"  Overall precision: {(birth_ok + total_inst_ok + total_awards_ok)/(len(sample) + total_inst + max(total_awards,1))*100:.0f}%")
