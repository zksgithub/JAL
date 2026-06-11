#!/usr/bin/env python3
"""Experiment 4: Narrative Arc Classification via LLM."""

import json, os, sys, time

LLM_DATA = "/home/tcb/老科学家年表/analysis/llm_comparison/all_scientists_llm.json"
OUTDIR = "/home/tcb/老科学家年表/analysis"

# Load env key
env_path = os.path.expanduser("~/.hermes/.env")
env = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if not line or line[0] == "#":
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")

API_KEY = env.get("DEEPSEEK_API_KEY", "")
if len(API_KEY) < 10:
    print("ERROR: No valid API_KEY")
    sys.exit(1)

from openai import OpenAI
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# Load data
with open(LLM_DATA, encoding='utf-8') as f:
    data = json.load(f)

# Prepare scientist summaries for classification
summaries = []
for name, entry in sorted(data.items()):
    if "error" in entry:
        continue
    
    person = entry.get("person", {})
    birth = person.get("birth", {}).get("year", "?")
    death = person.get("death", {}).get("year", "?") if person.get("death") else "?"
    
    events = entry.get("key_events", [])
    event_summary = []
    for ev in events[:20]:  # top 20 events
        y = ev.get("year", "")
        e = ev.get("event", "")
        t = ev.get("type", "")
        event_summary.append(f"{y}: [{t}] {e}")
    
    awards = entry.get("awards", [])
    award_summary = ", ".join(f"{a.get('year','')} {a.get('name','')}" for a in awards[:5])
    
    education = entry.get("education", [])
    edu_summary = ", ".join(f"{e.get('period','')} {e.get('institution','')}" 
                           for e in education if e.get("status") != "declined")
    
    summaries.append({
        "name": name,
        "birth": birth,
        "death": death,
        "education": edu_summary,
        "key_events": "\n".join(event_summary),
        "awards": award_summary
    })

# Build prompt
system_prompt = """You are a narrative analyst specializing in oral history and biographical texts.

For each scientist, classify their life narrative into ONE of these archetypes:

1. TRIUMPH (凯旋型): Steady career advancement, major achievements, late-career recognition/awards, positive trajectory. Key events include breakthroughs, honors, and leadership roles.

2. RESILIENCE (受难型): Career interrupted by external events (war, political campaigns), followed by recovery and late recognition. Key events include displacement, hardship, then eventual vindication or awards.

3. STEADY (稳健型): Consistent research/scholarship career without dramatic interruptions. Steady publication record, institutional stability, few dramatic highs or lows.

4. ASCETIC (隐士型): Focused on research/teaching, minimal personal or political content. Events emphasize scholarship over careerism or recognition.

For each scientist, output:
{
  "name": "...",
  "arc_type": "TRIUMPH|RESILIENCE|STEADY|ASCETIC",
  "confidence": 0-1,
  "rationale": "1-2 sentence justification",
  "tone_positive": 0-1,  // overall positive tone (1 = very positive)
  "tone_negative": 0-1,  // overall negative tone (1 = very negative)
  "tone_neutral": 0-1,   // overall neutral/technical tone
  "key_turning_points": ["event1", "event2"]  // 2-3 most pivotal events
}

Output a JSON array of all scientists. No markdown, no explanation."""

user_content = "Classify the narrative arcs of these Chinese scientists based on their biographical event summaries:\n\n"
for s in summaries:
    user_content += f"--- {s['name']} ({s['birth']}–{s['death']}) ---\n"
    user_content += f"Education: {s['education']}\n"
    user_content += f"Key events:\n{s['key_events']}\n"
    user_content += f"Awards: {s['awards']}\n\n"

print(f"Sending classification request for {len(summaries)} scientists...")

try:
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0,
        max_tokens=4000,
        response_format={"type": "json_object"}
    )
    
    content = resp.choices[0].message.content
    result = json.loads(content)
    
    # result might be {"scientists": [...]} or just [...]
    if isinstance(result, dict) and "scientists" in result:
        classifications = result["scientists"]
    elif isinstance(result, list):
        classifications = result
    else:
        classifications = [result]
    
    print(f"Classified {len(classifications)} scientists")
    print(f"Tokens used: {resp.usage.total_tokens if resp.usage else '?'}")
    
    # Summary
    from collections import Counter
    types = Counter(c["arc_type"] for c in classifications)
    print("\nNarrative Arc Distribution:")
    for t, c in types.most_common():
        names = [c2["name"] for c2 in classifications if c2["arc_type"] == t]
        print(f"  {t}: {c} — {', '.join(names)}")
    
    # Tone averages
    avg_pos = sum(c.get("tone_positive", 0) for c in classifications) / len(classifications)
    avg_neg = sum(c.get("tone_negative", 0) for c in classifications) / len(classifications)
    avg_neu = sum(c.get("tone_neutral", 0) for c in classifications) / len(classifications)
    print(f"\nAverage tones: pos={avg_pos:.2f}, neg={avg_neg:.2f}, neutral={avg_neu:.2f}")
    
    # Save
    outpath = os.path.join(OUTDIR, "narrative_arcs.json")
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(classifications, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to: {outpath}")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
