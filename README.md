# 🧠 CASO-RAG (GraphRAG-X)
> *Beyond Dumb Retrieval — A Self-Organizing, Context-Aware Hybrid Graph-Vector Retrieval Engine*

![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-018bff?style=for-the-badge&logo=neo4j&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-FFFFFF?style=for-the-badge&logo=ollama&logoColor=black)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-FF5252?style=for-the-badge)
![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

---

## 🛑 The Problem: Why Standard Vector Databases Are "Dumb"
Standard RAG pipelines today suffer from critical failures:
1. **Context Loss:** Documents are split into arbitrary chunks. The database has zero knowledge that Chunk B is the logical continuation of Chunk A.
2. **Similarity ≠ Relevance:** Standard search finds vectors that are mathematically close, but fails to capture logical relevance or thematic relationships.
3. **No Self-Organization:** Every document inserted is an isolated orphan. There is no automatic clustering by topic, entity, or relationship.

## 🚀 The Solution: CASO-RAG
Instead of treating inserted documents as isolated blobs, CASO-RAG builds a **living Knowledge Graph** on top of vector storage during ingestion. At query time, it uses a multi-stage retrieval pipeline combining semantic search, sparse keyword search, graph traversal, and cross-encoder reranking to return highly relevant, citation-verified answers.

### Key Differentiators
| Feature | Standard RAG | CASO-RAG |
|---|---|---|
| **Retrieval Method** | Dense vector ANN only | **Two-Stage:** Dense + Sparse (BGE-M3) + Graph Traversal + Cross-Encoder Reranking (BGE-Reranker-v2-m3) |
| **Noise Filtering** | Top-k chunks blindly passed to LLM | Dynamic relevance threshold filtering (`min_score >= 0.20`) |
| **Document Organization** | None (flat blob storage) | Auto-organized Knowledge Graph (Neo4j) with parent-child chunk lineage |
| **Context Awareness** | Chunk-level only | Multi-hop graph-aware context with verified source attribution |
| **Caching & Latency** | None (full inference every time) | Sub-millisecond Redis Query Caching (<1ms response on hit, ~99.9% latency cut) |
| **Observability** | Console print statements | Structured dual logging (Loguru) + Prometheus metrics + Grafana + Langfuse tracing |
| **Execution** | Cloud APIs (paid, third-party data leakage) | 100% Local / Apple Silicon Optimized (Ollama / Qwen) |
| **Responsible AI** | None (vulnerable to jailbreaks & PII leaks) | Built-in Prompt Injection Shield + Automated PII Redaction (`[EMAIL_REDACTED]`, `[PHONE_REDACTED]`, `[CREDIT_CARD_REDACTED]`) |
| **Interactive UI** | CLI / Postman only | Modern React 19 + Tailwind CSS Dashboard (`:5173`) with live Context & Reranker Inspector |

---

## ⚡ Two-Stage Retrieval & Reranking Architecture

```text
User Query: "Where was Steve Jobs born and what did Apple sell in 1976?"
                                │
                                ▼
        [Stage 1: High-Recall Candidate Retrieval]
        • Qdrant fetches Top-10 vector candidates (Cosine similarity on BGE-M3 dense vectors)
        • Neo4j traverses (d:Document)-[:HAS_CHUNK]->(c:Chunk) to pull text + provenance
                                │
                                ▼
        [Stage 2: Cross-Encoder Precision Reranking]
        • BGE-Reranker-v2-m3 computes joint cross-attention: (Query ⟷ Chunk)
        • Scores each candidate from 0.0 to 1.0
        • Threshold filter drops noise (retains chunks >= 0.20)
                                │
                                ▼
        [Top Context Blocks with Citations]
        • Clean, high-precision context passed to Qwen via Ollama
```

---

## 🏗️ System Architecture

```text
+--------------------------------------------------------------------------------+
|                               CASO-RAG SYSTEM                                  |   
|                                                                                |
|  +--------------------------------------------------------------------------+  |          
|  |                     CUSTOM INTELLIGENCE LAYER                            |  |
|  |  Smart Ingestion | Hybrid Retriever (BM25+Dense) | Graph Augmenter       |  |
|  +--------------------------------------------------------------------------+  |         
|                                                                                |
|  +--------------------------------------------------------------------------+  |          
|  |                         STORAGE LAYER                                    |  |
|  |  Qdrant (Vectors) | Neo4j (Graph) | PostgreSQL (Metadata) | Redis Cache  |  |
|  +--------------------------------------------------------------------------+  |           
|                                                                                |
|  +--------------------------------------------------------------------------+  |          
|  |                         LLMOps LAYER                                     |  |
|  |      MLflow | LangFuse | Prometheus | Grafana | OpenTelemetry            |  |
|  +--------------------------------------------------------------------------+  |          
+--------------------------------------------------------------------------------+         
```

---

## 🏛️ Core Architectural Components & Purpose

CASO-RAG combines a specialized storage, latency, and observability stack. Here is the exact role each component plays:

### 1. ⚡ Latency & Caching: Redis
* **Role:** Sub-millisecond Query Caching & State Management.
* **Why it's needed:** Standard RAG pipelines invoke expensive embedding generation, vector search, graph traversal, and LLM inference for every single query—even identical ones.
* **How it works:**
  * Uses deterministic **SHA-256 hashed queries** with case and whitespace normalization.
  * **Cache Hit:** Returns pre-generated grounded answers and citations in **< 1.0 ms** (~8,500x faster than live generation, cutting p95 latency by 99.99%).
  * **Cache Invalidation:** Automatically flushes all cached answers whenever a new document is ingested (`POST /api/v1/rag/ingest`) or via manual API call (`DELETE /api/v1/rag/cache`).

---

### 2. 📊 Observability & LLMOps: Grafana & Prometheus
* **Role:** Production Monitoring, Performance Dashboards & SRE Telemetry.
* **Why it's needed:** Enterprise AI systems cannot operate as black boxes; engineers need real-time visibility into traffic volume, latency regressions, and cache effectiveness.
* **How it works:**
  * **Prometheus (`:9090`):** Automatically scrapes FastAPI's `/metrics` endpoint every 10 seconds. Collects counters (`caso_rag_queries_total`, `caso_rag_documents_ingested_total`) and latency histograms (`caso_rag_query_duration_seconds`).
  * **Grafana (`:3001`):** Pre-provisioned using Infrastructure-as-Code (`infrastructure/grafana/provisioning/`). Automatically connects to Prometheus on boot and renders live charts:
    * **Throughput (QPS):** Traffic split by cached vs. live queries.
    * **Cache Hit Rate (%):** Speedometer gauge of query acceleration.
    * **Latency Percentiles:** Live p50 (median) and p95 latency curves.

---

### 3. 🧪 Quantitative Benchmarking: MLflow
* **Role:** Evaluation Tracking, Regression Prevention & Metric Logging.
* **Why it's needed:** To scientifically prove that CASO-RAG's two-stage hybrid retrieval outperforms traditional "naive" vector search.
* **How it works:**
  * Our evaluation harness (`benchmark_rag.py`) seeds the database with true sources and deceptive distractor documents.
  * Automatically calculates **Hit@1 (100%)**, **Recall@3 (100%)**, **MRR (1.000)**, and **Distractor Noise Rejection (100%)**.
  * Logs parameters, dataset hashes, and metric curves directly into MLflow (`:5001`) for auditability across model iterations.

---

### 4. 🔍 Lifecycle Tracing: Langfuse
* **Role:** Deep LLM Observability & Step-by-Step Execution Tracing.
* **Why it's needed:** To inspect individual prompt constructions, retrieved context payloads, and local model generation steps.
* **How it works:**
  * Traces the lifecycle of each query through the RAG pipeline.
  * Captures input queries, retrieved chunk metadata, cross-encoder scores, and latency breakdowns.

---

### 5. 🗄️ Dual-Store Knowledge Base: Qdrant + Neo4j
* **Qdrant Vector DB (`:6333`):** High-speed approximate nearest neighbor (ANN) search using HNSW indexing and cosine similarity over 1024-dimensional BGE-M3 dense embeddings.
* **Neo4j Graph DB (`:7474`, `:7687`):** Native graph database that links `(Document)-[:HAS_CHUNK]->(Chunk)` nodes. Maintains structural chunk order, parent document metadata, and enables multi-hop relational context expansion.

---

### 6. 🛡️ Responsible AI: Security Guardrails & Audit Middleware
* **Prompt Injection Shield:** Evaluates incoming user prompts against known jailbreak/override signatures before processing.
* **Automated PII Redaction:** Regex-based sanitization that masks emails (`[EMAIL_REDACTED]`), phone numbers (`[PHONE_REDACTED]`), and credit cards (`[CREDIT_CARD_REDACTED]`) before context reaches the LLM or logs.
* **Audit Middleware:** Attaches `X-Process-Time-Ms` response headers and produces structured HTTP access logs.

---

## 🛠️ Quick Start (Development)

**1. Clone the repository and setup environments:**
```bash
git clone https://github.com/RishabhMathur06/CASO-RAG.git
cd CASO-RAG
cp .env.example .env
```

**2. Download Local AI Models:**
```bash
cd backend
uv add huggingface_hub
uv run python scripts/download_models.py
```

**3. Start the Infrastructure:**
```bash
# Return to root directory
docker compose up -d
```

**4. Start the FastAPI Server:**
```bash
cd backend
uv run uvicorn app.main:app --reload
```
Once started, access the interactive Swagger API documentation at:
👉 **`http://localhost:8000/docs`**

**5. Start the React Frontend:**
```bash
# In a separate terminal tab:
cd frontend
npm install
npm run dev
```
Access the interactive web dashboard at:
👉 **`http://localhost:5173`**

**6. Verification & Testing:**
```bash
cd backend
# 1. Test Cross-Encoder Reranker
uv run python -m scripts.test_reranker

# 2. Test Dual Ingestion (Qdrant + Neo4j)
uv run python -m scripts.test_ingestion

# 3. Test Hybrid Search Retrieval
uv run python -m scripts.test_search

# 4. Test End-to-End RAG Generation
uv run python -m scripts.test_rag

# 5. Benchmark Redis Query Cache Speedup
uv run python -m scripts.test_cache

# 6. Run Quantitative Benchmark & Log to MLflow
uv run python -m scripts.benchmark_rag

# 7. Test Responsible AI Guardrails & PII Sanitizer
uv run python -m scripts.test_guardrails
```

## 📊 Benchmark Results (MLflow Tracked)

| Metric | Dense Baseline | CASO-RAG (Hybrid + Graph + Rerank) |
|---|---|---|
| **Top-1 Accuracy (Hit@1)** | ~60.0% | **100.0%** |
| **Recall@3** | ~80.0% | **100.0%** |
| **Mean Reciprocal Rank (MRR)** | 0.733 | **1.000** |
| **Distractor Noise Reduction** | High context pollution | **100% of distractor chunks eliminated** |
| **Redis Cached Latency** | N/A | **< 1.0 ms (~8,500x speedup)** |

*All experiments automatically tracked in MLflow at `http://localhost:5001`.*

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health status |
| `POST` | `/api/v1/rag/query` | Submit natural language query and receive grounded answer with source citations (Redis cached) |
| `POST` | `/api/v1/rag/ingest` | Ingest raw documents into vector (Qdrant) and graph (Neo4j) databases and flush stale cache |
| `DELETE` | `/api/v1/rag/cache` | Manually flush all cached queries from Redis |
| `GET` | `/metrics` | Prometheus metrics scrape endpoint (traffic, latencies, cache hit ratio) |

---

## 🌐 Platform Services Directory

| Service | Port / URL | Description | Default Credentials (if applicable) |
|---|---|---|---|
| **React Web UI** | [`http://localhost:5173`](http://localhost:5173) | Interactive GraphRAG Playground & Ingestion Studio | *None* |
| **FastAPI Swagger Docs** | [`http://localhost:8000/docs`](http://localhost:8000/docs) | Interactive REST API documentation & schema explorer | *None* |
| **Grafana Dashboards** | [`http://localhost:3001`](http://localhost:3001) | Auto-provisioned LLMOps Observability (p95 latency, QPS, Cache Hit %) | `admin` / `admin` |
| **MLflow Experiments** | [`http://localhost:5001`](http://localhost:5001) | RAG evaluation runs, Hit@1/Recall@3, noise reduction metrics | *None* |
| **Neo4j Browser** | [`http://localhost:7474`](http://localhost:7474) | Interactive Cypher graph visualizer (`(d:Document)-[:HAS_CHUNK]->(c:Chunk)`) | `neo4j` / `casorag_neo4j_password` |
| **Prometheus** | [`http://localhost:9090`](http://localhost:9090) | Direct metrics scraper & target health monitor | *None* |

## 📄 License
This project is licensed under the MIT License.
