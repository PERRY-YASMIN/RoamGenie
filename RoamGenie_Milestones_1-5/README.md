# RoamGenie — Academic Submission Package (Milestones 1–5)

## 📌 Project Overview
**RoamGenie — AI Travel Planner & Budget Optimizer** is an intelligent, relational database-backed travel scheduling and budget optimization platform developed for the **Semester 5 Database Management Systems (DBMS Theory & Project)** curriculum.

The system takes natural user constraints (*"I have ₹30,000, 5 days, and want to explore Jaipur"*), queries a normalized PostgreSQL travel catalogue of destinations, accommodations, dining venues, attractions, and transit options, and generates a structured, day-wise schedule with itemized budget tracking, real-time deficit alerts, weather grounding, and interactive activity swapping.

---

## 🎯 Purpose of this Package
This package is a **self-contained academic submission deliverable** covering the conceptual, requirements, and relational database engineering work required for **Milestones 1 through 5**.

It is formatted for direct upload to a shared Google Drive folder. Every team member will use this consolidated documentation as the official common project reference to independently prepare their individual presentation slide decks (PPTs) and academic reports.

> **Academic Separation Notice:** This package is an academic submission deliverable and is intentionally maintained in this dedicated directory. The repository's main [`docs/`](../docs/) directory remains the comprehensive technical source of truth for the complete application codebase, migrations, test suites, and v1.0.0 release.

---

## 📁 Included Documents & Index

```text
RoamGenie_Milestones_1-5/
│
├── README.md                                 # Package Index, Context, & Validation Summary (This File)
│
├── Problem_Statement.md                      # Milestone 1: Domain Background, Problem Definition, Objectives
│
├── Software_Requirements_Specification.md    # Milestone 2: SRS (FR-01 to FR-18, NFRs, Use Cases, Constraints)
│
├── ER_Diagram/                               # Milestone 3: Entity-Relationship Diagram
│   ├── ER_Diagram.png                        # High-Resolution Visual ER Diagram (Presentation/Submission Quality)
│   └── ER_Diagram.md                         # Complete Mermaid ER Diagram & Entity/Relationship Descriptions
│
├── Normalized_Database_Design.md             # Milestone 4: Functional Dependencies, 1NF, 2NF, 3NF & BCNF Proofs
│
├── Relational_Schema.md                      # Milestone 5: Mathematical Relational Notation & Table Specifications
│
└── PROJECT_CHECKLIST.md                      # Academic & Technical Progress Checklist (Done / Pending)
```

---

## 📑 Detailed Document Descriptions

### 1. [`Problem_Statement.md`](Problem_Statement.md) — Milestone 1
* **Focus:** Problem context, limitations of fragmented travel tools and ungrounded LLMs, proposed relational solution, 6 academic objectives, target user personas, and expected outcomes.

### 2. [`Software_Requirements_Specification.md`](Software_Requirements_Specification.md) — Milestone 2
* **Focus:** 3-Tier system perspective, user roles (`traveller` and `admin`), 18 functional requirements (FR-01 to FR-18), 10 non-functional quality metrics, system constraints, and use-case interaction flows.

### 3. [`ER_Diagram/ER_Diagram.md`](ER_Diagram/ER_Diagram.md) & [`ER_Diagram/ER_Diagram.png`](ER_Diagram/ER_Diagram.png) — Milestone 3
* **Focus:** Visual and textual Entity-Relationship modeling covering all 22 domain relations (+ 1 audit ledger), detailed entity attribute descriptions, and complete cardinality matrix ($1:1$, $1:N$, $N:M$).

### 4. [`Normalized_Database_Design.md`](Normalized_Database_Design.md) — Milestone 4
* **Focus:** Formal functional dependency analysis ($X \rightarrow Y$), First Normal Form (1NF) attribute atomicity, Second Normal Form (2NF) partial dependency removal, Third Normal Form (3NF) transitive dependency removal, Boyce-Codd Normal Form (BCNF) proofs, and anomaly elimination.

### 5. [`Relational_Schema.md`](Relational_Schema.md) — Milestone 5
* **Focus:** Compact mathematical relational schema notation ($\text{TABLE}(\underline{\text{PK}}, \text{attr}, \text{FK} \rightarrow \text{RefTable.PK})$), table-by-table attribute specifications, data types, primary keys, foreign keys with cascading referential actions, check constraints, and unique constraints.

---

## 🔍 Validation & Technical Integrity Report

| Verification Dimension | Source of Truth Checked | Audit Verdict | Status |
| :--- | :--- | :--- | :---: |
| **Source of Truth Used** | PostgreSQL Schema (`001_schema.sql`) & SQLAlchemy Models | Verified 100% against actual codebase | **PASS** |
| **Exact Database Table Count** | Live PostgreSQL Database (Supabase) | **22 Domain Tables** (+ 1 `trip_audit` table = 23) | **PASS** |
| **ER Diagram Consistency** | `ER_Diagram.md` & `ER_Diagram.png` | Exactly matches all 22 relations, PKs, FKs, and cardinalities | **PASS** |
| **Relational Schema Consistency**| `Relational_Schema.md` | All columns, constraints, unique keys, and cascade actions match | **PASS** |
| **Milestone Scope Boundary** | Milestone 1 to Milestone 5 strictly | Contains zero M6+ query benchmarks, seed scripts, or test logs | **PASS** |
| **Existing Docs Integrity** | Main repository [`docs/`](../docs/) | **Untouched and 100% preserved** | **PASS** |
