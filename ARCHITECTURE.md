# Mükellef - AI CFO Assistant | System Architecture

**Team Lead / Maintainer:** Futhark1393
**Feature Developers:** SMBayraktar, alaraayuceturk
**Event:** SolveX AI Hackathon 2026

## 1. System Overview
"Mükellef" is an AI-augmented autonomous accounting assistant. The system is designed to ingest financial documents, generate accurate accounting entries, process expense allocations, and forecast future cash flows. 

## 2. Technology Stack
*   **Backend:** FastAPI (Python)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript (No-build approach for rapid MVP development)
*   **Database:** SQLite (Lightweight, local file-based storage suitable for MVP without containerization overhead)
*   **Version Control:** Git & GitHub (GitHub Flow with strict branch protection)

## 3. Core Modules (Feature Branches)
The architecture is modular, divided into three main operational branches developed by the team members:

### A. OCR Processing Module (`feature/ocr-processing`) -> SMBayraktar
*   **Purpose:** Extracts structured financial data (amounts, dates, VAT, supplier info) from raw invoice images.
*   **Agent Interaction:** Skills Agent is utilized to optimize regex patterns and text parsing logic for high accuracy.

### B. Cashflow Prediction Module (`feature/cashflow-prediction`) -> alaraayuceturk
*   **Purpose:** Analyzes current entries and generated expense distributions to forecast financial standing for the next 3 to 6 months.
*   **Agent Interaction:** AI analyzes historical data patterns to generate predictive financial models.

### C. Expense Allocation Module (`feature/expense-allocation`) -> Futhark1393
*   **Purpose:** Automatically distributes prepaid expenses (e.g., yearly insurance) across relevant monthly periods (Dönemsellik İlkesi).
*   **Agent Interaction:** AI is used to validate the mathematical distribution logic and ensure compliance with accounting principles.

## 4. AI-Augmented Development (Agentic Workflow)
This project strictly follows the AI-Augmented Development methodology:
*   **Plan Agent:** This architecture and the accompanying roadmap were generated using an AI Plan Agent to ensure structural integrity before coding began.
*   **Skills Agent:** Complex algorithmic challenges are handled via AI agents acting as "Expert Developers".
*   **AI Traceability:** All code blocks generated or heavily optimized by AI contain explicit inline documentation in English.

## 5. Directory Structure
```text
mukellef-ai-cfo-assistant/
│
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── ARCHITECTURE.md          # System architecture and AI strategy
├── ROADMAP.md               # Development milestones and tasks
│
├── static/                  # Frontend assets
│   ├── index.html           # Main dashboard UI
│   ├── style.css            # UI styling
│   └── app.js               # Frontend logic and API integration
│
└── core/                    # Core business logic
    ├── ocr_engine.py        # OCR parsing logic (SMBayraktar)
    ├── cashflow.py          # Prediction algorithms (alaraayuceturk)
    └── expense_manager.py   # Period allocation logic (Futhark1393)
```
