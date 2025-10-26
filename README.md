# Aureus

Aureus is an automated **financial report extraction and rendering system** that parses company financial reports (PDFs or TXT files), extracts factual and tabular data, and generates structured Geojit-style research reports in HTML and PDF formats.

---

## Prerequisites

Before running the project locally, ensure you have the following installed:

| Tool                        | Recommended Version | Notes                                         |
| --------------------------- | ------------------- | --------------------------------------------- |
| **Python**                  | 3.11+               | For backend API and workers                   |
| **Node.js**                 | 18+                 | For Vite frontend                             |
| **npm**                     | latest              | To install frontend dependencies              |
| **Docker & Docker Compose** | latest              | To run Postgres, RabbitMQ, and MinIO services |
| **Playwright**              | latest              | Required for PDF rendering (Chromium)         |
| **Make**                    | any                 | Used to manage local development commands     |

---

## How to Run (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/webdevavi/aureus.git
cd aureus
```

### 2. Create and activate a Python virtual environment

#### macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell):

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python backend dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Playwright browsers (required for rendering PDFs)

```bash
playwright install chromium
```

> ⚠️ This step downloads the Chromium binary used by the renderer worker.  
> If you skip it, you will get an error like:  
> “BrowserType.launch: Executable doesn't exist at ... headless_shell”.

### 5. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 6. Add a `.env` file

Create a new file named `.env` at the root of the project and add the following:

```bash
API_BASE_URL="http://localhost:8000"
CORS_ORIGIN="http://localhost:5173"

MAX_WORKERS=4

POSTGRES_HOST="localhost"
POSTGRES_USER="aureus"
POSTGRES_PASSWORD="<generate new secret>"
POSTGRES_DB="aureus"
POSTGRES_PORT=5432

MINIO_BUCKET="aureus"
MINIO_PORT=9000
MINIO_ENDPOINT="http://localhost:9900"
MINIO_ACCESS_KEY="aureus"
MINIO_SECRET_KEY="<generate new secret>"
MINIO_REGION=""

RABBITMQ_DEFAULT_USER="aureus"
RABBITMQ_DEFAULT_PASS="<generate new secret>"
RABBITMQ_PORT=5673
RABBITMQ_URL="amqp://aureus:<generate new secret>@localhost:5673/"
RABBITMQ_EXCHANGE="aureus"

OPENAI_API_KEY="<your OpenAI API key>"
```

> ⚠️ Make sure to generate strong random secrets for all passwords before deployment.

### 7. Start the infrastructure (Postgres, MinIO, RabbitMQ)

```bash
make up
```

### 8. Launch all services (API, frontend, workers)

```bash
make dev
```

This will start:

- FastAPI backend (port `8000`)
- Vite frontend (port `5173`)
- Extractor & Renderer background workers

### 9. Access the UI

Open [http://localhost:5173](http://localhost:5173) in your browser.

### 10. Stop the stack

```bash
make stop
```

---

## Tech Stack

| Layer              | Technology                                                               |
| ------------------ | ------------------------------------------------------------------------ |
| **Backend API**    | FastAPI + SQLAlchemy (async)                                             |
| **Workers**        | Python (aio-pika, pdfplumber, pandas, OpenAI API, MinIO SDK, Playwright) |
| **Frontend**       | React + Vite + TailwindCSS                                               |
| **Message Queue**  | RabbitMQ (for async job orchestration)                                   |
| **Object Storage** | MinIO (S3-compatible, stores PDFs/JSON/HTML)                             |
| **Database**       | PostgreSQL                                                               |

---

## Template & Field Definitions

| Component         | Location                                                                     | Description                                                                    |
| ----------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **HTML Template** | `backend/templates/report.html`                                              | Jinja2 template for rendering final HTML reports                               |
| **PDF Renderer**  | `backend/workers/renderer/main.py`                                           | Converts rendered HTML into a styled PDF using Playwright                      |
| **Field Mapping** | `PROMPT_TEMPLATE` inside `backend/workers/extractor/utils/prompt_builder.py` | Defines how LLM interprets and maps financial terms (Sales, EBITDA, PAT, etc.) |

---

Each report includes:

- Key highlights summary
- Tabular YoY/QoQ performance data
- Consolidated financial metrics
- Auto-generated analyst commentary

---

## Notes

- Supports both **PDF** and **TXT** source files.
- Automatically queues jobs for extraction and rendering once upload is complete.
- Uses presigned MinIO URLs for upload/download.
- Workers auto-detect file type and run the appropriate parsing pipeline.
- Requires one-time `playwright install chromium` setup on fresh environments.

---

## Folder Structure

```
aureus/
├── backend/
│   ├── api/                 # FastAPI endpoints (reports, files)
│   └── workers/
│       ├── extractor/       # PDF/TXT parsing + JSON generation
│       └── renderer/        # HTML → PDF rendering
├── frontend/                # React + Vite UI
├── docker-compose.yml       # Infrastructure stack
├── Makefile                 # Dev automation commands
└── README.md
```

---

## Author

**Avinash Sinha**  
Software Engineer, AsyncFoundry
