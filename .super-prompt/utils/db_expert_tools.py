#!/usr/bin/env python3
"""
DB Expert Utilities — helper functions for Prisma + 3NF workflows.
English only. Logs must start with '--------'.

These helpers generate pragmatic starting points; they do not replace
domain-driven design or full migrations review.
"""
from __future__ import annotations
import os, re, json, datetime
from typing import Dict, List, Optional


def log(msg: str) -> None:
    print(f"-------- {msg}")


PRISMA_HEADER = """// Prisma schema template (datasource+generator)
// Adjust provider/url via env; keep migrations safe and incremental.
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = env("PRISMA_DB_PROVIDER") // e.g., "postgresql"
  url      = env("DATABASE_URL")
}
"""


def build_prisma_model(name: str, fields: List[Dict[str, str]]) -> str:
    """Build a Prisma model block from field descriptors.
    fields: [{name, type, attrs?}, ...]
    """
    lines = [f"model {name} {{"]
    for f in fields:
        typ = f.get("type", "String")
        attrs = f.get("attrs", "")
        space = " " if attrs and not attrs.startswith(" ") else ""
        lines.append(f"  {f['name']} {typ}{space}{attrs}")
    lines.append("}")
    return "\n".join(lines)


def build_prisma_schema(entities: Dict[str, List[Dict[str, str]]], extras: str = "") -> str:
    """Assemble a full Prisma schema. entities is a mapping of modelName -> fields[]."""
    parts = [PRISMA_HEADER.strip(), ""]
    for name, fields in entities.items():
        parts.append(build_prisma_model(name, fields))
        parts.append("")
    if extras:
        parts.append("// Extras (indexes/@@map/@@unique etc.)")
        parts.append(extras.strip())
    return "\n".join(parts).rstrip() + "\n"


def suggest_indexes(schema_text: str) -> List[str]:
    """Naive heuristics to suggest indexes for fields used as foreign keys or lookups."""
    suggestions: List[str] = []
    for model_block in re.findall(r"model\s+([A-Za-z0-9_]+)\s*{([^}]+)}", schema_text, re.S):
        model, body = model_block
        for line in body.splitlines():
            line = line.strip()
            if re.search(r"@relation", line):
                fname = line.split()[0]
                suggestions.append(f"model {model}: consider @@index([{fname}]) for relation lookups")
            if re.search(r"createdAt|updatedAt|email|name|status", line, re.I):
                fname = line.split()[0]
                suggestions.append(f"model {model}: candidate index on {fname}")
    return suggestions


def generate_docs(schema_text: str, title: str = "Database Documentation") -> str:
    """Produce a minimal, clean DB doc in Markdown with ERD summary placeholder."""
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    models = re.findall(r"model\s+([A-Za-z0-9_]+)\s*{([^}]+)}", schema_text, re.S)
    out = [
        f"# {title}",
        f"_Last updated: {now}_",
        "",
        "## Overview",
        "- This document describes entities, relations, constraints, and query patterns.",
        "- Prisma is the default ORM; see `schema.prisma` for the authoritative schema.",
        "",
        "## ERD (Summary)",
        "- List key entities and relations in plain text (or attach diagram).",
        "",
        "## Entities",
    ]
    for model, body in models:
        out.append(f"### {model}")
        out.append("Fields:")
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("@@"):  # skip decorations
                continue
            parts = line.split()
            name = parts[0]
            typ = parts[1] if len(parts) > 1 else "?"
            out.append(f"- `{name}`: `{typ}`")
        out.append("")
    out += [
        "## Constraints & Indexes",
        "- Document PRIMARY KEYs, UNIQUE constraints, CHECKs (if any), and indexes.",
        "",
        "## Query Patterns",
        "- Typical SELECTs with pagination/sorting, write paths, and transactions.",
        "",
        "## Migrations",
        "- Outline migration order, backfills, and rollback strategy.",
    ]
    return "\n".join(out) + "\n"


def read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def write_text(path: str, data: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    log(f"write → {path}")


def main(argv: List[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="db-expert-tools")
    sub = p.add_subparsers(dest="cmd")

    p_tpl = sub.add_parser("template", help="Emit a starter Prisma schema")
    p_tpl.add_argument("--out", default="prisma/schema.prisma")

    p_doc = sub.add_parser("doc", help="Generate DB documentation from Prisma schema")
    p_doc.add_argument("--schema", default="prisma/schema.prisma")
    p_doc.add_argument("--out", default="docs/db.md")

    args = p.parse_args(argv[1:])
    if args.cmd == "template":
        entities = {
            "User": [
                {"name": "id", "type": "String", "attrs": "@id @default(cuid())"},
                {"name": "email", "type": "String", "attrs": "@unique"},
                {"name": "name", "type": "String?"},
                {"name": "createdAt", "type": "DateTime", "attrs": "@default(now())"},
            ],
            "Order": [
                {"name": "id", "type": "String", "attrs": "@id @default(cuid())"},
                {"name": "userId", "type": "String"},
                {"name": "status", "type": "String"},
                {"name": "createdAt", "type": "DateTime", "attrs": "@default(now())"},
                {"name": "user", "type": "User", "attrs": "@relation(fields: [userId], references: [id])"},
            ],
        }
        extras = """// Example composite indexes
// model Order { ... }
// @@index([userId, createdAt])
"""
        schema = build_prisma_schema(entities, extras)
        write_text(args.out, schema)
        for s in suggest_indexes(schema):
            log(s)
        return 0
    if args.cmd == "doc":
        schema = read_text(args.schema)
        if not schema:
            log(f"Schema not found: {args.schema}")
            return 2
        md = generate_docs(schema)
        write_text(args.out, md)
        return 0
    p.print_help()
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))

