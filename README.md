# ⚖️ LexAI — Indian Legal Research Assistant

A Retrieval-Augmented Generation (RAG) chatbot that answers Indian law research questions with citations, built for moot court preparation and legal research.

**[🔗 Live Demo](#)** &nbsp;|&nbsp; **[📂 GitHub Repo](#)**

> Replace the links above with your actual Streamlit Cloud URL and GitHub repo link before publishing.

---

## 📌 Overview

Most RAG demos are built on generic PDFs (résumés, Wikipedia dumps, etc.). LexAI applies the same technique to a real, high-value domain: Indian legal research. Ask a constitutional law question — like *"What are the arguments for right to privacy under Article 21?"* — and LexAI retrieves relevant passages from a curated corpus of the Indian Constitution and landmark Supreme Court judgments, then generates a structured, cited answer.

It's built for law students, moot court participants, and anyone who needs quick, source-grounded answers instead of a generic chatbot response that might hallucinate case law.

## ✨ Features

- **Retrieval-Augmented Generation** — answers are grounded in real legal documents, not just the LLM's parametric memory
- **Petitioner / Respondent / Both Sides argument modes** — generates arguments from either side of a case, useful for moot court prep
- **Source transparency** — every answer shows which document chunks it pulled from, with a relevance score
- **Web-augmented fallback** — if local documents don't have strong matches, it automatically searches the web and flags the answer as web-augmented so users know the source
- **Downloadable research output** — export any Q&A session as a `.txt` file
- **Adjustable retrieval depth** — slider to control how many document chunks are retrieved per query

## 🏗️ How It Works

```
User Question
     │
     ▼
Embed question (sentence-transformers)
     │
     ▼
Search FAISS vector index  ──► Top-k relevant chunks
     │
     ▼
Chunks below relevance threshold? ──► Yes ──► Web search fallback
     │ No
     ▼
Question + retrieved chunks + mode  ──► Gemini API
     │
     ▼
Structured answer with citations + source panel
```

**Ingestion pipeline (`ingest.py`):** legal PDFs (Indian Constitution, *K.S. Puttaswamy v. Union of India*, *Maneka Gandhi v. Union of India*, etc.) are split into ~200-word chunks with 50-word overlap, embedded locally with `sentence-transformers`, and stored in a FAISS index for fast similarity search.

**Retrieval + generation pipeline (`rag.py`):** on each query, the top-k most relevant chunks are retrieved, and — along with the selected argument mode — passed to Google's Gemini API to generate a grounded, structured legal answer.

**UI (`app.py`):** a Streamlit interface with a sidebar for settings (argument mode, retrieval depth, loaded documents) and a main panel for the question, answer, and source breakdown.

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| LLM | Google Gemini API (free tier) |
| Embeddings | `sentence-transformers` (local, no API cost) |
| Vector store | FAISS (`faiss-cpu`) |
| PDF parsing | `pypdf` / `PyPDF2` |
| Frontend | Streamlit |
| Config | `python-dotenv` |
| Deployment | Streamlit Community Cloud |

## 📂 Project Structure

```
legal-rag-chatbot/
├── documents/          # Source legal PDFs
├── vector_store/        # FAISS index + chunk metadata
├── ingest.py             # Reads PDFs → chunks → embeds → builds FAISS index
├── rag.py                # Retrieval + Gemini generation pipeline
├── app.py                 # Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Running It Locally

```bash
git clone https://github.com/<your-username>/legal-rag-chatbot.git
cd legal-rag-chatbot
pip install -r requirements.txt

# Add your Gemini API key
cp .env.example .env
# then edit .env and add: GEMINI_API_KEY=your_key_here

# Build the vector index (only needed once, or after adding new documents)
python ingest.py

# Launch the app
streamlit run app.py
```

## 📚 Document Corpus

- Constitution of India (legislative.gov.in)
- *K.S. Puttaswamy v. Union of India* (2017) — right to privacy
- *Maneka Gandhi v. Union of India* (1978) — Article 21, personal liberty
- Sourced from [indiankanoon.org](https://indiankanoon.org)

## 🧠 What I Learned

- Designing a retrieval pipeline that balances chunk size, overlap, and relevance thresholds to avoid feeding irrelevant context to the LLM
- Building a **fallback strategy** — detecting when local retrieval is weak and gracefully degrading to web search instead of forcing a bad answer
- Prompt design for domain-specific, structured legal output (as opposed to free-form chat answers)
- Deploying a full ML-adjacent application end-to-end: ingestion → vector search → LLM generation → UI → cloud deployment

## 🔮 Future Improvements

- Proper legal citation formatting (Bluebook / Indian citation style)
- Precedent relevance scoring surfaced directly in the UI
- Expand corpus with more landmark judgments (*Kesavananda Bharati*, *Vishaka*, etc.)
- Section/Article finder for direct lookup without a full question

---

**Built by Amith Goud** — [GitHub](https://github.com/amithgoud) · [LinkedIn](https://www.linkedin.com/in/amith-gouda)
