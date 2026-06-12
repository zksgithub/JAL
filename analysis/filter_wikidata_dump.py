#!/usr/bin/env python3
"""
Stream-filter wikidata latest-all.json.gz for our 26 scientists.
Counts structured statements per entity and outputs per-field breakdown.
"""
import gzip
import json
import sys
import re
import os

# 26 scientists: Chinese name → English/Romanized variants for matching
SCIENTISTS = {
    "冯端": "Feng Duan",
    "戴元本": "Dai Yuanben",
    "沈克琦": "Shen Keqi", 
    "黄旭华": "Huang Xuhua",
    "潘家铮": "Pan Jiazheng",
    "唐明述": "Tang Mingshu",
    "王德滋": "Wang Dezi",
    "沈志云": "Shen Zhiyun",
    "彭士禄": "Peng Shilu",
    "赵仁恺": "Zhao Renkai",
    "黄纬禄": "Huang Weilu",
    "钱学森": "Qian Xuesen",
    "钱三强": "Qian Sanqiang",
    "钱伟长": "Qian Weichang",
    "周光召": "Zhou Guangzhao",
    "李政道": "Li Zhengdao",
    "杨振宁": "Yang Zhenning",
    "吴健雄": "Wu Jianxiong",
    "丁肇中": "Ding Zhaozhong",
    "邓稼先": "Deng Jiaxian",
    "王大珩": "Wang Daheng",
    "钱临照": "Qian Linzhao",
    "程开甲": "Cheng Kaijia",
    "于敏": "Yu Min",
    "陈能宽": "Chen Nengkuan",
    "王淦昌": "Wang Ganchang",
}

# Build search patterns: Chinese names + romanized variants
def build_patterns():
    patterns = {}
    for zh_name, en_name in SCIENTISTS.items():
        patterns[zh_name] = {
            'zh': zh_name,
            'en_variants': [en_name, en_name.replace(' ', '').lower(), en_name.split()[-1]],
        }
    return patterns

# Wikidata property IDs for our fields of interest
EDUCATION_PROPS = {'P69'}      # educated at
EMPLOYER_PROPS = {'P108'}       # employer  
AWARD_PROPS = {'P166'}          # award received
MENTOR_PROPS = {'P1066'}        # student of
# Collaborator detection: P1325 (significant person), P3342 (significant event participant)
COLLAB_PROPS = {'P1325', 'P3342'}
# Events: P793 (significant event)
EVENT_PROPS = {'P793'}
# Birth: P569, Death: P570
BIRTH_DEATH = {'P569', 'P570'}

def count_claims(entity):
    """Count structured claims by category for a Wikidata entity."""
    claims = entity.get('claims', {})
    
    counts = {
        'education': 0,
        'employer': 0,
        'awards': 0,
        'mentors': 0,
        'collaborators': 0,
        'events': 0,
        'birth_death': 0,
        'other': 0,
        'total': 0,
    }
    
    for prop_id, claim_list in claims.items():
        n = len(claim_list)
        counts['total'] += n
        
        if prop_id in EDUCATION_PROPS:
            counts['education'] += n
        elif prop_id in EMPLOYER_PROPS:
            counts['employer'] += n
        elif prop_id in AWARD_PROPS:
            counts['awards'] += n
        elif prop_id in MENTOR_PROPS:
            counts['mentors'] += n
        elif prop_id in COLLAB_PROPS:
            counts['collaborators'] += n
        elif prop_id in EVENT_PROPS:
            counts['events'] += n
        elif prop_id in BIRTH_DEATH:
            counts['birth_death'] += n
        else:
            counts['other'] += n
    
    return counts

def match_scientist(entity, patterns):
    """Check if entity matches any of our scientists by label."""
    labels = entity.get('labels', {})
    
    for zh_name, variants in patterns.items():
        # Check Chinese label
        if 'zh' in labels and labels['zh']['value'] == variants['zh']:
            return zh_name
        if 'zh-cn' in labels and labels['zh-cn']['value'] == variants['zh']:
            return zh_name
        if 'zh-hans' in labels and labels['zh-hans']['value'] == variants['zh']:
            return zh_name
        
        # Check English label
        if 'en' in labels:
            en_label = labels['en']['value'].lower()
            for variant in variants['en_variants']:
                if variant.lower() in en_label:
                    return zh_name
    
    return None

def main():
    dump_path = sys.argv[1] if len(sys.argv) > 1 else '/home/tcb/老科学家年表/wikidata_latest-all.json.gz'
    
    if not os.path.exists(dump_path):
        print(f"ERROR: Dump file not found: {dump_path}")
        print("Usage: python3 filter_wikidata_dump.py [path_to_dump.json.gz]")
        sys.exit(1)
    
    patterns = build_patterns()
    found = {}
    total_lines = 0
    matched_lines = 0
    
    print(f"Streaming {dump_path}...")
    print(f"Looking for {len(SCIENTISTS)} scientists...")
    print()
    
    with gzip.open(dump_path, 'rt', encoding='utf-8', errors='replace') as f:
        for line in f:
            total_lines += 1
            
            # Progress indicator
            if total_lines % 5000000 == 0:
                print(f"  Processed {total_lines/1e6:.0f}M entities, found {len(found)}/{len(SCIENTISTS)}...", flush=True)
            
            # Quick pre-filter: check if any Chinese name is in the line
            has_match = False
            for zh_name in SCIENTISTS:
                if zh_name in line:
                    has_match = True
                    break
            
            if not has_match:
                continue
            
            try:
                entity = json.loads(line.strip().rstrip(','))
            except json.JSONDecodeError:
                continue
            
            name = match_scientist(entity, patterns)
            if name:
                matched_lines += 1
                qid = entity.get('id', 'unknown')
                labels = entity.get('labels', {})
                zh_label = labels.get('zh', labels.get('zh-cn', labels.get('zh-hans', {})))
                en_label = labels.get('en', {})
                
                counts = count_claims(entity)
                
                found[name] = {
                    'qid': qid,
                    'label_zh': zh_label.get('value', name) if zh_label else name,
                    'label_en': en_label.get('value', '') if en_label else '',
                    'claims': counts,
                }
                
                print(f"  ✓ Found {name} ({qid}): {counts['total']} claims | "
                      f"edu={counts['education']} emp={counts['employer']} "
                      f"award={counts['awards']} mentor={counts['mentors']}", flush=True)
                
                if len(found) >= len(SCIENTISTS):
                    print(f"\nAll {len(SCIENTISTS)} scientists found! Stopping early.")
                    break
    
    print(f"\n{'='*60}")
    print(f"Processed {total_lines:,} entities, found {len(found)}/{len(SCIENTISTS)} scientists")
    print(f"{'='*60}")
    
    # Summary table
    print(f"\n{'Name':<12} {'QID':<12} {'Total':>6} {'Edu':>4} {'Emp':>4} {'Awd':>4} {'Men':>4}")
    print("-" * 52)
    
    total = {'education': 0, 'employer': 0, 'awards': 0, 'mentors': 0, 
             'collaborators': 0, 'events': 0, 'birth_death': 0, 'other': 0, 'total': 0}
    
    for name in sorted(found.keys()):
        info = found[name]
        c = info['claims']
        print(f"{name:<12} {info['qid']:<12} {c['total']:>6} {c['education']:>4} "
              f"{c['employer']:>4} {c['awards']:>4} {c['mentors']:>4}")
        
        for k in total:
            total[k] += c[k]
    
    print("-" * 52)
    print(f"{'TOTAL':<12} {'':<12} {total['total']:>6} {total['education']:>4} "
          f"{total['employer']:>4} {total['awards']:>4} {total['mentors']:>4}")
    
    # Per-field comparison with LLM
    llm_data = {
        'education': 210, 'employer': 353, 'awards': 337, 
        'mentors': 74, 'collaborators': 268, 'events': 523
    }
    
    print(f"\n{'='*60}")
    print(f"WIKIDATA vs LLM COMPARISON (queried, not estimated)")
    print(f"{'='*60}")
    print(f"{'Field':<20} {'Wikidata':>10} {'LLM':>10} {'Ratio':>10}")
    print("-" * 52)
    
    for field, llm_count in llm_data.items():
        wd_count = total.get(field, 0)
        ratio = f"{llm_count/wd_count:.1f}×" if wd_count > 0 else "new"
        print(f"{field:<20} {wd_count:>10} {llm_count:>10} {ratio:>10}")
    
    print("-" * 52)
    llm_total_sum = sum(llm_data.values())
    wd_total_relevant = sum(total.get(f, 0) for f in llm_data)
    print(f"{'Total (relevant)':<20} {wd_total_relevant:>10} {llm_total_sum:>10} {llm_total_sum/wd_total_relevant:.1f}×" if wd_total_relevant > 0 else "N/A")
    print(f"{'WER (all claims)':<20} {total['total']:>10} {1765:>10} {1765/total['total']:.1f}×" if total['total'] > 0 else "N/A")
    
    # Save results
    out_path = '/home/tcb/老科学家年表/analysis/wikidata_queried_results.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'found_count': len(found),
            'total_entities_processed': total_lines,
            'total_claims': total,
            'per_scientist': {k: {'qid': v['qid'], 'claims': v['claims']} for k, v in found.items()},
            'comparison_with_llm': {
                'wikidata': {f: total.get(f, 0) for f in llm_data},
                'llm': llm_data,
                'wer': 1765 / total['total'] if total['total'] > 0 else None,
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {out_path}")

if __name__ == '__main__':
    main()
