# LLM vs. Jieba NER: Extraction Quality Comparison

## Case Study: Huang Xuhua (黄旭华, 1924–, Nuclear Submarine Designer)

**Source text:** 646 lines, 44,882 characters, 95 life events

## 1. Head-to-Head Comparison

| Dimension | Jieba+Dict NER | LLM Extraction | Key Advantage |
|-----------|---------------|----------------|---------------|
| Education institutions | 3 (交通大学, duplicate mentions) | 3 attended + 2 declined, with periods, departments, locations | LLM distinguishes enrolled vs. declined; adds temporal-spatial context |
| Career organizations | 3 (shipbuilding bureau, 7th Academy, CSSC) | 6 organizations with precise roles and timelines | LLM infers organizational hierarchy (715所→719所) and career progression |
| Collaborators/Peers | 0 (not extracted) | 15 named collaborators with relationship type, period, context | LLM extracts implicit social network from event descriptions |
| Mentors | 0 (not extracted) | 4 mentors with fields and institutions | LLM identifies teacher-student relationships |
| Family members | 0 (not extracted) | 9 family members with relations, birth years | LLM reconstructs family tree |
| Event types | 4 types (keyword match) | 5 milestone types + full event descriptions (95 total) | LLM classifies by semantic meaning, not keyword |
| False positives | High (交通大学 mentioned 40+ times, counted as 40 'education' entities) | Low (canonical entities, deduplicated) | LLM understands that multiple mentions of same institution = one relationship |
| Declined/not-attended | Cannot distinguish | Correctly identifies 唐山交通大学 (declined) and 中央大学 (declined) | Critical for accuracy — regex would count these as attended |

## 2. Quantitative Summary

| Metric | Jieba NER | LLM | Ratio |
|--------|----------|-----|-------|
| Entities extracted (dedup) | 7 | 89 | 12.7x |
| Relationship types | 2 (education, career) | 8 (education, career, collaborator, mentor, family, award, political, milestone) | 4x |
| Named persons | 0 | 62 | ∞ |
| False positive rate (est.) | ~60% (duplicate mentions) | <5% | 12x reduction |
| Precision (education) | Low (3/40+ mentions) | High (3 attended / 5 extracted) | — |

## 3. Qualitative Advantages of LLM Extraction

1. **Contextual understanding:** LLM correctly identifies that Huang applied to 唐山交通大学 and was offered 中央大学 placement but *declined both* — a distinction regex/jieba cannot make.
2. **Relationship extraction:** LLM surfaces the Huang–Peng Shilu (彭士禄) collaboration, a historically significant partnership in China's nuclear submarine program that no keyword-based system would detect.
3. **Temporal reasoning:** LLM reconstructs career progression (technician→section chief→deputy chief engineer→chief designer) with precise periodization.
4. **Cross-document linking:** When applied to all 26 chronologies, LLM can identify shared collaborators (e.g., 彭士禄 appears in both Huang Xuhua's and Zhao Renkai's chronologies), building a true social network that regex cannot.
5. **Structured output:** LLM produces canonical JSON with VIAF-compatible entity types, directly ingestible into library metadata systems without manual curation.

## 4. Limitations of LLM Approach

- **Cost:** LLM API calls for all 26 chronologies (~440K chars) would require ~50K tokens per scientist, totaling ~1.3M tokens.
- **Hallucination risk:** LLM may infer relationships not explicitly stated. Mitigation: cross-reference against regex baseline for verification.
- **Reproducibility:** LLM outputs vary between runs. Mitigation: temperature=0, structured output format.

## 5. Recommendation for Paper

The paper should present a **hybrid extraction architecture**:
1. Regex baseline for demographic data (birth/death years) — fast, deterministic
2. LLM-based deep extraction for relationships, career trajectories, and event classification
3. Cross-validation: LLM outputs verified against regex baseline for factual consistency
4. This architecture reduces the NER pipeline from 4 tool dependencies (jieba+spaCy+dicts+heuristics) to 1 (LLM API), while providing 12.7× more entities and 4× more relationship types.