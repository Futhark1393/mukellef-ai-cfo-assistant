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
