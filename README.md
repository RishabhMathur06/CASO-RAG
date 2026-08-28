<div align="center">
  <h1>GraphRAG-X 🧠</h1>
  <p><b>Beyond Dumb Retrieval — A Self-Organizing, Context-Aware Hybrid Graph-Vector Retrieval Engine</b></p>

  <a href="https://github.com/RishabhMathur06/CASO-RAG/stargazers"><img src="https://img.shields.io/github/stars/RishabhMathur06/CASO-RAG" alt="Stars Badge"/></a>
  <a href="https://github.com/RishabhMathur06/CASO-RAG/network/members"><img src="https://img.shields.io/github/forks/RishabhMathur06/CASO-RAG" alt="Forks Badge"/></a>
  <a href="https://github.com/RishabhMathur06/CASO-RAG/pulls"><img src="https://img.shields.io/github/issues-pr/RishabhMathur06/CASO-RAG" alt="Pull Requests Badge"/></a>
  <a href="https://github.com/RishabhMathur06/CASO-RAG/issues"><img src="https://img.shields.io/github/issues/RishabhMathur06/CASO-RAG" alt="Issues Badge"/></a>
  <a href="https://github.com/RishabhMathur06/CASO-RAG/blob/main/LICENSE"><img src="https://img.shields.io/github/license/RishabhMathur06/CASO-RAG?color=2b9348" alt="License Badge"/></a>
</div>

<br>

GraphRAG-X is a production-grade, fully open-source Retrieval-Augmented Generation (RAG) system that fundamentally solves the "dumb search" problem plaguing standard Vector Database implementations. 

Instead of treating inserted documents as isolated embedding blobs, GraphRAG-X builds a **living Knowledge Graph** on top of vector storage during ingestion. At query time, it uses a multi-stage, custom-built retrieval pipeline that combines semantic search, sparse keyword search, graph traversal, and cross-encoder reranking to return highly relevant, contextually coherent, and citation-verified answers.

Designed for privacy and full control, GraphRAG-X runs **entirely locally with zero paid API dependencies**, using open-source LLMs loaded from HuggingFace, self-hosted databases, and custom algorithms.

---

## 🌟 Key Differentiators

| Feature | Standard RAG | **GraphRAG-X** |
| :--- | :--- | :--- |
| **Retrieval Method** | Dense vector ANN only | Dense + Sparse (BM25) + Graph Traversal + Reranking |
| **Document Organization** | None (flat blob storage) | Auto-organized Knowledge Graph |
| **Context Awareness** | Chunk-level only | Multi-hop graph-aware context |
| **Hallucination Control** | None | Faithfulness Auditor + Citation Enforcement |
| **PII Handling** | None | Microsoft Presidio scrubbing at ingestion |
| **Toxicity Filtering** | None | Detoxify on query + response |
| **Observability** | None | LangFuse traces + MLflow + Grafana dashboards |
| **Safety** | None | Guardrails AI + Prompt Injection Detector |
| **Deployment** | Script/Notebook | Fully Dockerized production stack |

---

## 🏗️ Architecture

GraphRAG-X employs a modular, microservices-based architecture orchestrated via Docker:

- **Frontend**: React 19, TypeScript, TailwindCSS 4, Zustand, Vite.
- **Backend**: FastAPI (Python 3.11+), AsyncIO, Pydantic v2.
- **Databases**:
  - **Qdrant**: Vector storage (Dense + Sparse HNSW indexing).
  - **Neo4j**: Graph database for entity nodes and relationship edges.
  - **PostgreSQL**: Relational metadata, audit logs, and document registry.
  - **Redis**: Caching, rate limiting, and session state.
- **LLM/ML Layer**: Open-source models (Llama-3.1-8B, Phi-3.5) running via HuggingFace and `llama-cpp-python` for CPU/GPU inference.
- **Responsible AI**: Guardrails AI, Presidio (PII), Detoxify.
- **LLMOps**: MLflow, LangFuse, Prometheus, Grafana.

---

## 🚀 Quick Start (Docker)

The easiest way to get GraphRAG-X running is via our Docker Compose setup, which automatically provisions the backend, frontend, databases, and MLflow/LangFuse observability stack.

### Prerequisites
- Docker & Docker Compose plugin
- Git
- At least 16GB RAM (32GB recommended if running larger LLMs entirely on CPU)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RishabhMathur06/CASO-RAG.git
   cd CASO-RAG
   ```

2. **Configure Environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your specific tokens if needed (e.g., HF_TOKEN for HuggingFace)
   ```

3. **Start the infrastructure:**
   ```bash
   docker compose up -d
   ```

4. **Access the services:**
   - **Web UI:** `http://localhost:3000` (or port 80 via Nginx)
   - **API Docs (Swagger):** `http://localhost:8000/docs`
   - **Neo4j Browser:** `http://localhost:7474`
   - **Grafana Dashboards:** `http://localhost:3001`
   - **LangFuse:** `http://localhost:3000` (depending on your port mapping)

---

## 🛠️ Usage Pipeline

### 1. Smart Ingestion
Upload documents (PDF, MD, TXT). GraphRAG-X will:
1. Scrub PII using Microsoft Presidio.
2. Filter out toxic content.
3. Semantically chunk the document.
4. Extract Subject-Predicate-Object entities using LLMs.
5. Embed chunks (Dense + Sparse vectors).
6. Build a dynamic Neo4j Graph linking chunks and entities.

### 2. Multi-Stage Retrieval & Querying
When a user submits a query:
1. **Security Check**: Prompt injection and toxicity checks.
2. **Recall (Stage 1)**: Hybrid search (Dense Qdrant + Sparse BM25) fused via Reciprocal Rank Fusion (RRF).
3. **Context Enrichment (Stage 2)**: Traverses Neo4j to pull multi-hop entity relationships and sequential context.
4. **Precision (Stage 3)**: Cross-encoder reranking to ensure top relevance.
5. **Generation**: LLM constructs the answer with inline citations.
6. **Audit**: Faithfulness auditor ensures the answer doesn't hallucinate beyond the retrieved context.

---

## 📂 Project Structure

```text
graphrag-x/
├── backend/            # FastAPI, Core Intelligence Layer, Retrieval, LLMOps
├── frontend/           # React 19 UI, Interactive Graph Visualizer, Dashboards
├── infrastructure/     # Nginx, Prometheus, Grafana configs
├── data/               # Models, benchmarks, and sample documents
├── notebooks/          # Jupyter notebooks for algorithm exploration
├── docker-compose.yml  # Production docker stack
└── docs/               # Detailed documentation and context
```

---

## 🤝 Contributing

We welcome contributions from the community! If you're interested in making RAG smarter, more observable, and entirely local, please check out our [Contributing Guidelines](CONTRIBUTING.md) (coming soon).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <b>Built with ❤️ by the open-source AI community.</b>
</div>
