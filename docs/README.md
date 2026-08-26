# RoamGenie — Documentation Index

Welcome to the technical documentation for **RoamGenie — AI Travel Planner & Budget Optimizer** (Semester 5 DBMS Theory & Project).

---

## 📁 Master Documentation Structure

```text
docs/
├── README.md                              # Master Documentation Index (This Document)
├── requirements/
│   ├── PROBLEM_STATEMENT.md               # Academic Problem Statement & Objectives
│   ├── SRS.md                             # Software Requirements Specification (FR-01 to FR-12)
│   ├── REQUIREMENTS_TRACEABILITY.md       # Requirements Traceability Matrix (RTM)
│   ├── PROJECT_SPECIFICATION.md           # Master Requirements Specification & DBMS Mapping
│   └── REQUIREMENTS_MATRIX.md             # Detailed Requirements Matrix
├── architecture/
│   ├── SYSTEM_ARCHITECTURE.md             # 3-Tier System Architecture & Topology
│   ├── DATA_FLOW.md                       # End-to-End Data Flow & Lifecycle Diagrams
│   ├── SECURITY_ARCHITECTURE.md           # Security Architecture, IDOR Guards, & Controls
│   └── ARCHITECTURE_OVERVIEW.md           # High-Level Architecture Overview
├── database/
│   ├── ER_DIAGRAM.md                      # Entity-Relationship Diagram (23 Tables, Mermaid)
│   ├── DATABASE_DESIGN.md                 # 3NF Normalization Proofs & Relational Design
│   ├── RELATIONAL_SCHEMA.md               # Formal Relational Schema Definitions
│   ├── DATA_DICTIONARY.md                 # Column Types, Nullability, Defaults, & Constraints
│   ├── DATABASE_FEATURES.md               # DDL, DML, DCL, TCL, Triggers, & Analytical SQL
│   ├── DATABASE_ARCHITECTURE.md           # Physical Database Architecture
│   └── NORMALIZATION.md                   # Relational Normalization Proofs
├── api/
│   └── API_SPECIFICATION.md               # REST API Specification & Endpoint Contracts
├── ai/
│   ├── AI_FEATURES.md                     # AI Feature Inventory & Capabilities
│   └── AI_ARCHITECTURE.md                 # Multi-Provider LLM Gateway & Grounding Engine
├── testing/
│   ├── TESTING.md                         # Comprehensive Testing Framework & Guide
│   ├── TEST_RESULTS.md                    # Live Verified Test Results (162/162 PASS)
│   ├── REGRESSION_TEST_REPORT.md          # Full Regression Test Verification Report
│   └── TESTING_STRATEGY_AND_REPORT.md     # Historical Testing Strategy & Report
├── datasets/
│   ├── DATASET_DOCUMENTATION.md           # Master Dataset Overview (500 Cities, 21,133 Rows)
│   ├── DATASET_VERIFICATION_REPORT.md     # Live Database Row Count & FK Verification
│   └── CATALOGUE_DATASETS_REPORT.md       # Catalogue Dataset Analysis
├── milestones/
│   └── MILESTONE_COMPLETION_STATUS.md     # Academic Milestone Tracker (12/12 COMPLETE)
├── release/
│   ├── RELEASE_NOTES.md                   # v1.0.0 Release Notes & Feature Inventory
│   ├── MVP_RELEASE_REPORT.md              # MVP Release Verification Report
│   ├── KNOWN_LIMITATIONS.md               # System Boundaries & Post-MVP Roadmap
│   ├── DOCUMENTATION_AUDIT_REPORT.md      # Documentation Synchronization Audit Report
│   └── V1.0.0_RELEASE_REPORT.md           # Historical v1.0.0 Release Report
├── presentation/
│   └── PRESENTATION_AND_VIVA_GUIDE.md     # 15-Slide Presentation Outline & 7-Min Demo Script
├── guides/
│   ├── DEVELOPER_GUIDE.md                 # Developer & Admin Credentials, Commands & Environment
│   ├── DEPLOYMENT_AND_OPERATIONS.md       # Local & Supabase Deployment Guide
│   ├── PRESENTATION_AND_VIVA_GUIDE.md     # Live Demonstration & Defense Script
│   └── RISK_REGISTER.md                   # Technical Risk Register & Mitigations
└── PROJECT_CHECKLIST.md                   # Master Academic & Technical Progress Checklist
```

---

## 🎯 Quick Links by Role

* **For Academic Evaluators & Instructors:**
  1. [Master Academic & Technical Checklist](PROJECT_CHECKLIST.md)
  2. [Problem Statement](requirements/PROBLEM_STATEMENT.md) & [SRS](requirements/SRS.md)
  3. [Entity-Relationship Diagram](database/ER_DIAGRAM.md) & [Relational Schema](database/RELATIONAL_SCHEMA.md)
  4. [Database Design & Normalization](database/DATABASE_DESIGN.md)
  5. [Data Dictionary (23 Tables)](database/DATA_DICTIONARY.md)
  6. [Database Advanced Features & 10 Analytical Queries](database/DATABASE_FEATURES.md)
  7. [Dataset Verification Report (21,133 Records)](datasets/DATASET_VERIFICATION_REPORT.md)
  8. [Academic Milestone Completion Status (12/12 Complete)](milestones/MILESTONE_COMPLETION_STATUS.md)
  9. [Presentation & Viva Defense Guide](presentation/PRESENTATION_AND_VIVA_GUIDE.md)

* **For Developers & Engineers:**
  1. [Developer & Admin Reference Guide (Credentials & Commands)](guides/DEVELOPER_GUIDE.md)
  2. [System Architecture](architecture/SYSTEM_ARCHITECTURE.md) & [Data Flow](architecture/DATA_FLOW.md)
  3. [Security Architecture & IDOR Controls](architecture/SECURITY_ARCHITECTURE.md)
  4. [AI Grounding Architecture](ai/AI_ARCHITECTURE.md)
  5. [Testing Guide & Verified Results](testing/TEST_RESULTS.md)
  6. [REST API Specification](api/API_SPECIFICATION.md)

* **For Release & Quality Auditors:**
  1. [MVP Release Report](release/MVP_RELEASE_REPORT.md)
  2. [Requirements Traceability Matrix](requirements/REQUIREMENTS_TRACEABILITY.md)
  3. [Regression Test Report](testing/REGRESSION_TEST_REPORT.md)
  4. [Documentation Audit Report](release/DOCUMENTATION_AUDIT_REPORT.md)
