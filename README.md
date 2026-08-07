# ⚖️ LexAI — Indian Legal Research Assistant

> An AI-powered legal research chatbot built for moot court competitions.
> Ask any Indian constitutional law question and get structured, citation-backed research in seconds — with automatic web augmentation from Indian Kanoon when local documents are insufficient.

<br>

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=flat-square&logo=streamlit)
![Gemini](https://img.shields.io/badge/Gemini-API-orange?style=flat-square&logo=google)
![RAG](https://img.shields.io/badge/Architecture-RAG-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

**⚖️[Live Demo →](https://lexai-indian-legal-rag-42fincgixja3g98rcfnpfx.streamlit.app/)** - Ask any question related to Indian law

<br>

---

## 🎯 What it does

LexAI is a **Retrieval Augmented Generation (RAG)** system that helps law students research Indian legal cases, constitutional provisions, and moot court arguments.

```
User asks a legal question
          ↓
Semantic search over curated Indian law documents (FAISS)
          ↓
Relevance score too low? → Auto-fetch from Indian Kanoon
          ↓
Combined context sent to Gemini with structured legal prompt
          ↓
Structured answer: legal issue · provisions · precedents ·
                   petitioner arguments · respondent arguments
```

<br>

---

## ✨ Key Features

| Feature | Detail |
|---------|--------|
| **Hybrid retrieval** | FAISS semantic search + automatic Indian Kanoon web augmentation |
| **Smart routing** | Relevance threshold decides local vs web search — no manual switching |
| **Structured output** | Every answer follows legal brief format with citations |
| **Argument modes** | Petitioner / Respondent / Both sides toggle |
| **Source transparency** | Shows every document chunk used with relevance % |
| **Download research** | Export complete research as text file |
| **Legal-specific embeddings** | BGE-base model with legal query prefix optimization |

<br>

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                       │
│                  (Streamlit — app.py)                    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   smart_search()                         │
│                                                          │
│   1. Embed query with BAAI/bge-base-en-v1.5             │
│   2. Search FAISS vector store                           │
│   3. Calculate avg relevance score                       │
│   4. Score < 0.45 → search Indian Kanoon via DDG        │
│   5. Return local + web results                          │
└──────────────────────────┬──────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌──────────────────┐      ┌──────────────────────┐
   │   FAISS Index    │      │  DuckDuckGo Search   │
   │  (local PDFs)   │      │  (Indian Kanoon)      │
   │  921 vectors     │      │  Live web results     │
   │  768 dimensions  │      │  No API key needed    │
   └──────────────────┘      └──────────────────────┘
              │                         │
              └────────────┬────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  generate_answer()                       │
│                                                          │
│   Builds structured legal prompt with:                   │
│   - Local document chunks                                │
│   - Web snippets (if retrieved)                          │
│   - Mode instruction (petitioner/respondent/both)        │
│   - 7-section legal brief format                         │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    Gemini API          │
              │  (gemini-3.6-flash)    │
              └────────────────────────┘
```

<br>

---

## 🔬 Technical Deep Dive

### Embeddings
Uses **BAAI/bge-base-en-v1.5** — a state-of-the-art bi-encoder model with 768-dimensional embeddings. Legal queries use the BGE-specific prefix:
```python
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
query_vector = model.encode(QUERY_PREFIX + question)
```
Document chunks are embedded without the prefix — this asymmetric approach is specific to BGE and improves retrieval quality significantly over symmetric models.

### Vector Search
**FAISS IndexFlatIP** (Inner Product) with L2 normalization — equivalent to cosine similarity. All 921 document chunks are searchable in milliseconds regardless of corpus size.

### Smart Routing — Hybrid Retrieval
```python
avg_score = sum(scores) / len(scores)
if avg_score < 0.45:          # threshold tuned empirically
    web_results = search_web(question)
```
The 0.45 threshold was chosen because BGE cosine similarity scores below this indicate the local corpus doesn't meaningfully cover the query topic — web augmentation then fills the gap without adding noise when local results are already strong.

### Document Chunking
```
Chunk size:    200 words
Overlap:       50 words
Strategy:      sliding window with overlap
               preserves context at chunk boundaries
```

### Legal Prompt Engineering
The system prompt instructs Gemini to structure every answer as a 7-section legal brief — matching the format used in actual Indian moot court competitions:
```
1. Legal Issue
2. Constitutional Provisions
3. Key Legal Principles
4. Landmark Judgments
5. Petitioner Arguments
6. Respondent Arguments
7. Conclusion
```

<br>

---

## 📚 Document Corpus

| Document | Coverage |
|----------|----------|
| Indian Constitution | Full text — all articles and schedules |
| KS Puttaswamy v Union of India (2017) | Right to privacy — landmark 9-judge bench |
| Maneka Gandhi v Union of India (1978) | Article 21 — personal liberty expansion |

*More judgments can be added by dropping PDFs in `documents/` and re-running `ingest.py`*

<br>

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.10+
Gemini API key (free at aistudio.google.com)
```

### Installation
```bash
# 1. Clone the repo
git clone https://github.com/[YOUR_USERNAME]/[REPO_NAME].git
cd [REPO_NAME]

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
echo GEMINI_API_KEY=your_key_here > .env

# 4. Add legal PDFs to documents/ folder

# 5. Build the vector store
python ingest.py

# 6. Run the app
streamlit run app.py
```

### Requirements
```
google-genai
sentence-transformers
faiss-cpu
pypdf
streamlit
python-dotenv
duckduckgo-search
numpy
```

<br>

---

## 📁 Project Structure

```
legal-rag-chatbot/
│
├── app.py              # Streamlit UI — complete frontend
├── rag.py              # Core RAG pipeline:
│                       #   search(), search_web(),
│                       #   smart_search(), generate_answer()
├── ingest.py           # Document ingestion pipeline:
│                       #   read_pdf(), chunk_text(),
│                       #   embed_chunks(), build_faiss_index()
│
├── documents/          # Indian law PDFs (add more here)
│   ├── constitution.pdf
│   └── puttaswamy.pdf
│
├── vector_store/       # Auto-generated by ingest.py
│   ├── index.faiss     # FAISS vector index
│   └── chunks.pkl      # Chunk text + metadata
│
├── requirements.txt
├── .env                # API key (never pushed to GitHub)
└── .gitignore
```

<br>

---

## 💡 Engineering Decisions & Tradeoffs

### Why RAG over fine-tuning?
Fine-tuning Gemini on legal data would require thousands of labeled examples and significant compute. RAG achieves the same result — grounded, citation-backed answers — with just a few PDFs and no training cost.

### Why FAISS over ChromaDB or Pinecone?
FAISS runs entirely locally with zero setup — no database server, no API key, no cost. For a corpus of ~1000 chunks, FAISS is faster than any managed vector database and requires no internet connection for retrieval.

### Why hybrid search over pure web search?
Pure web search makes 2 LLM calls per query (analyze + answer) and depends entirely on internet availability. The hybrid approach uses 1 LLM call for most queries and falls back to web only when needed — halving API usage while maintaining answer quality.

### Why BGE over MiniLM?
BGE-base scores ~8% higher on legal retrieval benchmarks than MiniLM-L6. The tradeoff is size (440MB vs 80MB) and speed — for a legal research tool where answer quality matters more than latency, BGE is the right choice.

<br>

---

## 🎓 What I Learned Building This

- **RAG architecture** — how retrieval-augmented generation works end to end, from chunking strategy to prompt construction
- **Vector similarity search** — FAISS IndexFlatIP, L2 normalization, cosine similarity at scale
- **Embedding models** — asymmetric retrieval with BGE, query prefix optimization
- **Hybrid retrieval** — designing relevance thresholds and fallback strategies
- **Prompt engineering** — structuring legal domain prompts for consistent, citation-backed output
- **Streamlit** — building production-quality ML-powered web applications in pure Python

<br>

---

## 🗺️ Roadmap

- [ ] Add more Supreme Court judgments to corpus
- [ ] Citation verification — check if cited cases actually exist
- [ ] Case comparison mode — compare two judgments side by side
- [ ] Upload your own moot court problem PDF
- [ ] Multi-turn conversation memory
- [ ] Export as formatted PDF brief

<br>

---

## 👤 Author

**[Amith ]**
[LinkedIn](www.linkedin.com/in/amith-gouda) ·
[GitHub](https://github.com/amithgoud) ·
[Email](mailto:amithgouda02@gmail.com)

*CS229 (Andrew Ng) · Building ML projects from scratch*

<br>

---

## 📄 License

MIT License — free to use, modify, and build on.

---

<div align="center">
  <sub>Built with ❤️ · RAG · Gemini · FAISS · Streamlit · Indian Law</sub>
</div>
