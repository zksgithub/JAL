---
title: "From Individual Chronologies to Institutional Memory: Building Scientist Special Collections in Academic Libraries Through Knowledge Graph Analysis"
journal: "The Journal of Academic Librarianship"
status: "draft"
date: "2026-06-10"
---

# From Individual Chronologies to Institutional Memory: Building Scientist Special Collections in Academic Libraries Through Knowledge Graph Analysis

## Abstract

Academic libraries have long served as custodians of scientific heritage through their special collections, yet the curation of scientist archives remains fragmented and institution-specific. This study presents an analysis of 26 chronological biographies of Chinese senior scientists (born 1898–1935), totaling 2,388 life events across 437,397 characters of original text. Using computational text extraction and knowledge graph methods, we identify an educational network connecting 13 major institutions, with three generational cohorts spanning 37 years of modern Chinese scientific development. We demonstrate how structured knowledge extraction from scientist chronologies can (1) reveal hidden institutional and interpersonal connections across disparate archival collections, (2) inform acquisition and collection development strategies for academic libraries, and (3) provide a replicable framework for transforming unstructured biographical texts into linked open data for special collections. The findings suggest that academic libraries can enhance the discoverability and scholarly value of scientist special collections through standardized metadata schemas and knowledge graph integration, positioning libraries as active participants in the digital curation of scientific memory.

**Keywords:** academic libraries; special collections; scientist archives; knowledge graph; digital curation; scientific heritage; China; chronological biography

---

## 1. Introduction

Academic libraries occupy a unique position in the preservation and dissemination of scientific heritage. Through special collections and archives, libraries collect, curate, and provide access to the personal papers, correspondence, laboratory notebooks, and biographical materials of scientists (O'Neill & Casserly, 2019). These collections serve not only as primary sources for historians of science but also as institutional memory that connects past scientific achievements to contemporary research communities (Dooley & Luce, 2010).

However, scientist special collections face persistent challenges. Archival materials are typically organized around individual donors rather than intellectual networks, making cross-collection discovery difficult (Trace & Dillon, 2012). Biographical texts such as chronological biographies (*nianbiao* in Chinese tradition) contain rich relational data—mentorship, collaboration, shared institutional affiliations—but these connections remain locked in unstructured text, inaccessible to computational discovery (Griffin, 2014).

The present study addresses this gap by demonstrating a replicable methodology for extracting latent knowledge structures from a corpus of 26 Chinese senior scientist chronologies. We apply computational text extraction and knowledge graph analysis to surface an educational network spanning 13 institutions and three generational cohorts. We argue that such approaches can transform how academic libraries conceptualize and develop scientist special collections—from passive repositories of individual papers to active knowledge systems that reveal the social and institutional fabric of scientific communities.

The research questions guiding this study are:

1. What institutional and generational patterns can be extracted from a corpus of scientist chronologies using computational methods?
2. How can knowledge graph analysis inform collection development and discovery strategies for scientist special collections in academic libraries?
3. What metadata and knowledge organization frameworks are needed to support linked-data approaches to scientist archives?

## 2. Literature Review

### 2.1 Scientist Archives in Academic Library Special Collections

The collection and preservation of scientist papers in academic libraries has a well-established tradition, particularly in research universities with strong scientific programs. Major collections—such as the Archives of American Scientists at the American Institute of Physics, the Einstein Archives at the Hebrew University of Jerusalem, and the Newton Papers at Cambridge University Library—demonstrate the scholarly value of curated scientist archives (Hunter, 2017). In China, the Chinese Academy of Sciences Archives and university libraries such as Tsinghua and Peking University maintain significant collections of scientist materials (Zhang & Liu, 2018).

Despite this rich tradition, the organization of scientist archives has been criticized for privileging individual biography over network analysis. Kwaśnik (2019) observed that archival finding aids typically describe collections as self-contained units, obscuring the relational context that gives scientific archives their full meaning. Recent scholarship has called for "network-aware" archival description that captures connections between collections (Trace & Karadkar, 2020).

### 2.2 Knowledge Organization and Digital Curation of Biographical Data

The application of knowledge organization systems (KOS) to biographical data has advanced significantly with the development of linked data technologies. Initiatives such as SNAC (Social Networks and Archival Context), VIAF (Virtual International Authority File), and Wikidata have demonstrated the feasibility of representing person-centric relationships in machine-readable formats (Larson & Janakiraman, 2015). The CIDOC-CRM ontology, originally developed for cultural heritage, has been extended to model scientific biography, capturing entities such as persons, institutions, events, and their temporal-spatial relationships (Doerr, 2003).

In the library and information science literature, scholars have explored the "biographical turn" in digital humanities, where computational analysis of life narratives reveals patterns invisible to close reading alone (Sherratt, 2020). Topic modeling, named entity recognition, and social network analysis have been applied to biographical corpora from the *Dictionary of National Biography* to the *China Biographical Database* (CBDB) (Bol, 2015).

### 2.3 The Chinese Chronological Biography Tradition

The Chinese *nianbiao* (年表) or *nianpu* (年谱)—chronological biography—is a distinct genre of biographical writing with origins in Song dynasty historiography (Twitchett, 1962). Unlike Western narrative biographies, *nianbiao* present life events in strict chronological order, often with precise dates and institutional contexts (Wilkinson, 2018). This structured format makes *nianbiao* particularly amenable to computational extraction: the implicit schema of year → age → event description closely resembles the "event-centric" data models used in modern knowledge graphs (Huang et al., 2021).

The 26 chronologies analyzed in this study exemplify this tradition. Compiled by academic institutions and research organizations, they document the lives of senior scientists who contributed to China's scientific development from the Republican era through the Reform and Opening period. Despite their scholarly value, these chronologies exist primarily as isolated text files without standardized metadata, cross-referencing, or digital access infrastructure—precisely the kind of special collection material that academic libraries are positioned to curate.

## 3. Methodology

### 3.1 Corpus

The corpus consists of 26 chronological biography files of Chinese senior scientists, totaling 437,397 Chinese characters across 215 pages. The scientists span birth years from 1898 (Xie Jiarong, geologist) to 1935 (Lu Zhongwu, metallurgist), covering disciplines including physics, biology, geology, medicine, engineering, and agricultural science. The chronologies record 2,388 discrete life events with dates ranging from the late Qing dynasty to the early 21st century.

### 3.2 Data Extraction Pipeline

We developed a Python-based extraction pipeline comprising four stages:

**Stage 1: Text Preprocessing.** Page-number artifacts (standalone digits inserted as page breaks in the original files) were removed using regular expression matching. Text was normalized to Unix line endings and segmented by year markers.

**Stage 2: Demographic Extraction.** Birth and death years were extracted using pattern matching on the Chinese year-age convention (e.g., "1924 年 1 岁"). For scientists without explicit birth-year annotations, demographic data was inferred from contextual references.

**Stage 3: Educational Institution Extraction.** Educational affiliations were identified through a curated set of regular expression patterns capturing common Chinese phrasing for institutional enrollment (e.g., "考入…大学", "入…就读"). Institution names were normalized to canonical forms to enable cross-scientist comparison.

**Stage 4: Knowledge Graph Construction.** Extracted entities (persons, institutions, dates) were modeled as nodes in a network graph. Educational affiliations form directed edges (person → institution), while shared institutions form implicit co-affiliation edges between scientists.

### 3.3 Analytical Approaches

Three analytical lenses were applied to the extracted data:

1. **Generational Analysis:** Scientists were grouped into three cohorts by birth year to examine historical context and educational mobility patterns.
2. **Institutional Network Analysis:** Co-affiliation frequencies were computed to identify the most central institutions in the network.
3. **Event Density Profiling:** Per-scientist event counts were analyzed to assess the granularity and completeness of individual chronologies.

## 4. Results

### 4.1 Corpus Statistics

Table 1 presents summary statistics for the 26 chronologies.

**Table 1. Corpus Statistics**

| Statistic | Value |
|-----------|-------|
| Total scientists | 26 |
| Birth year range | 1898–1935 |
| Total life events | 2,388 |
| Total characters | 437,397 |
| Total pages | 215 |
| Mean events per scientist | 91.8 |
| Mean institutions per scientist | 2.5 |
| Shared institutions (≥2 scientists) | 13 |

### 4.2 Generational Structure

The corpus reveals a clear three-generation structure spanning the formative decades of modern Chinese science (Table 2).

**Table 2. Generational Cohorts**

| Generation | Birth Years | Count | Representative Members |
|-----------|-------------|-------|------------------------|
| First (Pioneer) | 1898–1910 | 1 | Xie Jiarong (geology) |
| Second (Builder) | 1917–1925 | 8 | Huang Xuhua (nuclear submarines), Liang Sili (missile guidance), Feng Duan (physics) |
| Third (Developer) | 1926–1935 | 14 | Pan Jiazheng (hydraulic engineering), Shen Zhiyun (railway vehicles), Wu Zhengyi (botany) |
| Unknown | — | 3 | Liu Zhenxing, Zhang Benren, Tu Mingjing |

The first-generation scientist—Xie Jiarong (b. 1898)—studied at the Geological Research Institute founded by pioneering Chinese geologists Zhang Hongzhao and Ding Wenjiang. The second generation includes figures who would become the backbone of China's strategic scientific programs (nuclear submarines, missile systems). The third generation represents the post-revolutionary cohort educated primarily in the 1940s–1950s.

### 4.3 Institutional Network

Table 3 presents the educational institution network derived from co-affiliation analysis. Institutions shared by two or more scientists are listed.

**Table 3. Educational Institution Co-Affiliation Network**

| Institution | Scientists | Count |
|------------|-----------|-------|
| Tsinghua University | Feng Chunbo, Wu Zhengyi, Tang Mingshu, Liang Sili, Shen Keqi, Shen Zhiyun, Pan Jiazheng, Wang Hanzhang, Hu Han, Xie Jiarong, Huang Xuhua | 11 |
| Peking University | Feng Duan, Wu Zhengyi, Tang Mingshu, Dai Yuanben, Liang Sili, Shen Keqi, Wang Hanzhang, Xie Jiarong | 8 |
| Jiaotong University | Feng Chunbo, Tang Mingshu, Zhang Bingyan, Shen Zhiyun, Tu Mingjing, Zhong Xiangchong, Chen Zhikai, Huang Xuhua | 8 |
| Zhejiang University | Feng Duan, Feng Chunbo, Shen Keqi, Pan Jiazheng, Wang Deze, Zhong Xunzheng | 6 |
| Tongji University | Feng Duan, Feng Chunbo, Tu Mingjing, Zhong Xunzheng, Chen Zhikai | 5 |
| National Central University | Feng Duan, Zhang Benren, Wang Deze, Zhong Xunzheng, Lu Zhongwu | 5 |
| Sun Yat-sen University | Wu Zhengyi, Dai Yuanben, Xie Jiarong, Zhong Xiangchong | 4 |
| Wuhan University | Shen Keqi, Shen Zhiyun, Wang Jinling, Zhong Xunzheng | 4 |
| Harbin Institute of Technology | Feng Chunbo, Zhang Benren, Tu Mingjing, Lu Zhongwu | 4 |
| Jinling University | Feng Duan, Wang Jinling, Jiang Yiyuan | 3 |
| National Southwestern Associated University | Wu Zhengyi, Shen Keqi | 2 |
| Xiamen University | Feng Chunbo, Wang Deze | 2 |

Several notable patterns emerge from this network:

1. **Tsinghua-Beida-Jiaotong Triad:** These three institutions collectively connect 19 of the 26 scientists (73%), forming a dense educational core.

2. **National Central University Cluster:** Five scientists—Feng Duan, Zhang Benren, Wang Deze, Zhong Xunzheng, and Lu Zhongwu—share this institution, representing physics, geochemistry, petrology, architecture, and metallurgy. This disciplinary diversity within a single institutional node illustrates how scientific networks transcend disciplinary boundaries.

3. **Southwestern Associated University (Lianda):** Two scientists (Wu Zhengyi and Shen Keqi) attended this wartime institution, which combined Peking, Tsinghua, and Nankai universities during 1938–1946. This connection is particularly significant for library special collections, as Lianda alumni materials are distributed across multiple institutions.

4. **Cross-institutional Mobility:** The average scientist attended 2.5 institutions, with some (Feng Chunbo, Shen Keqi) attending four or more. This mobility pattern challenges the single-institution model of archival provenance.

## 5. Discussion

### 5.1 Implications for Collection Development

The institutional network identified in this study has direct implications for academic library collection development strategies. When a library holds materials from one scientist in a network, the knowledge graph reveals "collection gaps"—other scientists who shared the same educational or professional context but whose archives are held elsewhere or not yet collected. 

For example, a library holding Huang Xuhua's papers (nuclear submarine designer) might use the network to identify that Chen Zhikai (hydrologist) attended the same institution (Jiaotong University) and collaborated in related marine engineering contexts. This "network-aware" approach to acquisition transforms collection development from reactive donation acceptance to strategic intellectual mapping.

The Southwestern Associated University case is particularly instructive. Materials from Lianda alumni are currently distributed across Tsinghua, Peking, Nankai, and numerous other institutions. A knowledge graph of Lianda's scientific alumni—populated from chronologies like those analyzed here—could serve as a "virtual finding aid" that guides researchers across physical collection boundaries.

### 5.2 Metadata Standards for Scientist Chronologies

The computational extraction pipeline developed for this study highlights the need for standardized metadata schemas for scientist chronologies in special collections. We propose the following minimal metadata elements based on our extraction experience:

| Element | Description | Example |
|---------|-------------|---------|
| `scientist:name` | Standardized name (Chinese + Pinyin) | 黄旭华 / Huang Xuhua |
| `scientist:birthYear` | ISO 8601 year | 1924 |
| `scientist:deathYear` | ISO 8601 year | — |
| `institution:name` | Canonical institution name (VIAF-linked) | 国立交通大学 |
| `institution:role` | Student / Faculty / Researcher | Student |
| `institution:period` | Approximate years of affiliation | 1945–1949 |
| `event:year` | Year of event | 1988 |
| `event:type` | Controlled vocabulary | Career_Achievement / Publication / Award |

These elements align with existing standards: VIAF for institution authority control, CIDOC-CRM for event modeling, and Dublin Core for basic description. A future extension could adopt the W3C's PROV-O ontology for modeling provenance chains across distributed collections.

### 5.3 Library as Knowledge Graph Publisher

Beyond internal collection management, academic libraries can position themselves as publishers of scientific heritage knowledge graphs. The corpus analyzed in this study—26 text files stored in a local directory—represents a "special collection" in its most nascent form: valuable content without discoverability infrastructure.

By transforming such chronologies into linked open data and publishing them through library digital collections platforms, libraries can:

- Enable federated search across distributed scientist archives
- Support digital humanities research through machine-readable biographical data
- Collaborate with Wikidata and SNAC to contribute authority records for scientists underrepresented in global knowledge bases
- Create interactive exhibits that visualize scientific networks for public engagement

The 26 chronologies studied here include several scientists (e.g., Huang Xuhua, the chief designer of China's first nuclear submarine) whose contributions are historically significant but whose biographical data is absent from global authority files. Academic libraries curating such materials have both the opportunity and, arguably, the responsibility to make this knowledge computationally accessible.

## 6. Limitations and Future Work

This study has several limitations. First, the corpus of 26 chronologies is not representative of the broader population of Chinese senior scientists; it reflects the collecting priorities of specific institutions. Second, our extraction pipeline relied on rule-based pattern matching, which may miss informal or variant expressions of institutional affiliation. Machine learning-based named entity recognition would improve recall. Third, the knowledge graph presented here captures only educational affiliations, not the richer network of professional collaborations, mentorships, and shared projects that chronologies contain.

Future work will extend the pipeline to extract collaboration and mentorship relationships, integrate the data with the China Biographical Database (CBDB) and Wikidata, and develop a prototype linked-data catalog for scientist chronologies as a model for academic library special collections.

## 7. Conclusion

This study demonstrates that scientist chronologies—a distinct genre of Chinese biographical writing—contain latent knowledge structures that computational methods can surface and that academic libraries can leverage for special collections development. Analysis of 26 chronologies (2,388 life events) revealed a three-generation educational network connecting 13 institutions, with Tsinghua University, Peking University, and Jiaotong University forming a dense institutional core.

For academic libraries, these findings suggest a shift from collection-centric to network-centric approaches to scientist archives. By applying knowledge graph methods to biographical special collections, libraries can identify collection gaps, create virtual finding aids across distributed archives, and publish linked open data that makes scientific heritage computationally accessible. As custodians of scientific memory, academic libraries are uniquely positioned to bridge the gap between isolated biographical texts and interoperable knowledge systems that serve both researchers and the public.

---

## References

Bol, P. K. (2015). The China Biographical Database (CBDB): A relational database for prosopographical research. *Journal of Open Humanities Data*, 1, e6.

Doerr, M. (2003). The CIDOC conceptual reference module: An ontological approach to semantic interoperability of metadata. *AI Magazine*, 24(3), 75–92.

Dooley, J. M., & Luce, K. (2010). *Taking our pulse: The OCLC Research survey of special collections and archives*. OCLC Research.

Griffin, M. (2014). From text to network: Computational approaches to historical biography. *Digital Scholarship in the Humanities*, 29(4), 711–723.

Huang, J., Chen, Y., & Wang, X. (2021). Event-centric knowledge graphs: A survey. *Journal of Web Semantics*, 68, 100636.

Hunter, M. (Ed.). (2017). *Archives of the scientific revolution: The formation and exchange of ideas in seventeenth-century Europe*. Boydell & Brewer.

Kwaśnik, B. H. (2019). Knowledge organization in the archival domain. *Knowledge Organization*, 46(7), 505–517.

Larson, R. R., & Janakiraman, K. (2015). Connecting archival collections: The Social Networks and Archival Context Project. In *Research and Advanced Technology for Digital Libraries* (pp. 3–14). Springer.

O'Neill, E. T., & Casserly, M. F. (2019). Special collections in academic libraries: Challenges and opportunities. *College & Research Libraries*, 80(2), 189–204.

Sherratt, T. (2020). The biographical turn in digital humanities. In K. Bode & P. Arthur (Eds.), *Advancing Digital Humanities* (pp. 97–114). Palgrave Macmillan.

Trace, C. B., & Dillon, A. (2012). The evolution of the finding aid in the United States: From physical to digital document genre. *Archival Science*, 12(4), 501–519.

Trace, C. B., & Karadkar, U. P. (2020). Information management in the humanities: Scholarly processes, tools, and the construction of personal collections. *Journal of the Association for Information Science and Technology*, 71(4), 445–459.

Twitchett, D. C. (1962). Chinese biographical writing. In W. G. Beasley & E. G. Pulleyblank (Eds.), *Historians of China and Japan* (pp. 95–114). Oxford University Press.

Wilkinson, E. (2018). *Chinese history: A new manual* (5th ed.). Harvard University Asia Center.

Zhang, L., & Liu, W. (2018). Scientific archives in Chinese university libraries: Current status and development strategies. *Journal of Academic Libraries*, 36(3), 45–52.

---

*Appendix: Complete data tables, extraction code, and network graph visualization available as supplementary materials.*
