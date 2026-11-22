# 🛡️ RAG Sentinel — AI Knowledge-Base Security Platform

**RAG Sentinel** is an AI Security Operations Center (SOC) platform designed to defend Retrieval-Augmented Generation (RAG) knowledge systems against indirect prompt injection, adversarial overrides, and knowledge-poisoning attacks.

Built for academic research and cyber-defense demonstrations, RAG Sentinel features pre-ingestion threat detection, semantic contradiction analysis, cryptographic SHA-256 fingerprinting, administrator-verified knowledge indexing, and protected AI retrieval.

---

## 🌟 Key Capabilities

- **Secure Document Ingestion**: Ingests PDF and TXT files through automated heuristic scans and cryptographic SHA-256 fingerprinting.
- **Pre-Ingestion Threat Quarantine**: Automatically isolates adversarial prompt injections, instruction overrides, and policy contradictions into a Zero-Trust Quarantine Vault.
- **Administrator Review Queue**: Enforces human-in-the-loop verification before candidate documents can be indexed into the production vector database.
- **Protected AI Chat**: Zero-Trust query engine strictly bounded to administrator-approved knowledge chunks with live cryptographic evidence citations and chunk distance metrics.
- **RAG Poisoning Research Lab**: Controlled experimental suite evaluating vulnerable baseline behavior vs defended routing under clean, injected, and mixed retrieval conditions (using the Northstar IT Helpdesk scenario).
- **Empirical & Held-Out Evaluations**: Offline and held-out benchmark runners with confusion matrix calculation (accuracy, precision, recall, F1-score) and downloadable CSV decision logs.
- **Local Access Control & Governance**: Role-based access control (`admin`, `analyst`, `viewer`) with PBKDF2-HMAC-SHA256 password hashing and append-only cryptographic audit logging.

---

## 🏗️ Architecture & Security Pipeline

```
01 / INGEST          02 / INSPECT         03 / DECIDE          04 / PROTECT
PDF & TXT Uploads -> Heuristic Scan &  -> Admin Review vs   -> Approved-Only
                     SHA-256 Hash         Quarantine           ChromaDB RAG
```

The system strictly isolates production knowledge from experimental attack vectors:
- **`rag_approved_knowledge`**: Dedicated zero-trust ChromaDB collection queried exclusively by Protected AI Chat. Only administrator-approved documents are indexed.
- **`rag_knowledge_base`**: Dedicated experimental ChromaDB collection used by the Research Lab for controlled poisoning attacks.

---

## 🚀 Free Deployment Guide (Streamlit Community Cloud)

You can deploy RAG Sentinel to **Streamlit Community Cloud** for a public demonstration in under 5 minutes.

### Step 1: Push Repository to GitHub

Ensure your code is pushed to your GitHub repository (e.g. `your-username/RAG-Sentinel`).

> **Note:** Sensitive local files (`database/users.json`, `database/security_registry.json`, `database/chroma/`, `data/`) are excluded by `.gitignore` and are safely initialized automatically on first cloud launch.

### Step 2: Create App on Streamlit Cloud

1. Log into [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
2. Click **"New app"**.
3. Select your repository and branch (`master` or `main`).
4. Set **Main file path** to either `app/main.py` or `streamlit_app.py`.
5. Click **"Deploy!"**.

### Step 3: First-Launch Setup

1. On initial load, the application will detect a fresh environment and present the **First launch: create administrator account** screen.
2. Create your administrator credentials (minimum 12 characters, uppercase, lowercase, and a number).
3. Sign in to access the full operational platform.

---

## ⚡ Cloud vs Local Feature Matrix (Free Tier)

| Capability / Module | Streamlit Cloud (Free) | Local Workstation |
| :--- | :---: | :---: |
| **Security Overview Dashboard** | ✅ **Full Support** | ✅ **Full Support** |
| **Document Security & Upload** | ✅ **Full Support** | ✅ **Full Support** |
| **SHA-256 Fingerprinting** | ✅ **Full Support** | ✅ **Full Support** |
| **Heuristic & Override Detection** | ✅ **Full Support** | ✅ **Full Support** |
| **Admin Review Queue & Approval** | ✅ **Full Support** | ✅ **Full Support** |
| **ChromaDB Vector Indexing** | ✅ **Full Support** (all-MiniLM-L6-v2) | ✅ **Full Support** |
| **Quarantine Threat Vault** | ✅ **Full Support** | ✅ **Full Support** |
| **Synthetic Detector Benchmark** | ✅ **Full Support** | ✅ **Full Support** |
| **Multi-Policy Conflict Benchmark** | ✅ **Full Support** | ✅ **Full Support** |
| **End-to-End Routing Evaluation** | ✅ **Full Support** | ✅ **Full Support** |
| **Phase 6 Held-Out Evaluation** | ✅ **Full Support** | ✅ **Full Support** |
| **User & Audit Administration** | ✅ **Full Support** | ✅ **Full Support** |
| **Zero-Trust Evidence Retrieval** | ✅ **Full Support** | ✅ **Full Support** |
| **Live LLM Answer Synthesis** | ⚙️ **Requires Remote Ollama** | ✅ **Local Ollama** (`qwen2.5:1.5b`) |

### Enabling Live Ollama on Streamlit Cloud (Optional)

Streamlit Community Cloud is a serverless Python execution environment and cannot host local background daemons like Ollama. 

All detection, quarantine, ingestion, and vector search features work 100% out of the box. To additionally enable live LLM answer synthesis:

1. On your machine where Ollama is running (`ollama run qwen2.5:1.5b`), expose Ollama's port `11434` via a free tunnel (e.g. [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) or [ngrok](https://ngrok.com/)):
   ```bash
   ngrok http 11434
   ```
2. In your Streamlit Cloud app dashboard, go to **App Settings -> Secrets**.
3. Add your tunnel URL:
   ```toml
   OLLAMA_BASE_URL = "https://your-tunnel-subdomain.ngrok-free.app"
   ```
4. Save secrets. Protected AI Chat and Research Lab will instantly connect to your live model.

---

## 💻 Local Development Setup

### Prerequisites
- Python 3.11
- [Ollama](https://ollama.com/) with model `qwen2.5:1.5b` (`ollama pull qwen2.5:1.5b`)

### Quickstart

```powershell
# 1. Clone repository
git clone https://github.com/your-username/RAG-Sentinel.git
cd RAG-Sentinel

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Run automated test suite
python -m unittest discover tests

# 4. Launch RAG Sentinel
streamlit run app/main.py
```

Open your browser at `http://localhost:8501`.

---

## 🧪 Testing & Validation

Run the complete test suite:

```bash
python -m unittest discover tests
```

Tests cover:
- PBKDF2 password hashing, salt generation, and role checks (`test_phase7_security.py`)
- Heuristic injection detection & risk scoring (`test_evaluation.py`)
- Multi-policy semantic contradiction detection (`test_contradiction.py`, `test_policy_conflict_metrics.py`)
- End-to-end evidence routing (`test_end_to_end.py`)
- Held-out synthetic evaluation benchmarks (`test_phase6_heldout.py`)
- Live experiment summary parsing (`test_live_experiment.py`)

---

## 📄 License & Disclaimer

Academic cybersecurity research prototype. Developed for controlled laboratory experiments demonstrating indirect prompt injection and knowledge-base poisoning defenses.
