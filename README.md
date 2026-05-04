# QuestionCraft

## Overview

QuestionCraft is a backend-driven application designed to generate structured, university-level question papers from user-provided study materials. It leverages a Retrieval-Augmented Generation (RAG) pipeline to process multiple file formats and produce context-aware exam papers based on customizable parameters such as difficulty, marks distribution, and question types.

The system is built to simulate realistic academic paper setting by combining semantic retrieval, structured prompt engineering, and dynamic question composition.

---

## Features

* Generate complete question papers from uploaded syllabus or study material
* Supports multiple file formats including PDF, PPT, and CSV
* Handles scanned documents using OCR fallback
* Configurable difficulty levels (Easy, Medium, Hard)
* Custom question distribution across topics/chapters
* Flexible paper structure (sections, marks, question types)
* Context-aware question generation using semantic search
* FAISS-based vector indexing for efficient retrieval
* Modular pipeline for extensibility and experimentation

---

## System Architecture

The application follows a modular RAG-based pipeline:

1. **Input Processing**

   * Accepts user-uploaded files
   * Extracts text using format-specific loaders
   * Falls back to OCR when text extraction fails

2. **Text Chunking**

   * Splits content into semantically meaningful chunks
   * Prepares data for embedding and retrieval

3. **Embedding & Indexing**

   * Converts chunks into vector embeddings
   * Stores vectors using FAISS for fast similarity search

4. **Retrieval**

   * Fetches relevant chunks based on user query and constraints

5. **Question Generation**

   * Uses retrieved context to generate structured exam questions
   * Applies constraints such as marks, difficulty, and distribution

6. **Response Formatting**

   * Outputs a complete question paper in a structured format

---

## Tech Stack

**Backend**

* Python
* FastAPI
* Uvicorn

**RAG Pipeline**

* FAISS (vector search)
* Custom chunking and ranking strategies
* Prompt-based generation pipeline

**Document Processing**

* PyPDF / PDF loaders
* pdf2image + OCR (for scanned PDFs)
* Custom loader registry system

**Other**

* Async processing with asyncio
* Structured logging system
* Modular service-based architecture

---

## Project Structure

```
backend/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── paper.py          # API endpoint for paper generation
│   │
│   ├── core/
│   │   ├── config.py            # App configuration
│   │   ├── logging.py           # Custom logging setup
│   │   └── middleware.py        # Error handling middleware
│   │
│   ├── services/
│   │   └── paper_service.py     # Core business logic
│   │
│   ├── rag/
│   │   ├── pipeline.py          # RAG orchestration
│   │   ├── indexer/
│   │   │   └── pipeline.py      # Index building logic
│   │   ├── loaders/
│   │   │   ├── registry.py      # Loader selection
│   │   │   └── pdf.py           # PDF + OCR handling
│   │
│   └── models/                  # Data models (if applicable)
│
└── main.py                      # Entry point
```

---

## Installation

### Prerequisites

* Python 3.10+
* Homebrew (macOS) or equivalent package manager

### System Dependencies (Important)

Install OCR dependencies:

```bash
brew install poppler
brew install tesseract
```

---

### Setup

```bash
git clone https://github.com/Rishikesh4089/QuestionCraft.git
cd QuestionCraft/backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

### Run the Server

```bash
uvicorn app.main:app --reload
```

---

## API Usage

### Generate Question Paper

**Endpoint**

```
POST /api/v1/generate-paper/
```

**Request Parameters**

* Subject
* Difficulty
* Study material files
* Marks distribution
* Question types
* Chapter/topic distribution

**Response**

* Structured question paper with sections and marks allocation

---

## Key Design Decisions

* **RAG over fine-tuning**
  Ensures flexibility across subjects without retraining models

* **FAISS indexing**
  Enables scalable and fast semantic retrieval

* **OCR fallback pipeline**
  Handles real-world scanned documents effectively

* **Modular loaders**
  Easy to extend for new file formats

* **Separation of concerns**
  Clear split between API, services, and RAG pipeline

---

## Limitations

* OCR accuracy depends on input quality
* Performance may degrade with very large documents
* Requires proper system dependencies for full functionality
* Current pipeline may skip documents with extraction failures

---

## Future Improvements

* Multi-query retrieval and reranking strategies
* Better chunking using semantic boundaries
* Hybrid search (keyword + vector)
* Improved prompt optimization and context compression
* Frontend interface for interactive paper generation
* Export formats (PDF, DOCX)
* User authentication and saved paper history

---

## Contribution

Contributions are welcome. Feel free to fork the repository and submit pull requests for improvements or new features.

---

## License

This project is intended for educational and research purposes.

---