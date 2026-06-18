#!/usr/bin/env python3
"""Charge des chunks DÉJÀ embeddés (*.emb.jsonl) dans `maestro_norms_chunks`
(pgvector), de façon idempotente PAR DOCUMENT :

  1. UPSERT de tous les chunks du doc (ON CONFLICT (id) DO UPDATE) ;
  2. DELETE de la queue orpheline (chunk_index >= nb nouveaux chunks du doc).

→ jamais de fenêtre à zéro chunk ; remplace proprement l'ancien découpage par le
nouveau (section-aware), même quand le nouveau a moins de chunks que l'ancien.

NE RÉ-EMBEDDE PAS : lit les vecteurs du .emb.jsonl → l'espace vectoriel est
garanti = celui qui a produit ces vecteurs (ici gemini-embedding-001 768d, validé
par l'auto-test cosinus, cf. RUNBOOK §3). Donc PAS besoin de GEMINI_API_KEY.

Requiert une connexion Postgres : SUPABASE_DB_URL (ou DATABASE_URL).
La table n'est PAS créée ici (on cible une table existante en prod).

Usage :
    # validation hors-ligne (dims/continuité) sans toucher la base :
    python3 tools/load_emb_supabase.py --validate index/rage/*.emb.jsonl
    # comptes avant (lecture seule) :
    SUPABASE_DB_URL=postgres://... python3 tools/load_emb_supabase.py --check index/rage/*.emb.jsonl
    # chargement réel (UPSERT + DELETE-queue, transaction unique) :
    SUPABASE_DB_URL=postgres://... python3 tools/load_emb_supabase.py index/rage/*.emb.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

TABLE = "maestro_norms_chunks"
COLS = ["id", "doc_id", "doc_path", "title", "site", "source_url",
        "source_date", "doc_sha256", "chunk_index", "text", "embedding"]


def load(paths):
    docs: dict[str, list] = defaultdict(list)
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    docs[r["doc_sha256"]].append(r)
    for sha in docs:
        docs[sha].sort(key=lambda r: r["chunk_index"])
    return docs


def validate(docs) -> None:
    """Invariants avant tout écrit : dim 768, chunk_index contigus 0..n-1."""
    total = 0
    for sha, rows in docs.items():
        dims = {len(r["embedding"]) for r in rows}
        idx = [r["chunk_index"] for r in rows]
        if dims != {768}:
            sys.exit(f"✗ {sha[:12]} : dimensions != 768 ({dims})")
        if idx != list(range(len(rows))):
            sys.exit(f"✗ {sha[:12]} : chunk_index non contigus 0..{len(rows)-1}")
        total += len(rows)
        print(f"  {sha[:12]}  n={len(rows):>3}  idx 0..{len(rows)-1}  dim=768 ✓")
    print(f"  → {len(docs)} doc(s), {total} chunks, invariants OK.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="*.emb.jsonl pré-embeddés")
    ap.add_argument("--validate", action="store_true", help="invariants hors-ligne, aucune connexion")
    ap.add_argument("--check", action="store_true", help="connexion lecture seule : comptes avant")
    args = ap.parse_args()

    docs = load(args.files)
    print(f"{len(docs)} document(s), {sum(len(v) for v in docs.values())} chunks pré-embeddés.")
    validate(docs)
    if args.validate:
        return 0

    db = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not db:
        sys.exit("✗ SUPABASE_DB_URL (ou DATABASE_URL) manquant — requis pour lire/écrire la base.")

    import psycopg
    from pgvector.psycopg import register_vector

    with psycopg.connect(db, autocommit=False) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            for sha, rows in docs.items():
                cur.execute(f"SELECT count(*), min(chunk_index), max(chunk_index) "
                            f"FROM {TABLE} WHERE doc_sha256=%s", (sha,))
                n, lo, hi = cur.fetchone()
                print(f"  [{sha[:12]}] avant: n={n} (idx {lo}..{hi}) → attendu après: {len(rows)} (idx 0..{len(rows)-1})")
        if args.check:
            print("--check : aucune écriture effectuée.")
            return 0

        with conn.cursor() as cur:
            for sha, rows in docs.items():
                vals = [tuple(r.get(c) for c in COLS) for r in rows]
                placeholders = ",".join(["%s"] * len(COLS))
                setclause = ", ".join(f"{c}=EXCLUDED.{c}" for c in COLS if c != "id")
                cur.executemany(
                    f"INSERT INTO {TABLE} ({','.join(COLS)}) VALUES ({placeholders}) "
                    f"ON CONFLICT (id) DO UPDATE SET {setclause}", vals)
                cur.execute(f"DELETE FROM {TABLE} WHERE doc_sha256=%s AND chunk_index >= %s",
                            (sha, len(rows)))
            conn.commit()

        ok_all = True
        with conn.cursor() as cur:
            for sha, rows in docs.items():
                cur.execute(f"SELECT count(*), max(chunk_index) FROM {TABLE} WHERE doc_sha256=%s", (sha,))
                n, hi = cur.fetchone()
                ok = (n == len(rows) and hi == len(rows) - 1)
                ok_all &= ok
                print(f"  [{'OK' if ok else '✗'}] {sha[:12]} après: n={n} (max idx {hi}, attendu {len(rows)-1})")
        print("✓ chargement idempotent terminé." if ok_all else "⚠️ incohérence — inspecter.")
        return 0 if ok_all else 2


if __name__ == "__main__":
    raise SystemExit(main())
