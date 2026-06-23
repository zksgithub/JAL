# IP&M Conversion Plan

> **Goal:** Convert JAL manuscript to IP&M format — reframe from library special collections to computational information processing, expand methodology, restructure related work

**Current:** 30 pages, elsarticle JAL-format, library-focused framing
**Target:** IP&M, 30-35 pages, computaionally-focused, with technical depth

---

## Task 1: Set up IP&M template
- Create `paper_ipm.tex` from scratch with IP&M-appropriate structure
- Remove CJKutf8 dependency (IP&M LaTeX doesn't need it)
- Use standard Elsevier `elsarticle` class (same template family, just different journal)
- Sections: Introduction → Related Work → Method → Experiments → Results → Discussion → Conclusion
- **Verify:** `pdflatex paper_ipm.tex` compiles without errors on empty skeleton

## Task 2: Write new title and abstract
- Title: computational focus, no "Special Collections"
- Abstract: methodology-first, library as application domain
- **Verify:** Compiles, abstract fits IP&M style

## Task 3: Rewrite Introduction
- Cut library framing, build computational narrative
- Start with: unstructured biographical text → information extraction challenge
- Three motivations (keep, slightly rephrase for CS audience)
- Three RQs (keep as-is)
- Three contributions (keep, add passive→proactive)
- **Verify:** ~3 paragraphs, same key messages

## Task 4: Restructure Related Work
- ~Cut §2.1 (Scientist Archives) by 70%, keep only EventKG + LLM-KG papers
- ~Cut §2.2 (Nianbiao Tradition) by 60%, keep CIDOC-CRM + SNAC
- §2.3 (Narrative Studies) keep as-is or reduce 20%
- Add new subsections:
  - LLM-based Entity Extraction (Pan 2023, Carriero 2024, + 3 new refs)
  - Text-to-Knowledge-Graph Systems (REBEL, GPT-KG, + 2 new refs)
  - Wikidata Enrichment (keep Allison-Cassin)
- **Verify:** 6-8 new references added, total ~34-36 refs

## Task 5: Expand Methodology (§3)
- Add pseudocode for three-tier extraction (Algorithm 1)
- Add LLM prompt template (as figure or table)
- Add ablation study design (regex-only vs LLM-only vs full pipeline)
- Add Wikidata dump processing details
- **Verify:** §3 is now ~2x longer than before

## Task 6: Restructure Experiments (§4)
- Reorder: Extraction Performance → Wikidata Comparison → Indicator System
- Add precision/recall table for ALL entity types (not just education/awards)
- Add ablation results (regex-only baseline numbers)
- Keep all 11 figures
- **Verify:** Logical flow that builds from micro (extraction) to macro (indicators)

## Task 7: Rewrite Discussion (§5)
- Reframe: "Implications for Libraries" → "Methodological Contributions and Information Processing Implications"
- Add: comparison to existing text-to-KG systems
- Add: generalizability to other biographical corpora
- Keep MI1-MI5 indicator system as-is (already well-formatted)
- **Verify:** Discussion now ~1.5x longer

## Task 8: Final assembly and compile
- Merge all sections
- Update references (renumbered, new additions)
- Compile ×2
- **Verify:** Zero errors, zero warnings

---

## Files
- **Create:** `/home/tcb/老科学家年表/paper_ipm.tex`
- **Read/copy from:** `/home/tcb/老科学家年表/paper.tex`
- **Images:** reuse all from `analysis/fig*.png`
- **Data:** reuse `analysis/eda_results.json`, `analysis/wikidata_dump_verified.json`

## References to add (6-8)
- Huguet Cabot & Navigli (2021) — REBEL: Relation Extraction By End-to-end Language generation
- Yao et al. (2023) — GPT-KG or similar LLM-KG construction
- Chen et al. (2024) — LLM evaluation for entity extraction
- Min et al. (2023) — Factual precision of LLM extraction
- Wei et al. (2025) — Recent survey on LLM+KG integration
- Additional Wikidata/SPARQL enrichment papers
