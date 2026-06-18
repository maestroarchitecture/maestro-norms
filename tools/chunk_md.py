#!/usr/bin/env python3
"""Markdown structuré → chunks par SECTION (prêts pour embed_and_load.py).

Contrairement à `extract_chunks.py` (fenêtres de 300 mots à l'aveugle sur tout le
PDF), ce découpage respecte les **frontières de section** du `.md` produit par
`pdf_to_md.py` : un chunk ne mélange jamais deux sections, et porte le fil
d'Ariane des titres (`section_path`) + `lot` / `dtu_refs` du front-matter.

Bénéfices :
  • retrieval plus précis (chunk = une sous-section cohérente) ;
  • citation exacte possible (« §7.2 Entretien… ») ;
  • filtrage déterministe par `lot` avant même la recherche sémantique.

Sortie : JSONL aux champs attendus par `embed_and_load.py` (id, doc_id, …,
chunk_index, text) + extras (`section_path`, `section_title`, `lot`, `dtu_refs`)
ignorés par l'INSERT Supabase → 100 % rétro-compatible.

Usage :
    python3 tools/chunk_md.py index/sample/<doc>.md [--words 300 --overlap 50 \
        --out index/sample/<doc>.chunks.jsonl]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def parse_front_matter(text: str):
    """→ (dict front-matter, corps sans le front-matter)."""
    fm: dict = {}
    if not text.startswith("---"):
        return fm, text
    end = text.find("\n---", 3)
    if end == -1:
        return fm, text
    block = text[3:end].strip("\n")
    for line in block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, text[end + 4:].lstrip("\n")


def iter_sections(body: str):
    """Itère (level, title, breadcrumb_path, section_text)."""
    lines = body.splitlines()
    stack: list[tuple[int, str]] = []  # (level, title) ancêtres
    cur_title, cur_level, buf = None, 0, []

    def path():
        # Exclut le titre de document (niveau 1) : redondant avec `title`/`doc_id`.
        return " > ".join(t for lvl, t in stack if lvl >= 2)

    for ln in lines:
        m = HEAD_RE.match(ln)
        if m:
            if cur_title is not None or buf:
                yield cur_level, cur_title, path(), "\n".join(buf).strip()
            buf = []
            level = len(m.group(1))
            title = m.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            cur_title, cur_level = title, level
        else:
            buf.append(ln)
    if cur_title is not None or buf:
        yield cur_level, cur_title, path(), "\n".join(buf).strip()


def chunk_words(text: str, size: int, overlap: int):
    words = text.split()
    if not words:
        return
    step = max(1, size - overlap)
    for i in range(0, len(words), step):
        piece = words[i:i + size]
        if piece:
            yield i, " ".join(piece)
        if i + size >= len(words):
            break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md", help="fichier .md produit par pdf_to_md.py")
    ap.add_argument("--words", type=int, default=300)
    ap.add_argument("--overlap", type=int, default=50)
    ap.add_argument("--out", default=None)
    ap.add_argument("--min-words", type=int, default=12,
                    help="ignore les sections plus courtes (titres orphelins)")
    args = ap.parse_args()

    with open(args.md, encoding="utf-8") as f:
        fm, body = parse_front_matter(f.read())

    doc_sha = fm.get("doc_sha256", "")
    doc_id = doc_sha[:16]
    doc_title = fm.get("title", os.path.basename(args.md)).strip('"')
    lot = fm.get("lot", "")
    dtu = fm.get("dtu_refs", "[]")
    doc_path = fm.get("doc_path", "")  # rempli au besoin par l'appelant
    # Garde-fou licence (cf. RUNBOOK-DTU-pivot §5) : un DTU/NF payant porte
    # `licence: dtu_payant` en front-matter. On le propage sur chaque chunk pour
    # que la couche de restitution exclue leur `text` de toute sortie client
    # (retrieval interne → l'agent cite la réf, ne recopie pas la prose).
    licence = fm.get("licence", "")

    out = args.out or os.path.splitext(args.md)[0] + ".chunks.jsonl"
    n = 0
    with open(out, "w", encoding="utf-8") as w:
        for level, title, breadcrumb, sect in iter_sections(body):
            if len(sect.split()) < args.min_words:
                continue
            for woff, piece in chunk_words(sect, args.words, args.overlap):
                cid = hashlib.sha256(f"{doc_sha}:{n}".encode()).hexdigest()[:24]
                rec = {
                    "id": cid,
                    "doc_id": doc_id,
                    "chunk_index": n,
                    "doc_path": doc_path,
                    "title": doc_title,
                    "site": fm.get("site", ""),
                    "source_url": fm.get("source_url", ""),
                    "source_date": fm.get("source_date", ""),
                    "doc_sha256": doc_sha,
                    # --- extras section-aware (ignorés par l'INSERT Supabase) ---
                    "section_title": title,
                    "section_path": breadcrumb,
                    "lot": lot,
                    "dtu_refs": dtu,
                    "licence": licence,  # "" (libre) ou "dtu_payant" (citation seule)
                    "n_chars": len(piece),
                    "text": f"[{breadcrumb}]\n{piece}" if breadcrumb else piece,
                }
                w.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1

    print(f"✓ {out}")
    print(f"  {n} chunks · lot={lot or '—'} · dtu_refs={dtu} · "
          f"mots/chunk≈{args.words} (overlap {args.overlap})")


if __name__ == "__main__":
    main()
