# RoamGenie Architecture Overview

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Detailed Specification:** [docs/architecture/SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)

---

## 1. Executive Summary

RoamGenie is an intelligent, relational database-centric travel planning platform designed to eliminate the fragmentation of multi-app vacation planning. Built on a clean decoupled 3-tier architecture, it combines a React 18 frontend with a high-performance FastAPI backend, a 22-table PostgreSQL database hosted on Supabase, and a bounded AI gateway.

---

## 2. 3-Tier Layer Summary

| Tier | Component | Technologies | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| **Tier 1: Client** | Web Single-Page Application | React 18, Vite, React Router DOM, CSS Tokens | User authentication, interactive planning wizard, day-by-day timeline, visual budget bar with deficit alerts, packing checklist, and AI copilot drawer. |
| **Tier 2: API Gateway & Services** | Backend Application Server | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 | Request validation, Argon2id/JWT auth, deterministic scheduling, iterative budget optimization, multi-provider LLM orchestration, Open-Meteo weather client, and transactional persistence. |
| **Tier 3: Database** | Relational Database Management System | PostgreSQL 15+ (Hosted on Supabase) | 22 normalized tables (3NF/BCNF), primary/foreign keys, `CHECK` constraints, composite uniqueness, database views, stored procedures, PL/pgSQL audit triggers, and B-Tree indexes. |

---

## 3. Core Security & Isolation Principles

1. **Zero Client Secrets:** The React frontend communicates strictly with FastAPI over JSON REST endpoints. No database passwords or Supabase keys are exposed.
2. **Resource Ownership Enforcement:** All trip access and modifications are guarded by `verify_trip_ownership()`, ensuring complete isolation between users.
3. **Bounded AI Gateway:** AI models receive strictly formatted catalogue facts and return Pydantic-validated JSON. The AI has zero direct database execution permissions.
4. **Deterministic Resilience:** Offline mode is built-in; the application operates 100% reliably using the deterministic catalogue scheduler even when third-party APIs are down.
