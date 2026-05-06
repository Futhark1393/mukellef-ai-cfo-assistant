# Mükellef - AI CFO Assistant | Development Roadmap

**Team Lead / Maintainer:** Futhark1393
**Feature Developers:** SMBayraktar, alaraayuceturk
**Event:** SolveX AI Hackathon 2026

## Phase 1: Project Initialization & AI Planning (09:00 - 09:30)
*   [x] **Futhark1393:** Initialize GitHub Repository with branch protection rules (`main` branch locked).
*   [x] **Futhark1393:** Setup base FastAPI boilerplate and virtual environment.
*   [x] **Futhark1393:** Consult **Plan Agent** to generate `ARCHITECTURE.md` and `ROADMAP.md`.
*   [x] **Futhark1393:** Commit initial boilerplate to `main` repository.

## Phase 2: Parallel Feature Development (09:30 - 12:00)
*   **Task 1: OCR Processing**
    *   [ ] **Developer:** SMBayraktar (Windows Environment)
    *   [ ] **Branch:** `feature/ocr-processing`
    *   [ ] Implement document upload endpoint.
    *   [ ] Integrate OCR parsing logic (use **Skills Agent** for extraction optimization).
    *   [ ] Ensure AI Traceability comments are added.
*   **Task 2: Cashflow Prediction**
    *   [ ] **Developer:** alaraayuceturk (Windows Environment)
    *   [ ] **Branch:** `feature/cashflow-prediction`
    *   [ ] Develop 3-6 months projection algorithm based on mock financial data.
    *   [ ] Add AI Traceability comments.
*   **Task 3: Expense Allocation**
    *   [ ] **Developer:** Futhark1393 (Fedora Environment)
    *   [ ] **Branch:** `feature/expense-allocation`
    *   [ ] Create logic to divide prepaid expenses into monthly chunks.
    *   [ ] Add AI Traceability comments.

## Phase 3: Integration & Code Review (12:00 - 14:00)
*   [ ] **SMBayraktar & alaraayuceturk:** Open Pull Requests (PRs) for completed feature branches.
*   [ ] **Code Review (Futhark1393):** Review PRs for code quality, conflict resolution, and AI Traceability tags.
*   [ ] **Futhark1393:** Merge approved feature branches into `main`.
*   [ ] **Team:** Connect Frontend (`app.js`) to the unified FastAPI endpoints.

## Phase 4: AI Refactoring & MVP Finalization (14:00 - 15:00)
*   [ ] **Futhark1393:** Run entire codebase through AI for **Final Review, Refactoring, and Optimization**.
*   [ ] **Team:** Conduct end-to-end testing: Upload receipt -> Process OCR -> Allocate Expenses -> View Cashflow.
*   [ ] **Team:** Fix UI/UX bugs on the dashboard.

## Phase 5: Demoday Preparation (15:00 - 17:00)
*   [ ] **Futhark1393:** Freeze code repository.
*   [ ] **Team:** Prepare live demonstration scenario (loading a test invoice and showing automated outcomes).
*   [ ] **Team:** Finalize pitch highlighting "Autonomous Accounting" and "Agentic Workflow" efficiency.

## Phase 6: Post-MVP (Phase 2) Roadmap
*   **Mert (Computer Vision focus):**
    *   [ ] Upgrade OCR pipeline to support multi-page PDF invoices.
    *   [ ] Implement line item extraction for tax breakdown and detailed categorization.
*   **Alara (Financial Data focus):**
    *   [ ] Add burn rate calculator based on historical cashflow data.
    *   [ ] Add runway projection with configurable scenarios.
*   **Futhark (System Architecture focus):**
    *   [ ] Implement PostgreSQL persistence layer with migrations.
    *   [ ] Add JWT-based authentication for multi-tenant users.
    *   [ ] Wire auth endpoints to Postgres (register/login/refresh).
    *   [ ] Document required auth/database environment variables.

## Phase 7: Business Operations Expansion (Draft)
*   **Alara (Financial Data focus):**
    *   [ ] Bank transactions ingestion and daily financial tracking outputs.
    *   [ ] 6-month cashflow forecast improvements with scenario inputs.
    *   [ ] Cost and profitability analysis (gross profit vs profitability metrics).
*   **SMBayraktar (OCR and Documents focus):**
    *   [ ] OCR for purchase invoices with item grouping (goods vs stock groups).
    *   [ ] Mobile OCR intake flow for receipts/invoices (mock pipeline).
*   **Futhark (System Architecture focus):**
    *   [ ] Current account (cari) tracking with auto receipt generation on payment.
    *   [ ] Supplier payment tracking (tediyeler) and payment planning.
    *   [ ] Stock and inventory management with in/out stock tracking.
    *   [ ] Inventory valuation (FIFO/LIFO) calculation utilities.
    *   [ ] Check and promissory note management (given/received/clearing).
    *   [ ] Tax and payroll month-end process tracking (KDV, Muhtasar, payroll).
    *   [ ] Employee attendance and time tracking calculations.
    *   [ ] Vehicle insurance/expense tracking with periodization.
    *   [ ] Prepaid expense separation across periods.
