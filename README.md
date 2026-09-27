# Résumé Semantic Search

Search a résumé collection by meaning rather than keywords. Ask for *"someone who has built production machine learning pipelines"* and the engine surfaces the candidate whose résumé says *"deployed model training workflows"* — no shared words required.

Résumés are read (with OCR for scans), embedded, and stored in **ChromaDB** for similarity search, with file metadata and extracted text kept in **MySQL**.

Ships with a web console served by the API itself.

---

## Highlights

| | |
|---|---|
| **Meaning, not keywords** | Matches on what a résumé says, not the exact words it uses |
| **OCR fallback** | Scanned and photographed résumés are read and indexed like any other |
| **Two stores, one job** | ChromaDB for vectors, MySQL for metadata and text |
| **Scored results** | Every match comes back with a similarity score you can rank or threshold on |
| **Bulk upload** | A helper indexes a whole directory of PDFs in one pass |
| **Web console** | Search, upload and see the pipeline explained at `/` |

---

## The console

The API serves its own front end — start the server and open the root URL.

**Search** — describe who you want in your own words. Results come back ranked with a similarity score and a bar showing each one's strength relative to the best match. Example queries are one click away.

**Upload Résumés** — drop in one or several PDFs. Each shows how many characters were recovered, and the extracted text of the latest one renders alongside. Everything indexed in the session stays listed for review.

**How it works** — the ingestion path, the query path, and worked examples of the kind of match semantic search finds that a keyword search would miss.

---

## How it works

### Ingestion

```
PDF upload
   │
   ├─ 1. Read     PyMuPDF pulls the text layer out page by page
   ├─ 2. OCR      pages with no text layer go through PaddleOCR
   ├─ 3. Clean    whitespace and layout artefacts are normalised
   ├─ 4. Embed    sentence-transformers turns the text into a dense vector
   └─ 5. Store    the vector goes to ChromaDB, the metadata and text to MySQL
```

### Querying

```
Query sentence
   │
   ├─ 1. Embed    your sentence goes through the same embedding model
   ├─ 2. Compare  ChromaDB ranks every stored résumé by similarity
   ├─ 3. Join     the top matches are enriched from their MySQL records
   └─ 4. Return   filenames, paths and similarity scores in rank order
```

Because both sides use the same model, the query and the résumés live in the same vector space — which is what makes the comparison meaningful.

---

## Tech stack

**API** FastAPI · Uvicorn · Pydantic v2 · pydantic-settings
**Vector store** ChromaDB
**Metadata** MySQL via PyMySQL
**Embeddings** sentence-transformers
**Documents** PyMuPDF · PaddleOCR · Pillow · OpenCV
**Logging** Loguru
**Front end** Vanilla HTML, CSS and JavaScript — no build step

---

## Getting started

### Prerequisites

- Python 3.12 or newer
- MySQL 8

### 1. Install

```bash
git clone https://github.com/harshlaxkar07/resume-semantic-search-ocr-vector-db.git
cd resume-semantic-search-ocr-vector-db

# with uv (recommended)
uv sync

# or with pip
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Create the schema

```bash
mysql -u root -p < sql/schema.sql
```

### 3. Configure

Create a `.env` file in the project root:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=resume_vectors

UPLOAD_DIRECTORY=resumes
CHROMA_DIRECTORY=chroma
COLLECTION_NAME=resumes

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

LOG_LEVEL=INFO
LOG_DIRECTORY=logs
```

### 4. Run

```bash
uvicorn main:app --reload
```

| URL | What it is |
|---|---|
| `http://localhost:8000/` | The search console |
| `http://localhost:8000/docs` | Interactive OpenAPI documentation |
| `http://localhost:8000/health` | Health probe |

---

## API reference

### `POST /resume/upload`

Upload a PDF, extract its text, embed it and index it.

```bash
curl -X POST http://localhost:8000/resume/upload -F "file=@resume.pdf"
```

```json
{
  "message": "Resume uploaded and indexed successfully.",
  "resume": {
    "id": 12,
    "original_filename": "Neha_Patil_Resume.pdf",
    "stored_filename": "0012.pdf",
    "pdf_path": "/data/resumes/0012.pdf",
    "raw_text": "NEHA PATIL\nSenior Data Engineer, Pune\n...",
    "uploaded_at": "2026-09-27T01:14:00"
  }
}
```

### `POST /search`

Search the collection by meaning. `top_k` accepts 1 to 100 and defaults to 5.

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "someone who has built production machine learning pipelines", "top_k": 10}'
```

```json
{
  "results": [
    {
      "id": 7,
      "original_filename": "Priya_Nair_ML_Engineer.pdf",
      "pdf_path": "/data/resumes/0007.pdf",
      "similarity_score": 0.8841
    }
  ]
}
```

---

## Bulk indexing

`routers/resume.py` exposes a helper that walks a directory and indexes every PDF in it:

```python
from routers.resume import bulk_upload_resume

results = await bulk_upload_resume("path/to/resumes")
```

Each entry in the result reports the filename and whether it was indexed.

---

## Project structure

```
resume-semantic-search-ocr-vector-db/
├── main.py                        FastAPI application, CORS and the static mount
├── routers/
│   ├── resume.py                  Upload endpoint and the bulk helper
│   └── search.py                  Semantic search endpoint
├── services/
│   ├── upload_service.py          Ingestion orchestration
│   └── search_service.py          Query orchestration
├── extractor/
│   ├── dispatcher.py              Picks the right reader
│   ├── pdf_reader.py              Text-layer extraction
│   ├── pdf_ocr.py                 OCR for scanned pages
│   └── text_cleaner.py            Normalisation
├── embedding/
│   ├── model.py                   Loads the sentence-transformer
│   └── generator.py               Produces vectors
├── vectordb/
│   ├── chroma.py                  Client setup
│   ├── collection.py              Collection management
│   └── search.py                  Similarity queries
├── crud/resume.py                 MySQL reads and writes
├── schemas/                       Pydantic models
├── sql/schema.sql                 Table definition
└── frontend/                      The search console
```
