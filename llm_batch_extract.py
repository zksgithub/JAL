#!/usr/bin/env python3
"""Batch LLM extraction for all 26 scientist chronologies."""

import json, os, sys, time
from openai import OpenAI

CORPUS_DIR = "/home/tcb/老科学家年表/老科学家年表"
OUTPUT_DIR = "/home/tcb/老科学家年表/analysis/llm_comparison"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load env vars from .env file (avoiding *** in source)
env = {}
env_path = os.path.expanduser("~/.hermes/.env")
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
    print("ERROR: No valid DEEPSEEK_API_KEY found")
    sys.exit(1)

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

PROMPT = """You are an expert biographical data extractor for Chinese scientist chronologies (nianbiao). Output ONLY valid JSON, no markdown.

Extract:
1. person: {name_cn, name_pinyin, birth: {year, month?, day?, location?}, death: null|{year, month?, day?}, aliases: []}
2. family: {father: {name, aka?}, mother: {name}, spouse: {name, married?}, children: [{name, birth?, relation}], siblings: [{name, relation, aka?}]}
3. education: [{period, institution, dept?, degree?, location?, status: "attended"|"declined"}]
4. career: [{period, organization, role, note?}]
5. collaborators: [{name, relationship, period?, context?}]
6. mentors: [{name, field?, institution?}]
7. students: [{name, field?, institution?}]
8. key_events: [{year, event, type: "POLITICAL"|"CAREER_MILESTONE"|"ACHIEVEMENT"|"HONOR"|"PUBLICATION"|"PARTICIPATION"}]
9. awards: [{year, name}]

Rules: Only extract explicitly stated facts. Mark declined education with status="declined". For period: "YYYY-YYYY". Empty arrays for no data. Deduplicate."""

def extract_one(filepath, max_tries=3):
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    if len(text) > 80000:
        text = text[:80000]

    name = os.path.basename(filepath).replace(".txt", "")

    for attempt in range(max_tries):
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": text}
                ],
                temperature=0, max_tokens=8000,
                response_format={"type": "json_object"}
            )
            data = json.loads(resp.choices[0].message.content)
            data["_meta"] = {
                "file": os.path.basename(filepath),
                "chars": len(text),
                "tokens": resp.usage.total_tokens if resp.usage else 0,
                "time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            return name, data
        except json.JSONDecodeError as e:
            print(f"  JSON err {name} try {attempt+1}: {e}")
            if attempt < max_tries - 1:
                time.sleep(2)
        except Exception as e:
            print(f"  API err {name} try {attempt+1}: {e}")
            if attempt < max_tries - 1:
                time.sleep(5)

    print(f"  FAILED: {name}")
    return name, {"error": f"Failed after {max_tries} attempts"}

def main():
    files = sorted(f for f in os.listdir(CORPUS_DIR) if f.endswith(".txt"))
    print(f"Processing {len(files)} scientists...")

    all_data = {}
    ok = fail = 0
    tokens = 0

    for i, fname in enumerate(files):
        path = os.path.join(CORPUS_DIR, fname)
        print(f"[{i+1}/{len(files)}] {fname}...", end=" ", flush=True)
        name, data = extract_one(path)
        all_data[name] = data

        if "error" in data:
            fail += 1
            print("FAIL")
        else:
            ok += 1
            t = data["_meta"]["tokens"]
            tokens += t
            e = len(data.get("education", []))
            c = len(data.get("career", []))
            cl = len(data.get("collaborators", []))
            m = len(data.get("mentors", []))
            ev = len(data.get("key_events", []))
            print(f"OK t={t} edu={e} career={c} collab={cl} mentor={m} events={ev}")

        # Save individual
        out = os.path.join(OUTPUT_DIR, fname.replace(".txt", "_llm.json"))
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        if i < len(files) - 1:
            time.sleep(0.5)

    # Combined output
    combined = os.path.join(OUTPUT_DIR, "all_scientists_llm.json")
    with open(combined, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"DONE: {ok}/{len(files)} ok, {fail} fail, {tokens:,} tokens")
    print(f"Output: {combined}")

if __name__ == "__main__":
    main()
