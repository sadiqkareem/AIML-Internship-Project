# AI Writer · Intelligent Text Summarizer

An enterprise-ready, open-source AI writing assistant and article summarizer powered by Hugging Face Transformers (`DistilBART`, `BART`, `T5`). Engineered with multi-pass sentence-aligned chunking to accurately condense long articles, research papers, and news essays while preserving key takeaways and readability.

---

## ✨ Features

- **Multi-Model Transformer Engine**:
  - `DistilBART` (`sshleifer/distilbart-cnn-12-6`) — Ultra fast, lightweight (~300MB), ideal for CPU and quick results.
  - `BART Large` (`facebook/bart-large-cnn`) — Deep CNN-based abstractive summarization.
  - `T5 Base` (`t5-base`) & `T5 Small` (`t5-small`) — Versatile text-to-text models for balanced synthesis.
- **Multiple Output Formats**:
  - **Standard Paragraph**: Coherent, fluent executive summary.
  - **Key Bullet Points**: Bulleted takeaways ready for presentations and briefing docs.
  - **Executive TL;DR**: One-to-two sentence high-impact summary.
- **Long Article Multi-Pass Chunking**:
  - Handles articles up to 30,000 words by grouping sentence-aligned chunks, summarizing chunk-by-chunk, and re-synthesizing merged passes.
- **Readability & Quantitative Metrics**:
  - Word count reduction & percentage saved.
  - Flesch Reading Ease score & grade level categorization.
  - Estimated reading time (seconds and minutes).
- **Multiple Document Ingestion Options**:
  - Direct paste with real-time word and reading-time counter.
  - Drag-and-drop file upload (`.txt`, `.md`).
  - One-click sample article loader.
  - URL article extractor (extract clean text directly from web URLs).
- **Persistent SQLite History**:
  - Saves past summaries with timestamps, models, formats, and compression ratios.
  - Restore previous articles back into the editor with one click, copy, or delete.
- **Modern Glassmorphic UI**:
  - Dark / Light mode toggle with persistent preference.
  - Responsive layout, animated loading states with elapsed timer, and keyboard shortcut (`Ctrl + Enter`).
- **Resilient Fallback**:
  - Built-in frequency-weighted extractive summarizer guarantees summarization even in low-memory or offline environments.

---

## 🚀 Quick Start (Local Run)

### Windows (One-Click)
Double-click `run.bat` or run:
```cmd
run.bat
```

### Linux / macOS
```bash
chmod +x run.sh
./run.sh
```

### Manual Setup
```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start development server
python app.py                   # Open http://localhost:5000
```

> **Note**: The default model is `distilbart` (~300MB, fast download and rapid CPU inference). To set a different default, set the environment variable `SUMMARIZER_MODEL=bart` or `SUMMARIZER_MODEL=t5`.

---

## 🧪 Testing

Run the automated test suite covering unit metrics, chunking logic, API routes, and history persistence:
```bash
pytest -v
```

---

## 📊 Generating Sample Outputs

To test sample articles across multiple models and generate `samples/sample_outputs.md`:
```bash
python generate_samples.py
```

---

## 🐳 Docker & Production Deployment

### Docker
```bash
# Build Docker image
docker build -t ai-writer .

# Run container
docker run -p 5000:5000 ai-writer
```

### Production WSGI Server
- **Linux / Cloud (Gunicorn)**:
  ```bash
  gunicorn -w 1 -t 300 -b 0.0.0.0:$PORT app:app
  ```
- **Windows (Waitress)**:
  ```bash
  waitress-serve --port=5000 app:app
  ```

---

## 📂 Project Architecture

```
ai-writer/
├── app.py              # Flask REST API, web routing, and SQLite storage
├── summarizer.py       # Transformers pipeline, chunking, and extractive fallback
├── readability.py      # Dependency-free Flesch scoring, grade level, and reading time
├── templates/
│   └── index.html      # Responsive glassmorphic frontend UI (Dark/Light)
├── samples/
│   ├── sample_article.txt  # Sample article for benchmarking
│   └── sample_outputs.md  # Generated multi-model comparison outputs
├── tests/
│   ├── test_app.py         # Flask route and history integration tests
│   ├── test_readability.py # Readability formula unit tests
│   └── test_summarizer.py  # Chunking, splitting, and format tests
├── requirements.txt    # Production dependencies
├── Dockerfile          # Containerized deployment spec
├── run.bat             # One-click Windows runner
├── run.sh              # One-click Unix runner
└── pytest.ini          # Pytest path configuration
```
