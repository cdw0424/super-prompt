# SQLite-based LTM (FTS5 + optional Vector) — Dev-Only

This directory contains a reference implementation for a long‑term memory (LTM)
controller using SQLite + FTS5 and optional vector extensions (sqlite‑vss/vec).

Important: This LTM is NOT published with the npm package and MUST NOT be
bundled into user apps. It exists only for local prompt‑engineering workflows.

## Overview
- Three‑layer philosophy preserved: Specification → Instance (SQLite) → Controller
- Hybrid retrieval pipeline: FTS5 → vector re‑ranking → score fusion → token budget
- Safe governance: validation first (AJV), RBAC/quotas (add as needed), telemetry

## Files
- `schema.sql` — SQLite DDL for project/memory/embedding + FTS5 triggers
- `controller.ts` — Minimal TS controller with AJV validation and hybrid search

## Quick Start (Dev Only)
1) Create DB and schema
```bash
sqlite3 ltm.db < schema.sql
```

2) Install deps (pinned stable)
```bash
pnpm add better-sqlite3@12.2.0 ajv@8.17.1 zod@4.1.8 ioredis@5.7.0
```

3) Build/run (sample)
```bash
ts-node controller.ts
```

4) Optional: Load vector extension
- Use `sqlite-vss` or `sqlite-vec` per your platform setup
- Adjust `schema.sql` accordingly and keep a pure‑SQLite fallback (cosine in app)

## Packaging Guardrails
- This directory is excluded from npm publish (not listed under `files`)
- Do not import it from application code; use only from local tooling

## Migration Path
- Start with FTS5 + cosine re‑ranking
- Upgrade to sqlite‑vss/vec
- Scale out to Qdrant/Milvus/Pinecone or Postgres+pgvector using the same repo API
