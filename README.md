# Aureus

Aureus is an automated **financial report extraction and rendering system** that parses company financial reports (PDFs or TXT files), extracts factual and tabular data, and generates structured Geojit-style research reports in HTML and PDF formats.

---

## Architecture Diagram

![Architecture Diagram](./diagram.png)

---

## Prerequisites

Before running the project locally, ensure you have the following installed:

| Tool                 | Recommended Version           | Notes                                                 |
| -------------------- | ----------------------------- | ----------------------------------------------------- |
| **Python**           | 3.11+                         | For backend API and workers                           |
| **Node.js**          | 18+                           | For Vite frontend                                     |
| **npm**              | latest                        | To install frontend dependencies                      |
| **PostgreSQL**       | 15+                           | For storing reports and file metadata                 |
| **RabbitMQ**         | latest                        | For async job orchestration between workers           |
| **S3-compatible OS** | Any (AWS S3, R2, MinIO, etc.) | Used for storing PDFs, extracted JSON, and HTML files |
| **Playwright**       | latest                        | Required for PDF rendering (Chromium)                 |

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
POSTGRES_PASSWORD="<your_db_password>"
POSTGRES_DB="aureus"
POSTGRES_PORT=5432


S3_BUCKET="aureus"
S3_REGION=""
S3_ACCESS_KEY="<your_s3_access_key>"
S3_SECRET_KEY="<your_s3_secret_key>"
S3_ENDPOINT="https://s3.amazonaws.com"


RABBITMQ_URL="amqp://user:password@localhost:5672/"
RABBITMQ_EXCHANGE="aureus"


OPENAI_API_KEY="<your_openai_api_key>"
```

> 💡 You can use **AWS S3**, **Cloudflare R2**, or **MinIO** — all are supported via standard boto3 client configuration.

---

### 7. Launch all services (API, frontend, workers)

```bash
make dev
```

This will start:

- FastAPI backend (port `8000`)
- Vite frontend (port `5173`)
- Extractor & Renderer background workers

### 8. Access the UI

Open [http://localhost:5173](http://localhost:5173) in your browser.

### 9. Stop the stack

```bash
make stop
```

---

## Tech Stack

| Layer              | Technology                                                           |
| ------------------ | -------------------------------------------------------------------- |
| **Backend API**    | FastAPI + SQLAlchemy (async)                                         |
| **Workers**        | Python (aio-pika, pdfplumber, pandas, OpenAI API, boto3, Playwright) |
| **Frontend**       | React + Vite + TailwindCSS                                           |
| **Message Queue**  | RabbitMQ (for async job orchestration)                               |
| **Object Storage** | S3-compatible (AWS S3 / R2 / MinIO)                                  |
| **Database**       | PostgreSQL                                                           |

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

### GPU Acceleration (Optional)

Aureus supports **GPU-accelerated OCR** when running on machines with **CUDA** and **NVIDIA drivers**.

The **EasyOCR** module automatically detects and uses a GPU if available; otherwise, it runs on CPU with no extra configuration required.

#### To enable GPU acceleration:

1. **Install NVIDIA drivers**

   ```bash
   sudo apt-get update
   sudo apt-get install -y nvidia-driver-550
   ```

2. **Verify GPU availability**

   ```bash
   nvidia-smi
   ```

3. **Install PyTorch with CUDA support**

   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

4. **(Optional) Force GPU usage**
   ```python
   import easyocr
   reader = easyocr.Reader(['en'], gpu=True)
   ```

#### Notes

- If you skip these steps, EasyOCR will default to **CPU mode**, which is fully supported — just slower.
- The rest of the Aureus stack (API, Renderer, Frontend) is **CPU-only** and does not depend on CUDA.

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
├── Makefile                 # Dev automation commands
└── README.md
```

---

### What “Aureus” Means

The name **Aureus** comes from the Latin word for _"golden"_ — symbolizing excellence, precision, and value.  
It reflects the project’s goal: turning raw, unstructured financial data into **refined, golden insights** through automation and intelligent processing.

---

## Author

**Avinash Sinha**  
Software Engineer, AsyncFoundry
