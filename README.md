# DocuMate: Production-Grade RAG System for Document Q&A

A document question-answering system demonstrating applied RAG (Retrieval-Augmented Generation) engineering with citations, evals, observability, and cost tracking.

![DocuMate Interface](DocuMate.png)

## What This Demonstrates

This project showcases practical RAG engineering for LLM engineer roles:

- **Grounded responses with citations**: Every answer includes source page numbers and chunk references
- **Eval harness**: Runnable test suite measuring retrieval hit rate and groundedness
- **Observability**: Structured JSON logs with request IDs, token counts, and latency per request
- **Streaming responses**: Non-blocking answer generation via Server-Sent Events
- **Retrieval quality**: Metadata-enriched chunking with configurable overlap and k-value tuning
- **Production hygiene**: Environment-based secrets, Docker Compose setup, PostgreSQL persistence

## Architecture

```
┌─────────────┐
│   React     │  User uploads PDF, asks questions
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
│  │ 1. PDF → PyMuPDF (page metadata)   │     │
│  │ 2. Recursive chunking (1000/200)   │     │
│  │ 3. Chroma + text-embedding-3-small │     │
│  │ 4. Retrieve k=4 chunks             │     │
│  │ 5. LLM (gpt-3.5-turbo) + context   │     │
│  │ 6. Citations from metadata         │     │
│  └────────────────────────────────────┘     │
│                                              │
│  Logs: JSON traces (request_id, tokens,     │
│         latency, retrieval_count, model)    │
└──────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│  PostgreSQL  │  Chats, messages, users
└──────────────┘
```

## Stack

**RAG Core:**
- LangChain (orchestration, retrieval chains)
- OpenAI GPT-3.5-turbo (generation)
- OpenAI text-embedding-3-small (embeddings)
- Chroma (vector store)
- PyMuPDF (PDF parsing with page metadata)

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

The eval harness measures retrieval quality and groundedness on a fixture PDF with known Q&A pairs.

```bash
# Generate test fixture and run evals
make eval

# Or manually:
cd evals
python3 create_fixture_pdf.py  # Creates fixtures/test_document.pdf
python3 run_evals.py            # Runs test questions

# Output: eval_results.json with metrics
```

### Eval Metrics

- **Retrieval hit rate**: % of queries where expected evidence appears in retrieved chunks
- **Groundedness**: % of answers containing content from retrieved context (basic faithfulness check)
- **Latency**: Average response time per query
- **Token usage**: Prompt/completion tokens per query

**Example output:**

```
EVALUATION SUMMARY
================================================================================
Total queries: 10
Retrieval hit rate: 9/10 (90.0%)
Grounded answers: 10/10 (100.0%)
Average latency: 1450ms
Total tokens used: 12500
Avg tokens per query: 1250
```

The eval harness does not run in CI (requires live OpenAI API calls). Run locally with `make eval` before demoing changes.

## Key Features

### 1. Citations

Every answer includes:
- Source page numbers
- Chunk IDs for traceability  
- First 200 chars of each retrieved chunk
- Returned in API response alongside answer

**API response format:**
```json
{
  "answer": "TechVentures was founded in 2018...",
  "citations": [
    {
      "page": 0,
      "chunk_id": 3,
      "text": "TechVentures Inc. is a technology company founded in 2018...",
      "source": "document.pdf"
    }
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
- `page`: Page number (0-indexed)
- `chunk_id`: Unique chunk identifier
- `source`: Original filename
- `start_index`: Character offset in source page

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/load_doc` | POST | Upload PDF, generate summary, create chat session |
| `/api/get_answer` | POST | Ask question, get answer + citations |
| `/api/get_answer_stream` | POST | Stream answer with citations |
| `/auth/register` | POST | Create user account |
| `/auth/login` | POST | Get JWT token |

All main endpoints require JWT authentication (pass `Authorization: Bearer <token>` header).

## Cost & Latency

Measured on fixture PDF (3 pages, ~1200 tokens):

- **Embedding cost**: ~$0.0001 per document (one-time, on upload)
- **Query cost**: ~$0.002 per Q&A (4 chunks × 250 tokens + generation)
- **Latency**: ~1.2-1.8s per query (includes embedding lookup + LLM generation)

Token usage is logged per request for cost tracking.

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
