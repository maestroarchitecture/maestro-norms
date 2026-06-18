#!/usr/bin/env python3
"""PDF → Markdown structuré : format-pivot pour consultation interne + ingestion RAG.

Reconstruit la hiérarchie de titres à partir du **sommaire embarqué** du PDF
(signets/outline) et récupère le corps page par page via `pdftotext` (poppler).
Produit un `.md` navigable (titres `#`/`##`/`###`) avec un front-matter YAML issu
du `manifest.json` (titre, source, SHA-256, licence).

Ce `.md` est la SOURCE unique :
  • consultation humaine → recherche plein-texte (0 token LLM) ;
  • ingestion agent      → `chunk_md.py` (chunks par section) → embeddings.

Le LLM ne consomme JAMAIS ce fichier en entier.

Pré-requis : poppler-utils (`pdftotext`) + `pypdf`.
Usage :
    python3 tools/pdf_to_md.py corpus/rage/<fichier>.pdf [--out index/sample]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter

import pypdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBJ_REPL = "￼"  # glyphe « objet de remplacement » parasite des signets


def load_manifest() -> dict:
    for name in ("manifest.json", "manifest-rage.json"):
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                m = json.load(f)
            for e in m.get("files", []):
                yield_path = e.get("path")
                if yield_path:
                    LOAD_CACHE[yield_path] = e
    return LOAD_CACHE


LOAD_CACHE: dict = {}


def clean_title(t: str) -> str:
    t = t.replace(OBJ_REPL, " ").replace("•", " ")
    t = re.sub(r"\s+", " ", t).strip(" .•\t")
    return t


def outline_headings(reader: pypdf.PdfReader):
    """→ liste ordonnée de (depth, titre_nettoyé, page0)."""
    out = []

    def walk(node, depth=0):
        for item in node:
            if isinstance(item, list):
                walk(item, depth + 1)
            else:
                try:
                    pg = reader.get_destination_page_number(item)
                except Exception:
                    pg = None
                title = clean_title(getattr(item, "title", "") or "")
                if title and pg is not None:
                    out.append((depth, title, pg))

    try:
        walk(reader.outline)
    except Exception as exc:  # pas de sommaire → on échoue proprement
        print(f"  ! pas de sommaire exploitable: {exc}", file=sys.stderr)
    return out


def pages_text(path: str):
    """Texte par page (ordre de lecture). Sépare sur le saut de page \\f."""
    r = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", path, "-"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    raw = r.stdout.decode("utf-8", "replace")
    return raw.split("\x0c")


def boilerplate_lines(pages) -> set:
    """En-têtes/pieds de page récurrents → à retirer (lignes courtes répétées)."""
    c = Counter()
    for pg in pages:
        for ln in {l.strip() for l in pg.splitlines() if l.strip()}:
            c[ln] += 1
    thresh = max(3, int(0.30 * len(pages)))
    return {ln for ln, n in c.items() if n >= thresh and len(ln) < 120}


def clean_body(text: str, boiler: set) -> str:
    keep = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s in boiler:
            continue
        if re.fullmatch(r"\d{1,3}", s):  # numéro de page isolé
            continue
        keep.append(re.sub(r"[ \t]+", " ", ln.rstrip()))
    out = "\n".join(keep)
    return re.sub(r"\n{3,}", "\n\n", out).strip()


def build_markdown(path: str, meta: dict) -> str:
    reader = pypdf.PdfReader(path)
    heads = outline_headings(reader)
    pages = pages_text(path)
    boiler = boilerplate_lines(pages)

    meta = meta or {}
    # Tolère les deux schémas de manifest (AQC: source_url/site/title ;
    # RAGE: url_source/lot/dtu_refs, sans titre).
    title = meta.get("title") or meta.get("basename") or os.path.basename(path)
    url = meta.get("source_url") or meta.get("url_source") or ""
    site = meta.get("site", "")
    sha = meta.get("sha256", "")
    date = meta.get("source_date", "")
    lot = meta.get("lot", "")
    dtu_refs = meta.get("dtu_refs") or []

    fm = [
        "---",
        f'title: "{title}"',
        f"source_url: {url}",
        f"site: {site}",
        f"source_date: {date}",
        f"doc_sha256: {sha}",
        f"lot: {lot}".rstrip(),
        f"dtu_refs: [{', '.join(dtu_refs)}]" if dtu_refs else "dtu_refs: []",
        "licence: RAGE/PACTE/PROFEEL — libre de diffusion (plein texte autorisé)",
        "usage: consultation interne + ingestion RAG (NE PAS injecter en entier au LLM)",
        "---",
        "",
        f"# {title}",
        "",
    ]
    body = ["\n".join(fm)]

    if not heads:
        # Pas de sommaire → corps brut nettoyé (toujours utilisable).
        body.append(clean_body("\n\f".join(pages), boiler))
        return "\n".join(body)

    # Assigne à chaque titre les pages [page_i, page_{i+1}).
    for i, (depth, htitle, pg) in enumerate(heads):
        next_pg = heads[i + 1][2] if i + 1 < len(heads) else len(pages)
        # Même page que le titre suivant → on évite de dupliquer : corps vide,
        # le texte ira au dernier titre de la page.
        span = pages[pg:next_pg] if next_pg > pg else []
        sect = clean_body("\n".join(span), boiler)
        level = min(depth + 2, 6)  # # réservé au titre du doc
        body.append(f"\n{'#' * level} {htitle}\n")
        if sect:
            body.append(sect)
    return "\n".join(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="chemin du PDF (relatif au repo)")
    ap.add_argument("--out", default=os.path.join(ROOT, "index", "sample"))
    args = ap.parse_args()

    load_manifest()
    rel = os.path.relpath(os.path.abspath(args.pdf), ROOT)
    meta = LOAD_CACHE.get(rel) or LOAD_CACHE.get(args.pdf) or {}
    if not meta:
        print(f"  ! pas de métadonnées manifest pour {rel} (front-matter minimal)",
              file=sys.stderr)

    md = build_markdown(args.pdf, meta)
    os.makedirs(args.out, exist_ok=True)
    slug = os.path.splitext(os.path.basename(args.pdf))[0]
    dest = os.path.join(args.out, slug + ".md")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(md + "\n")

    n_head = md.count("\n##")
    print(f"✓ {dest}")
    print(f"  {len(md):,} caractères · {n_head} sections · "
          f"front-matter {'manifest' if meta else 'minimal'}")


if __name__ == "__main__":
    main()
