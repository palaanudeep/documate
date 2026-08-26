# DocuMate: Source-Grounded Q&A with Citations

PDF + website RAG system with citations, evals, and observability. Ask questions about documents or web pages and get answers grounded in retrieved sources.

**Product positioning:** DocuMate is the grounded research tool for asking questions about sources you provide (PDFs, web pages). It retrieves, cites, and answers. **SuperWise** (separate repo) is the personal agent that manages goals, calendar, and tasks. DocuMate doesn't do that.

![DocuMate Interface](DocuMate.png)

## What This Demonstrates

Applied RAG engineering for LLM engineer roles:

- **Citations from mixed sources**: Answers cite PDF page numbers or website URLs
- **Eval harness**: Test suite measuring retrieval hit rate and groundedness on PDF and URL fixtures
- **Observability**: JSON logs with request IDs, token counts, latency per request
- **Streaming responses**: Token-by-token generation
- **URL ingest**: Fetch and extract text from websites with timeouts, size limits, error handling
- **PDF ingest**: PyMuPDF extraction with page metadata
- **Production hygiene**: env-based secrets, Docker Compose, PostgreSQL

## Architecture

```
┌─────────────┐
│   React     │  Upload PDF or paste URL, ask questions
│  Frontend   │
└──────┬──────┘
       │ HTTP/REST
       ↓
┌──────────────────────────────────────────────┐
│          Flask Backend (JWT auth)            │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────┐     │
│  │   RAG Pipeline (LangChain)         │     │
│  ├────────────────────────────────────┤     │
│  │ PDF: PyMuPDF → page metadata       │     │
│  │ URL: requests + BeautifulSoup      │     │
│  │      → fetch with timeout/limits   │     │
│  │ Chunking: 1000/200 recursive       │     │
│  │ Embed: text-embedding-3-small      │     │
│  │ Store: Chroma vector DB            │     │
│  │ Retrieve: k=4 chunks               │     │
│  │ Generate: gpt-3.5-turbo + context  │     │
│  │ Citations: page# (PDF) or URL      │     │
│  └────────────────────────────────────┘     │
│                                              │
│  Logs: JSON (request_id, tokens, latency,   │
│         citations, source_type)             │
└──────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│  PostgreSQL  │  Users, chats, messages
└──────────────┘
```

## Stack

**RAG Core:**
- LangChain (orchestration, retrieval chains)
- OpenAI GPT-3.5-turbo (generation)
- OpenAI text-embedding-3-small (embeddings)
- Chroma (vector store)
- PyMuPDF (PDF parsing with page metadata)
- BeautifulSoup + html2text (web page extraction)
- requests (URL fetching with timeout/size limits)

**Backend:**
- Flask + Flask-JWT-Extended (auth)
- PostgreSQL + SQLAlchemy (persistence)
- Python 3.10+

**Frontend:**
- React 18 + Material-UI
- Axios (API client)

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ (or use Docker Compose)
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Quick Start (Docker Compose)

```bash
# 1. Clone the repo
git clone https://github.com/palaanudeep/documate.git
cd documate

# 2. Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key and secrets

# 3. Start all services
docker-compose up

# 4. Access the app
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

### Local Development Setup

```bash
# 1. Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp .flaskenv.example .flaskenv
# Edit .flaskenv with your credentials

# 3. Initialize database
flask db upgrade  # Run migrations

# 4. Start backend
flask run

# 5. In a new terminal, set up frontend
cd frontend
npm install
npm start

# 6. Visit http://localhost:3000
```

## Running Evals

The eval harness measures retrieval quality and groundedness on PDF and HTML fixtures.

```bash
# Generate PDF fixture and run evals
make eval

# Or manually:
cd evals
python3 create_fixture_pdf.py  # Creates fixtures/test_document.pdf
python3 run_evals.py            # Runs test questions on PDF and HTML fixtures

# Output: eval_results.json with metrics
```

### Eval Metrics

- **Retrieval hit rate**: % of queries where expected evidence appears in retrieved chunks
- **Groundedness**: % of answers containing content from retrieved context
- **Latency**: Average response time per query
- **Token usage**: Prompt/completion tokens per query

**Expected output format:**

```
EVALUATION SUMMARY
================================================================================
Total queries: 15 (8 PDF, 7 URL)
Retrieval hit rate: [run to measure]
Grounded answers: [run to measure]
Average latency: [run to measure]
Total tokens used: [run to measure]
```

Note: Numbers shown are placeholders. Run `make eval` locally to generate actual metrics. The harness does not run in CI (requires live OpenAI API calls).

## Key Features

### 1. Citations from Mixed Sources

Answers cite PDF pages or website URLs. Citations distinguish source type:

**PDF citation:**
```json
{
  "source_type": "pdf",
  "page": 0,
  "chunk_id": 3,
  "text": "TechVentures Inc. is a technology company founded in 2018...",
  "source": "document.pdf",
  "url": null,
  "title": null
}
```

**URL citation:**
```json
{
  "source_type": "url",
  "page": null,
  "chunk_id": 5,
  "text": "CloudTech Solutions is a cloud infrastructure company...",
  "source": "https://example.com/about",
  "url": "https://example.com/about",
  "title": "About Us"
}
```

**Full API response:**
```json
{
  "answer": "TechVentures was founded in 2018...",
  "citations": [
    { "source_type": "pdf", "page": 0, "chunk_id": 3, "text": "...", "source": "document.pdf" },
    { "source_type": "url", "url": "https://example.com/about", "chunk_id": 5, "text": "...", "title": "About Us" }
  ],
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "latency_ms": 1234,
  "token_usage": {
    "prompt_tokens": 850,
    "completion_tokens": 120,
    "total_tokens": 970
  }
}
```

### 2. Observability

Structured JSON logs for every request:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1704067200.0,
  "question": "What is the company revenue?",
  "answer": "TechVentures reported $45 million...",
  "citations": [...],
  "token_usage": {"prompt_tokens": 850, "completion_tokens": 120, "total_tokens": 970},
  "latency_ms": 1234,
  "retrieval_count": 4,
  "model": "gpt-3.5-turbo-0125"
}
```

**Optional LangSmith integration**: Set `LANGCHAIN_TRACING_V2=true` in `.env` for full trace visualization.

### 3. Streaming Responses

Use `/api/get_answer_stream` endpoint for token-by-token streaming:

```javascript
const response = await fetch('/api/get_answer_stream', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({ question, chat_history, chat_id })
});

const reader = response.body.getReader();
// Process NDJSON stream: citations → tokens → metrics
```

Format: NDJSON (newline-delimited JSON)
- First: `{"type": "citations", "data": [...], "request_id": "..."}`
- Chunks: `{"type": "token", "data": "word"}`
- Final: `{"type": "metrics", "data": {"latency_ms": ..., "token_usage": {...}}}`

### 4. Retrieval Configuration

Current settings (tuned for balance of recall and context window):

```python
chunk_size=1000          # Characters per chunk
chunk_overlap=200        # Overlap to preserve context across boundaries
k=4                      # Number of chunks retrieved per query
embedding_model="text-embedding-3-small"
separators=["\n\n", "\n", " ", ""]  # Prefer paragraph/sentence boundaries
```

Metadata preserved:
- **PDF sources**: `page` (0-indexed), `chunk_id`, `source` (filename), `start_index`
- **URL sources**: `url`, `title`, `chunk_id`, `source_type`

URL fetching constraints:
- Max page size: 10MB
- Timeout: 30 seconds
- Main content extraction (removes nav, footer, scripts)
- Robust error handling for non-200, blocked, or empty pages

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/load_doc` | POST | Upload PDF or submit URL, generate summary, create chat |
| `/api/get_answer` | POST | Ask question, get answer + citations |
| `/api/get_answer_stream` | POST | Stream answer with citations |
| `/auth/register` | POST | Create user account |
| `/auth/login` | POST | Get JWT token |

All main endpoints require JWT authentication (pass `Authorization: Bearer <token>` header).

**Load document/URL:**
```bash
# File upload
curl -X POST http://localhost:5000/api/load_doc \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"

# URL ingest
curl -X POST http://localhost:5000/api/load_doc \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

## Cost & Latency

Estimated for typical use (3-page PDF, ~1200 tokens):

- **Embedding cost**: ~$0.0001 per document (one-time, on upload)
- **Query cost**: ~$0.002 per Q&A (4 chunks × 250 tokens + generation)
- **Latency**: ~1-2s per query (embedding lookup + LLM generation)

Token usage is logged per request (word count × 1.3 estimate) for cost tracking. For exact counts, parse OpenAI API response usage fields.

## Limitations & Next Steps

**Current limitations:**
- Embeddings are ephemeral (Chroma in-memory; lost on restart)
- Token estimates are approximate (actual usage requires OpenAI API response parsing)
- No re-ranking or hybrid search
- Single-document context (no cross-document retrieval)
- No query intent classification or fallback strategies

**Logical next steps:**
- Persistent vector store (Chroma with SQLite/DuckDB backend, or Pinecone/Weaviate)
- Accurate token counting from OpenAI API responses
- Hybrid search (BM25 + vector) for keyword + semantic retrieval
- Re-ranking with cross-encoder (e.g., `rerank-english-v2.0`)
- Expanded eval set with adversarial questions (off-topic, ambiguous, multi-hop)
- Prompt optimization based on eval results
- Query expansion for better retrieval
- Confidence scoring and "I don't know" detection
- Multi-document/multi-session context management

## Development

```bash
# Run backend tests
cd backend
pytest

# Run evals
make eval

# Clean generated artifacts
make clean

# Lint backend
cd backend
flake8 app/

# Format code
black app/
```

## Project Structure

```
documate/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py              # User, Chat, Message models
│   │   ├── auth/
│   │   │   └── routes.py          # Login, register
│   │   └── main/
│   │       ├── routes.py          # Document upload, Q&A endpoints
│   │       ├── llm/
│   │       │   └── document_rag.py  # Core RAG logic, citations, logging
│   │       └── utils.py           # PDF parsing
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .flaskenv.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat.js            # Main chat interface
│   │   │   ├── login.js
│   │   │   └── register.js
│   │   └── App.js
│   ├── package.json
│   └── Dockerfile
├── evals/
│   ├── create_fixture_pdf.py      # Generate test PDF
│   ├── test_cases.py              # Eval questions + expected evidence
│   └── run_evals.py               # Eval harness (retrieval hit rate, groundedness)
├── docker-compose.yml
├── Makefile
├── .env.example
└── README.md
```

## Contributing

This is a portfolio project. For suggestions or questions, reach out via [LinkedIn](https://www.linkedin.com/in/anudeeppala/) or [email](mailto:anudeep.pala@gmail.com).

## License

MIT

## Contact

**Anudeep Pala**
- Email: [anudeep.pala@gmail.com](mailto:anudeep.pala@gmail.com)
- LinkedIn: [linkedin.com/in/anudeeppala](https://www.linkedin.com/in/anudeeppala/)
- GitHub: [@palaanudeep](https://github.com/palaanudeep)
