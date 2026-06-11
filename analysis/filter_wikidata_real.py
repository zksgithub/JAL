#!/usr/bin/env python3
"""Stream-filter wikidata dump for our actual 26 scientists."""
import gzip, json, sys, os, time

SCIENTISTS = {
    "冯端": ["Feng Duan"],
    "冯纯伯": ["Feng Chunbo"],
    "刘振兴": ["Liu Zhenxing"],
    "吴征镒": ["Wu Zhengyi"],
    "唐明述": ["Tang Mingshu"],
    "张本仁": ["Zhang Benren"],
    "张炳炎": ["Zhang Bingyan"],
    "戴元本": ["Dai Yuanben"],
    "梁思礼": ["Liang Sili"],
    "沈克琦": ["Shen Keqi"],
    "沈志云": ["Shen Zhiyun"],
    "涂铭旌": ["Tu Mingjing"],
    "潘家铮": ["Pan Jiazheng"],
    "王德滋": ["Wang Dezi"],
    "王文兴": ["Wang Wenxing"],
    "王翰章": ["Wang Hanzhang"],
    "王金陵": ["Wang Jinling"],
    "胡含": ["Hu Han"],
    "蒋亦元": ["Jiang Yiyuan"],
    "谢家荣": ["Xie Jiarong"],
    "钟训正": ["Zhong Xunzheng"],
    "钟香崇": ["Zhong Xiangchong"],
    "陆钟武": ["Lu Zhongwu"],
    "陈志恺": ["Chen Zhikai"],
    "高守一": ["Gao Shouyi"],
    "黄旭华": ["Huang Xuhua"],
}

EDUCATION_PROPS = {'P69'}
EMPLOYER_PROPS = {'P108'}
AWARD_PROPS = {'P166'}
MENTOR_PROPS = {'P1066'}
COLLAB_PROPS = {'P1325', 'P3342'}
EVENT_PROPS = {'P793'}
BIRTH_DEATH = {'P569', 'P570'}

def count_claims(entity):
    claims = entity.get('claims', {})
    counts = {'education':0,'employer':0,'awards':0,'mentors':0,
              'collaborators':0,'events':0,'birth_death':0,'other':0,'total':0}
    for pid, clist in claims.items():
        n = len(clist)
        counts['total'] += n
        if pid in EDUCATION_PROPS: counts['education'] += n
        elif pid in EMPLOYER_PROPS: counts['employer'] += n
        elif pid in AWARD_PROPS: counts['awards'] += n
        elif pid in MENTOR_PROPS: counts['mentors'] += n
        elif pid in COLLAB_PROPS: counts['collaborators'] += n
        elif pid in EVENT_PROPS: counts['events'] += n
        elif pid in BIRTH_DEATH: counts['birth_death'] += n
        else: counts['other'] += n
    return counts

def match_scientist(entity):
    labels = entity.get('labels', {})
    for zh_name, en_variants in SCIENTISTS.items():
        for lang in ['zh','zh-cn','zh-hans']:
            if lang in labels and labels[lang]['value'] == zh_name:
                return zh_name
        if 'en' in labels:
            en_label = labels['en']['value'].lower()
            for variant in en_variants:
                if variant.lower() in en_label:
                    return zh_name
    return None

dump_path = '/home/tcb/老科学家年表/wikidata_latest-all.json.gz'
found = {}
total = 0
t0 = time.time()

print(f"Streaming {dump_path} ({os.path.getsize(dump_path)/1e9:.1f} GB)...")
print(f"Looking for {len(SCIENTISTS)} scientists...\n")

with gzip.open(dump_path, 'rt', encoding='utf-8', errors='replace') as f:
    for line in f:
        total += 1
        if total % 5000000 == 0:
            elapsed = time.time() - t0
            print(f"  {total/1e6:.0f}M entities, {len(found)}/{len(SCIENTISTS)} found, {elapsed:.0f}s", flush=True)

        # Quick pre-filter: check if any Chinese name in line
        if not any(zh in line for zh in SCIENTISTS):
            continue

        try:
            entity = json.loads(line.strip().rstrip(','))
        except json.JSONDecodeError:
            continue

        name = match_scientist(entity)
        if name:
            qid = entity.get('id','?')
            counts = count_claims(entity)
            found[name] = {'qid': qid, 'claims': counts}
            en_label = entity.get('labels',{}).get('en',{}).get('value','')
            print(f"  ✓ {name} ({qid}) [{en_label}]: total={counts['total']} "
                  f"edu={counts['education']} emp={counts['employer']} "
                  f"awd={counts['awards']} men={counts['mentors']} "
                  f"col={counts['collaborators']} evt={counts['events']}", flush=True)
            if len(found) >= len(SCIENTISTS):
                break

elapsed = time.time() - t0
print(f"\n{'='*60}")
print(f"DONE: {total:,} entities in {elapsed:.0f}s ({total/elapsed:.0f} ent/s)")
print(f"Found: {len(found)}/{len(SCIENTISTS)} scientists")
print(f"{'='*60}")

# Summary
print(f"\n{'Name':<12} {'QID':<12} {'Total':>6} {'Edu':>4} {'Emp':>4} {'Awd':>4} {'Men':>4} {'Col':>4} {'Evt':>4}")
print("-"*60)
totals = {'education':0,'employer':0,'awards':0,'mentors':0,'collaborators':0,'events':0,'birth_death':0,'other':0,'total':0}
for name in sorted(found.keys()):
    c = found[name]['claims']
    print(f"{name:<12} {found[name]['qid']:<12} {c['total']:>6} {c['education']:>4} "
          f"{c['employer']:>4} {c['awards']:>4} {c['mentors']:>4} "
          f"{c['collaborators']:>4} {c['events']:>4}")
    for k in totals: totals[k] += c[k]
print("-"*60)
print(f"{'TOTAL':<12} {'':<12} {totals['total']:>6} {totals['education']:>4} "
      f"{totals['employer']:>4} {totals['awards']:>4} {totals['mentors']:>4} "
      f"{totals['collaborators']:>4} {totals['events']:>4}")

# Missing
missing = set(SCIENTISTS) - set(found)
if missing:
    print(f"\n⚠ NOT FOUND: {missing}")

# Comparison
print(f"\n{'='*60}")
print("WIKIDATA (QUERIED) vs LLM COMPARISON")
print(f"{'='*60}")
llm = {'education':210,'employer':353,'awards':337,'mentors':74,'collaborators':268,'events':523}
print(f"{'Field':<20} {'Wikidata':>10} {'LLM':>10} {'Ratio':>10}")
print("-"*52)
for field, llm_n in llm.items():
    wd_n = totals.get(field, 0)
    ratio = f"{llm_n/wd_n:.1f}×" if wd_n > 0 else "new"
    print(f"{field:<20} {wd_n:>10} {llm_n:>10} {ratio:>10}")
print("-"*52)
llm_total = sum(llm.values())
wd_total = sum(totals.get(f,0) for f in llm)
print(f"{'Total (relevant)':<20} {wd_total:>10} {llm_total:>10} {llm_total/wd_total:.1f}×" if wd_total > 0 else "N/A")
print(f"{'WER (all claims)':<20} {totals['total']:>10} {1765:>10} {1765/totals['total']:.1f}×" if totals['total'] > 0 else "N/A")

# Save
out = '/home/tcb/老科学家年表/analysis/wikidata_queried_results.json'
with open(out, 'w') as f:
    json.dump({
        'found': len(found), 'missing': list(missing), 'total_entities': total,
        'totals': totals, 'per_scientist': {k:{'qid':v['qid'],'claims':v['claims']} for k,v in found.items()},
        'comparison': {'wikidata':{f:totals.get(f,0) for f in llm}, 'llm':llm}
    }, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {out}")
