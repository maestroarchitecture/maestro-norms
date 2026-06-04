#!/usr/bin/env python3
"""Extraction + chunking du corpus PDF → index/chunks.jsonl (store-agnostique).

Pré-requis : poppler-utils (pdftotext). Lit manifest.json pour les métadonnées
(titre, URL source, site, SHA-256) et produit des chunks prêts à être plongés
(embeddings) par tools/embed_and_load.py.

Usage:
    python3 tools/extract_chunks.py [--words 300 --overlap 50 --out index/chunks.jsonl]
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORD_RE = re.compile(r"[0-9A-Za-zÀ-ÿ]{2,}")

def load_manifest():
    with open(os.path.join(ROOT, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    return {e["path"]: e for e in m["files"]}

def pdftotext(path: str) -> str:
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-nopgbrk", path, "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return r.stdout.decode("utf-8", "replace")

def clean(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def wordlike_ratio(text: str) -> float:
    toks = text.split()
    if not toks:
        return 0.0
    good = sum(1 for t in toks if WORD_RE.search(t))
    return good / len(toks)

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
    ap.add_argument("--words", type=int, default=300, help="mots par chunk")
    ap.add_argument("--overlap", type=int, default=50, help="recouvrement (mots)")
    ap.add_argument("--out", default=os.path.join(ROOT, "index", "chunks.jsonl"))
    ap.add_argument("--min-quality", type=float, default=0.45,
                    help="ratio mots-valides en dessous duquel un doc est marqué low_quality")
    args = ap.parse_args()

    meta = load_manifest()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    n_docs = n_chunks = n_lowq = n_empty = 0
    total_chars = 0
    with open(args.out, "w", encoding="utf-8") as out:
        for path in sorted(meta):
            abspath = os.path.join(ROOT, path)
            if not os.path.exists(abspath):
                print(f"  ! manquant: {path}", file=sys.stderr); continue
            n_docs += 1
            raw = clean(pdftotext(abspath))
            q = wordlike_ratio(raw)
            low = q < args.min_quality
            if not raw:
                n_empty += 1
            if low:
                n_lowq += 1
            e = meta[path]
            doc_id = e["sha256"][:16]
            for idx, (woff, text) in enumerate(chunk_words(raw, args.words, args.overlap)):
                cid = hashlib.sha256(f"{e['sha256']}:{idx}".encode()).hexdigest()[:24]
                rec = {
                    "id": cid,
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "word_offset": woff,
                    "n_chars": len(text),
                    "text": text,
                    "doc_path": path,
                    "title": e.get("title"),
                    "site": e.get("site"),
                    "source_url": e.get("source_url"),
                    "source_date": e.get("source_date"),
                    "doc_sha256": e["sha256"],
                    "extract_quality": round(q, 3),
                    "low_quality": low,
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_chunks += 1
                total_chars += len(text)

    stats = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "params": {"words": args.words, "overlap": args.overlap,
                   "min_quality": args.min_quality},
        "docs": n_docs, "chunks": n_chunks, "chars": total_chars,
        "docs_empty_text": n_empty, "docs_low_quality": n_lowq,
        "embedding_model_target": "text-embedding-004 (Gemini, dim 768)",
        "out": os.path.relpath(args.out, ROOT),
    }
    with open(os.path.join(ROOT, "index", "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=1)
    print(json.dumps(stats, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
