# NER-Based Entity Extraction Report

## 1. Extraction Comparison: NER vs Regex

| Metric | Regex Baseline | NER Pipeline | Improvement |
|--------|---------------|--------------|-------------|
| Education institutions extracted | 26 entries | 596 entries | +570 |
| Career organizations | Not extracted | 306 | +306 |
| Classified events | Not classified | 3863 typed | +3863 |
| Awards/honors | Not extracted | 50 | +50 |
| Raw events (all) | 2,388 | 1758 | -630 |
| Unique institutions | 13 | 22 | +9 |

## 2. Institution Coverage (NER)

| Institution | Scientists |
|------------|-----------|
| 交通大学 | 134 |
| 北京大学 | 113 |
| 南京大学 | 112 |
| 清华大学 | 46 |
| 中央大学 | 45 |
| 浙江大学 | 21 |
| 中山大学 | 21 |
| 西南联大 | 20 |
| 哈尔滨工业大学 | 19 |
| 同济大学 | 18 |
| 金陵大学 | 13 |
| 华南工学院 | 5 |
| 武汉大学 | 5 |
| 北京师范大学 | 5 |
| 厦门大学 | 3 |

## 3. Event Type Distribution

| Event Type | Count | % |
|-----------|-------|---|
| PARTICIPATION | 986 | 25.5% |
| APPOINTMENT | 873 | 22.6% |
| PUBLICATION | 800 | 20.7% |
| EDUCATION_START | 378 | 9.8% |
| ATTENDANCE | 270 | 7.0% |
| EDUCATION | 153 | 4.0% |
| AWARD | 131 | 3.4% |
| HONOR | 73 | 1.9% |
| BIRTH | 58 | 1.5% |
| ELECTION | 54 | 1.4% |
| DEATH | 40 | 1.0% |
| MARRIAGE | 17 | 0.4% |
| WORK_TRANSFER | 15 | 0.4% |
| EDUCATION_END | 13 | 0.3% |
| WORK_ASSIGN | 2 | 0.1% |

## 4. Education Span Distribution

- Mean: 22.9
- Median: 15
- Range: 0–71
- Scientists with 0 detected educations: 1

## 5. Top Scientists by Entity Density

- **谢家荣**: 460 entities (edu:40, career:40, events:380, awards:0)
- **潘家铮**: 342 entities (edu:19, career:56, events:267, awards:0)
- **黄旭华**: 287 entities (edu:38, career:25, events:217, awards:7)
- **胡含**: 262 entities (edu:17, career:31, events:213, awards:1)
- **冯端**: 258 entities (edu:68, career:16, events:168, awards:6)
- **王翰章**: 236 entities (edu:2, career:1, events:232, awards:1)
- **张炳炎**: 232 entities (edu:7, career:12, events:212, awards:1)
- **王德滋**: 215 entities (edu:71, career:4, events:138, awards:2)
- **冯纯伯**: 194 entities (edu:31, career:8, events:155, awards:0)
- **沈志云**: 189 entities (edu:41, career:7, events:139, awards:2)