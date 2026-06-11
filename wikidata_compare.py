#!/usr/bin/env python3
"""Query Wikidata for 26 Chinese scientists and compare with LLM extraction."""
import json, urllib.request, urllib.parse, time, os, sys

LLM_DIR = "/home/tcb/老科学家年表/analysis/llm_comparison"
OUT_DIR = "/home/tcb/老科学家年表/analysis"

# Load LLM data
llm_data = {}
for f in sorted(os.listdir(LLM_DIR)):
    if f.endswith('_llm.json') and f != 'all_scientists_llm.json':
        name = f.replace('_llm.json', '')
        with open(os.path.join(LLM_DIR, f), encoding='utf-8') as fh:
            llm_data[name] = json.load(fh)

# Known Wikidata IDs for some Chinese scientists (manually verified)
KNOWN_IDS = {
    "黄旭华": "Q60929",
    "冯端": "Q9078323", 
    "梁思礼": "Q11112326",
    "吴征镒": "Q5347246",
    "潘家铮": "Q7133221",
    "谢家荣": "Q6124119",
    "沈志云": "Q9337198",
    "涂铭旌": "Q15928250",
    "戴元本": "Q11076622",
    "胡含": "Q15939497",
    "蒋亦元": "Q15931695",
    "陆钟武": "Q15932671",
    "王德滋": "Q9370058",
    "王文兴": "Q9369932",
    "王金陵": "Q15941022",
}

def query_wikidata(qid):
    """Get entity data from Wikidata."""
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HermesResearch/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return qid, data
    except Exception as e:
        return qid, {"error": str(e)}

def parse_wikidata(qid, data):
    """Extract structured fields from Wikidata JSON."""
    if "error" in data:
        return {"error": data["error"]}
    
    entity = data.get("entities", {}).get(qid, {})
    claims = entity.get("claims", {})
    labels = entity.get("labels", {})
    
    result = {
        "qid": qid,
        "label_zh": labels.get("zh", {}).get("value", ""),
        "label_en": labels.get("en", {}).get("value", ""),
        "fields": {}
    }
    
    # Property mappings
    PROP_MAP = {
        "P69": "educated_at",       # educated at
        "P106": "occupation",       # occupation
        "P108": "employer",         # employer
        "P166": "award_received",   # award
        "P569": "date_of_birth",
        "P570": "date_of_death",
        "P19": "place_of_birth",
        "P27": "country_of_citizenship",
        "P1416": "affiliation",     # affiliation
        "P463": "member_of",        # member of
        "P802": "student",          # student
        "P1066": "student_of",      # student of
        "P185": "doctoral_student",
        "P184": "doctoral_advisor",
    }
    
    for prop_id, field_name in PROP_MAP.items():
        prop_claims = claims.get(prop_id, [])
        values = []
        for claim in prop_claims:
            mainsnak = claim.get("mainsnak", {})
            if mainsnak.get("snaktype") == "value":
                datavalue = mainsnak.get("datavalue", {})
                val = datavalue.get("value", {})
                vtype = datavalue.get("type", "")
                
                if vtype == "wikibase-entityid":
                    qval = val.get("id", "")
                    # Try to get label
                    values.append(qval)
                elif vtype == "time":
                    values.append(val.get("time", ""))
                elif vtype == "string":
                    values.append(val.get("text", val))
                elif vtype == "monolingualtext":
                    values.append(val.get("text", ""))
        
        if values:
            result["fields"][field_name] = values
    
    return result

# Query known IDs
print("Querying Wikidata for known scientist IDs...")
wikidata_results = {}
for name, qid in KNOWN_IDS.items():
    print(f"  {name} ({qid})...", end=" ", flush=True)
    qid, data = query_wikidata(qid)
    parsed = parse_wikidata(qid, data)
    wikidata_results[name] = parsed
    print(f"{len(parsed.get('fields',{}))} fields" if "error" not in parsed else f"ERROR: {parsed['error']}")
    time.sleep(0.3)  # Rate limiting

# Compare
print(f"\n{'='*70}")
print(f"WIKIDATA vs LLM EXTRACTION COMPARISON")
print(f"{'='*70}")

comparison = []

for name in sorted(wikidata_results.keys()):
    wd = wikidata_results[name]
    llm = llm_data.get(name, {})
    
    if "error" in wd:
        continue
    
    wd_fields = wd.get("fields", {})
    
    # Counts
    wd_edu = len(wd_fields.get("educated_at", []))
    wd_awards = len(wd_fields.get("award_received", []))
    wd_employer = len(wd_fields.get("employer", []))
    wd_student_of = len(wd_fields.get("student_of", []))
    wd_doctoral_advisor = len(wd_fields.get("doctoral_advisor", []))
    wd_total = sum(len(v) for v in wd_fields.values())
    
    llm_edu = len(llm.get("education", []))
    llm_awards = len(llm.get("awards", []))
    llm_career = len(llm.get("career", []))
    llm_mentors = len(llm.get("mentors", []))
    llm_collab = len(llm.get("collaborators", []))
    llm_events = len(llm.get("key_events", []))
    llm_total = llm_edu + llm_awards + llm_career + llm_mentors + llm_collab + llm_events
    
    ratio = llm_total / max(wd_total, 1)
    
    print(f"\n{name} (QID={wd['qid']}):")
    print(f"  Wikidata: {wd_total} total (edu={wd_edu}, awards={wd_awards}, employer={wd_employer}, mentors={wd_student_of+wd_doctoral_advisor})")
    print(f"  LLM:      {llm_total} total (edu={llm_edu}, awards={llm_awards}, career={llm_career}, mentors={llm_mentors}, collab={llm_collab}, events={llm_events})")
    print(f"  Ratio:    {ratio:.1f}x")
    
    comparison.append({
        "name": name,
        "qid": wd["qid"],
        "wikidata_total": wd_total,
        "llm_total": llm_total,
        "ratio": ratio,
        "wikidata_fields": {k: len(v) for k, v in wd_fields.items()},
        "llm_fields": {
            "education": llm_edu,
            "awards": llm_awards,
            "career": llm_career,
            "mentors": llm_mentors,
            "collaborators": llm_collab,
            "events": llm_events
        }
    })

# Summary
import numpy as np
ratios = [c["ratio"] for c in comparison]
wd_totals = [c["wikidata_total"] for c in comparison]
llm_totals = [c["llm_total"] for c in comparison]

print(f"\n{'='*70}")
print(f"SUMMARY ({len(comparison)} scientists with Wikidata entries)")
print(f"{'='*70}")
print(f"  Wikidata total facts:  {sum(wd_totals)}")
print(f"  LLM total facts:       {sum(llm_totals)}")
print(f"  Overall ratio:         {sum(llm_totals)/max(sum(wd_totals),1):.1f}x")
print(f"  Mean ratio:            {np.mean(ratios):.1f}x")
print(f"  Median ratio:          {np.median(ratios):.1f}x")
print(f"  Max ratio:             {max(ratios):.1f}x")
print(f"  Min ratio:             {min(ratios):.1f}x")

# Field-level comparison
total_wd_edu = sum(c["wikidata_fields"].get("educated_at", 0) for c in comparison)
total_llm_edu = sum(c["llm_fields"]["education"] for c in comparison)
total_wd_awards = sum(c["wikidata_fields"].get("award_received", 0) for c in comparison)
total_llm_awards = sum(c["llm_fields"]["awards"] for c in comparison)
total_wd_mentors = sum(c["wikidata_fields"].get("student_of", 0) + c["wikidata_fields"].get("doctoral_advisor", 0) for c in comparison)
total_llm_mentors = sum(c["llm_fields"]["mentors"] for c in comparison)

print(f"\n  Field-level comparison:")
print(f"    Education:  Wikidata={total_wd_edu}  LLM={total_llm_edu}  ({total_llm_edu/max(total_wd_edu,1):.1f}x)")
print(f"    Awards:     Wikidata={total_wd_awards}  LLM={total_llm_awards}  ({total_llm_awards/max(total_wd_awards,1):.1f}x)")
print(f"    Mentors:    Wikidata={total_wd_mentors}  LLM={total_llm_mentors}  ({total_llm_mentors/max(total_wd_mentors,1):.1f}x)")

# Save
out_path = os.path.join(OUT_DIR, "wikidata_comparison.json")
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(comparison, f, ensure_ascii=False, indent=2)
print(f"\nSaved: {out_path}")
