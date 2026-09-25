# 🧠 CASO-RAG (GraphRAG-X)
> *Beyond Dumb Retrieval — A Self-Organizing, Context-Aware Hybrid Graph-Vector Retrieval Engine*

![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-018bff?style=for-the-badge&logo=neo4j&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-FFFFFF?style=for-the-badge&logo=ollama&logoColor=black)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-FF5252?style=for-the-badge)

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
| **Retrieval Method** | Dense vector ANN only | Dense + Sparse (BM25) + Graph Traversal + Reranking |
| **Document Organization** | None (flat blob storage) | Auto-organized Knowledge Graph (Neo4j) |
| **Context Awareness** | Chunk-level only | Multi-hop graph-aware context |
| **Execution** | Cloud APIs | 100% Local / Apple Silicon Optimized (Ollama) |

---

## 🏗️ System Architecture

```text
+-----------------------------------------------------------------------------+
|                          CASO-RAG SYSTEM                                    |
|                                                                             |
|  +--------------------------------------------------------------------------+  |
|  |                   CUSTOM INTELLIGENCE LAYER                              |  |
|  |  Smart Ingestion | Hybrid Retriever (BM25+Dense) | Graph Augmenter       |  |
|  +--------------------------------------------------------------------------+  |
|                                                                             |
|  +--------------------------------------------------------------------------+  |
|  |                     STORAGE LAYER                                        |  |
|  |  Qdrant (Vectors) | Neo4j (Graph) | PostgreSQL (Metadata) | Redis Cache  |  |
|  +--------------------------------------------------------------------------+  |
|                                                                             |
|  +--------------------------------------------------------------------------+  |
|  |                         LLMOps LAYER                                     |  |
|  |  MLflow | LangFuse | Prometheus | Grafana | OpenTelemetry                |  |
|  +--------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------+
```

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

## 📄 License
This project is licensed under the MIT License.
