# Chatbot RAG Integration Guide

This guide walks you through setting up and using the Chatbot RAG (Retrieval-Augmented Generation) system integrated with the FastAPI application.

## Overview

The chatbot system enables document Q&A using:
- **LLM**: Llama 3.3 70B via Groq API
- **Vector DB**: Pinecone for document embeddings
- **Orchestration**: LangChain for RAG pipeline
- **File Support**: TXT, PDF, DOCX, DOC

## Architecture

```
1. Document Upload → DocumentProcessor
   ├─ Extract text (pdf, docx, doc, txt)
   ├─ Chunk text (1000 chars, 200 overlap)
   └─ Store in database

2. Document Processing → Pinecone
   ├─ Generate embeddings (HuggingFace all-MiniLM-L6-v2)
   ├─ Upsert vectors with metadata
   └─ Index by document_id and user_id

3. Question → RAG Pipeline
   ├─ Embed question
   ├─ Search Pinecone (filtered by document_id)
   ├─ Retrieve top 5 relevant chunks
   └─ Pass to Groq LLM with context

4. Response ← Groq LLM
   └─ Generate answer based on context
```

## Setup Instructions

### 1. Get Groq API Key

- Visit [Groq Console](https://console.groq.com)
- Sign up for free account
- Create API key
- Copy to `.env` as `GROQ_API_KEY`

### 2. Set Up Pinecone

- Visit [Pinecone](https://www.pinecone.io)
- Create free account
- Create a Serverless index:
  - **Name**: `chatbot-docs` (or customize in .env)
  - **Dimension**: 384 (matches all-MiniLM-L6-v2)
  - **Metric**: Cosine
  - **Cloud**: AWS (or your preference)
  - **Region**: us-east-1 (or your preference)
- Copy API Key to `.env` as `PINECONE_API_KEY`
- Update `.env` with `PINECONE_ENVIRONMENT` if you chose different region

### 3. Update .env

```bash
# Add to your .env file:
GROQ_API_KEY=your-groq-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=chatbot-docs
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Key new packages:
- `langchain>=0.1.0` - RAG orchestration
- `langchain-groq>=0.1.0` - Groq integration
- `pinecone-client>=3.0.0` - Vector DB
- `pypdf>=4.0.0` - PDF extraction
- `python-docx>=0.8.11` - DOCX extraction

### 5. Apply Database Migration

```bash
alembic upgrade head
```

This creates the `documents` table to track uploaded files.

## API Endpoints

### Upload Document
**POST** `/chatbot/upload`

Upload a document file (txt, pdf, docx, doc).

**Authentication**: Bearer token required

**Request**:
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@document.pdf" \
  http://localhost:8000/chatbot/upload
```

**Response** (201):
```json
{
  "message": "Document 'document.pdf' uploaded and processed (15 chunks)",
  "document": {
    "id": 1,
    "user_id": 1,
    "file_name": "document.pdf",
    "file_type": ".pdf",
    "chunk_count": 15,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### List User Documents
**GET** `/chatbot/documents`

List all documents uploaded by current user.

**Authentication**: Bearer token required

**Response** (200):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "file_name": "document.pdf",
    "file_type": ".pdf",
    "chunk_count": 15,
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### Ask Question
**POST** `/chatbot/ask/{document_id}`

Ask a question about a specific document.

**Authentication**: Bearer token required

**Request**:
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of this document?"}' \
  http://localhost:8000/chatbot/ask/1
```

**Response** (200):
```json
{
  "answer": "The main topic of this document is...",
  "sources": [
    {
      "chunk_index": 2,
      "relevance_score": 0.92
    },
    {
      "chunk_index": 5,
      "relevance_score": 0.88
    }
  ]
}
```

### Delete Document
**DELETE** `/chatbot/documents/{document_id}`

Delete a document and remove its embeddings from Pinecone.

**Authentication**: Bearer token required

**Response** (200):
```json
{
  "message": "Document 'document.pdf' deleted successfully"
}
```

## Usage Example

### 1. Register and Login

```bash
# Register
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepass123"
  }'

# Verify OTP (check email)
curl -X POST http://localhost:8000/users/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "123456"
  }'

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'

# Copy the access_token
```

### 2. Upload Document

```bash
curl -X POST \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -F "file=@research_paper.pdf" \
  http://localhost:8000/chatbot/upload
```

### 3. Ask Questions

```bash
curl -X POST \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key findings?"}' \
  http://localhost:8000/chatbot/ask/1
```

## File Size & Type Constraints

| Constraint | Value |
|-----------|-------|
| Max file size | 50MB |
| Chunk size | 1000 characters |
| Chunk overlap | 200 characters |
| Allowed types | .txt, .pdf, .docx, .doc |
| Embedding model | all-MiniLM-L6-v2 (384 dim) |

## How It Works

### Document Processing
1. **Extract**: Text is extracted from the uploaded file
2. **Chunk**: Text is split into 1000-char chunks with 200-char overlap (preserves context)
3. **Embed**: Each chunk is embedded using HuggingFace's all-MiniLM-L6-v2 (384 dimensions)
4. **Store**: Embeddings + metadata stored in Pinecone, document metadata in PostgreSQL

### Question Answering
1. **Embed Query**: User question is embedded with same model
2. **Retrieve**: Pinecone returns top 5 similar chunks (filtered by document_id)
3. **Prompt**: Chunks + question sent to Groq LLM (Llama 3.3 70B)
4. **Generate**: LLM generates answer with temperature=0.3 (more deterministic)

## Security

- **Authentication**: All endpoints require JWT token
- **Authorization**: Users can only access their own documents
- **File Validation**: File type and size validated before processing
- **Data Isolation**: Pinecone vectors filtered by document_id and user_id

## Troubleshooting

### "PINECONE_API_KEY not configured"
- Ensure `.env` file has `PINECONE_API_KEY`
- Restart the application after updating `.env`

### "GROQ_API_KEY not configured"
- Ensure `.env` file has `GROQ_API_KEY`
- Restart the application after updating `.env`

### PDF Text Extraction Issues
- Some PDFs with images/scans may extract poorly
- Try converting to text-based PDF first
- Check extracted text with the returned chunk_count

### Slow Question Answering
- Check Groq API rate limits (free tier: ~30 req/min)
- Ensure Pinecone index is not too large
- Consider caching frequent questions

### Document Not Found
- Verify document_id is correct
- Check that you own the document (created with your account)
- Documents are user-isolated

## Performance Notes

- **Embedding Generation**: ~100-200ms per chunk (HuggingFace local)
- **Pinecone Search**: ~200-500ms for retrieval
- **Groq LLM**: ~1-3 seconds for generation (depends on answer length)
- **Total Q&A Latency**: ~2-5 seconds typical

## Future Enhancements

- [ ] Async document processing (background tasks)
- [ ] Batch upload multiple documents
- [ ] Document summarization endpoint
- [ ] Custom system prompts per document
- [ ] Conversation history/context
- [ ] Document sharing between users
- [ ] Reranking retrieved chunks (cross-encoder)
- [ ] Streaming responses for long answers
