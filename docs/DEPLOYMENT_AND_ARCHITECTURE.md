# CollabAI — Deployment and Architecture Specification

## 🏛 System Architecture Overview

CollabAI utilizes a modern decoupled service architecture designed for scalability, zero-cost development tiers, and seamless local orchestration:

```
+--------------------------------------------------------------------+
|                         Next.js 14 Web UI                          |
| (App Router, Tailwind CSS, TanStack Query, Lucide Icons, Dark Mode)|
+---------------------------------+----------------------------------+
                                  |
                   REST APIs & WebSockets (JSON)
                                  |
                                  v
+--------------------------------------------------------------------+
|                         FastAPI Core Server                        |
|       (Async routing, Pydantic v2 schemas, JWT Authentication)     |
+-------------------+--------------------+-------------------+-------+
                    |                    |                   |
                    v                    v                   v
     +--------------------+   +--------------------+   +-------------+
     |   PostgreSQL 16    |   |  Swappable LLMs    |   |  ML Engine  |
     |     + pgvector     |   | (Gemini / Groq /   |   | (XGBoost /  |
     | (Neon / Supabase / |   |     Ollama)        |   |  NetworkX)  |
     |    Local Docker)   |   |                    |   |             |
     +--------------------+   +--------------------+   +-------------+
```

---

## 🚀 Local Quickstart Guide

### 1. Prerequisites
- **Python:** 3.11+
- **Node.js:** 18.x or 20.x
- **Docker & Docker Compose:** Optional for local PostgreSQL/pgvector database

### 2. Backend Initialization
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations / table creation
python -m app.main

# Start development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Initialization
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## ⚙️ Environment Configuration

| Variable | Description | Default / Example |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy Async connection string | `sqlite+aiosqlite:///./collabai.db` or `postgresql+asyncpg://user:pass@localhost:5432/collabai` |
| `JWT_SECRET_KEY` | Secret key for signing session tokens | `super-secret-development-jwt-key` |
| `LLM_PROVIDER` | Selected LLM backend provider | `gemini` / `groq` / `ollama` |
| `GEMINI_API_KEY` | Google AI Studio free tier API key | `AIzaSy...` |
| `GROQ_API_KEY` | GroqCloud low-latency API key | `gsk_...` |
| `OLLAMA_BASE_URL`| Local Ollama inference server endpoint | `http://localhost:11434` |

---

## 🔒 Security Best Practices
- **Token Handling:** JWT access tokens are stored in secure httpOnly cookies or authorization headers.
- **CORS Protection:** Configured with explicit origins for production domains.
- **Input Sanitization:** Automatic validation on all incoming payloads via Pydantic v2 models.
