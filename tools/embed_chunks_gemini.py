#!/usr/bin/env python3
"""Embeddings Gemini des chunks (étape key-gated de la ré-ingestion section-aware).

Découplé du store : produit les vecteurs ; l'écriture DB est pilotée séparément
(MCP Supabase ou tools/embed_and_load.py). Sert deux usages :

1) **Auto-test de modèle** (`--selftest fichier.json`) — AVANT toute ré-ingestion,
   on vérifie que le modèle choisi reproduit un vecteur DÉJÀ stocké dans
   ``maestro_norms_chunks`` (cosinus ≥ 0.999). Indispensable : ré-embedder dans un
   AUTRE espace vectoriel que les 4 049 chunks existants dégraderait le retrieval.
   Le fichier JSON est une liste ``[{"text": "...", "stored_embedding": [..768..]}]``
   (extraite de la table). Sortie : cosinus par échantillon + verdict.

2) **Embeddings de production** (mode par défaut) — lit des ``*.chunks.jsonl``
   (sortie de chunk_md.py) et écrit ``<entrée>.emb.jsonl`` (mêmes champs + champ
   ``embedding``: liste de 768 float).

⚠️ GEMINI_API_KEY (ou GOOGLE_API_KEY) requis.

Modèle : par défaut ``gemini-embedding-001`` (dim 768, task RETRIEVAL_DOCUMENT) —
c'est l'espace vectoriel RÉEL de la table ``maestro_norms_chunks``, PROUVÉ par
l'auto-test cosinus (cf. RUNBOOK §3 ; ``text-embedding-004`` répond désormais 404
NOT_FOUND, retiré par Google). À 768d ce modèle n'est PAS L2-normalisé nativement
→ ce script renormalise (option par défaut). NB : ``model_config.py:43`` de la
plateforme déclare encore ``text-embedding-004`` côté CONFIG, mais les vecteurs en
base sont bien gemini-embedding-001 — la source de vérité est l'auto-test §3.

Exemples :
    # 1) auto-test du modèle (récupérer probes via MCP/SQL au préalable)
    GEMINI_API_KEY=... python3 tools/embed_chunks_gemini.py --selftest probes.json

    # 2) embeddings des 9 RAGE section-aware
    GEMINI_API_KEY=... python3 tools/embed_chunks_gemini.py index/rage/*.chunks.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

DEFAULT_MODEL = "gemini-embedding-001"   # espace vectoriel réel de maestro_norms_chunks (auto-test §3)
DIM = 768


def get_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("✗ GEMINI_API_KEY (ou GOOGLE_API_KEY) manquant.")
    return key


def make_client(key):
    from google import genai
    return genai.Client(api_key=key)


def _l2_normalize(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def embed(client, texts, model, task_type, dim=DIM, normalize=None,
          batch=100, sleep=0.2, max_retries=6):
    """Vecteurs pour `texts`. `normalize` None → auto (gemini-embedding-001 → True).

    Robuste au rate-limit : sur 429 RESOURCE_EXHAUSTED, backoff puis retry (utile
    sur le free tier Gemini où le débit jeton/min est bas).
    """
    from google.genai import types
    try:
        from google.genai import errors as genai_errors
    except Exception:  # pragma: no cover
        genai_errors = None
    if normalize is None:
        normalize = model.startswith("gemini-embedding")   # 768d non normalisé nativement
    cfg = {"task_type": task_type}
    if model.startswith("gemini-embedding"):
        cfg["output_dimensionality"] = dim
    out = []
    for i in range(0, len(texts), batch):
        part = texts[i:i + batch]
        for attempt in range(max_retries + 1):
            try:
                resp = client.models.embed_content(
                    model=model, contents=part, config=types.EmbedContentConfig(**cfg),
                )
                break
            except Exception as e:  # 429 / quota → backoff + retry
                code = getattr(e, "status_code", None) or getattr(e, "code", None)
                is_429 = code == 429 or "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e)
                if is_429 and attempt < max_retries:
                    wait = min(60, 15 * (attempt + 1))
                    print(f"  429 quota — pause {wait}s puis retry "
                          f"(essai {attempt + 1}/{max_retries})", file=sys.stderr)
                    time.sleep(wait)
                    continue
                raise
        vecs = [e.values for e in resp.embeddings]
        if normalize:
            vecs = [_l2_normalize(v) for v in vecs]
        out.extend(vecs)
        print(f"  embeddings {min(i + batch, len(texts))}/{len(texts)}", file=sys.stderr)
        time.sleep(sleep)
    return out


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def do_selftest(client, path, model, dim) -> int:
    """Vérifie que `model` reproduit des vecteurs déjà stockés (cosinus ≥ 0.999)."""
    with open(path, encoding="utf-8") as f:
        probes = json.load(f)
    texts = [p["text"] for p in probes]
    # tâche RETRIEVAL_DOCUMENT : les chunks ont été indexés ainsi
    vecs = embed(client, texts, model, "RETRIEVAL_DOCUMENT", dim=dim)
    worst = 1.0
    print(f"\nAuto-test modèle « {model} » (dim {dim}) sur {len(probes)} échantillon(s) :")
    for i, (p, v) in enumerate(zip(probes, vecs)):
        cos = _cosine(v, p["stored_embedding"])
        worst = min(worst, cos)
        tag = p.get("tag", f"#{i}")
        flag = "OK" if cos >= 0.999 else ("~" if cos >= 0.95 else "✗")
        print(f"  [{flag}] {tag:<24} cosinus = {cos:.5f}")
    ok = worst >= 0.999
    print(f"\n{'✓ MÊME espace vectoriel' if ok else '✗ ESPACE DIFFÉRENT — NE PAS ré-embedder'} "
          f"(pire cosinus = {worst:.5f}).")
    if not ok:
        print("  → le modèle/config ne correspond pas à la table. Re-tester un autre modèle\n"
              "    (text-embedding-004 vs gemini-embedding-001) ou escalader (ré-embed total).",
              file=sys.stderr)
    return 0 if ok else 2


def do_embed_files(client, paths, model, dim, batch=100, sleep=0.2, max_retries=6) -> int:
    total = 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            chunks = [json.loads(l) for l in f if l.strip()]
        if not chunks:
            print(f"  (vide) {path}", file=sys.stderr)
            continue
        # idempotent : si le .emb.jsonl complet existe déjà, on saute (reprise sûre)
        out_existing = (os.path.splitext(path)[0][:-7] if os.path.splitext(path)[0].endswith(".chunks")
                        else os.path.splitext(path)[0]) + ".emb.jsonl"
        if os.path.exists(out_existing):
            try:
                done = sum(1 for _ in open(out_existing))
            except OSError:
                done = -1
            if done == len(chunks):
                print(f"✓ {out_existing}  (déjà fait, {done} vecteurs — saute)")
                total += done
                continue
        vecs = embed(client, [c["text"] for c in chunks], model, "RETRIEVAL_DOCUMENT",
                     dim=dim, batch=batch, sleep=sleep, max_retries=max_retries)
        out = os.path.splitext(path)[0]
        out = (out[:-7] if out.endswith(".chunks") else out) + ".emb.jsonl"
        with open(out, "w", encoding="utf-8") as w:
            for c, v in zip(chunks, vecs):
                c["embedding"] = v
                w.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"✓ {out}  ({len(chunks)} vecteurs, dim {len(vecs[0])})")
        total += len(chunks)
    print(f"\n✓ {total} chunks embeddés.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="*.chunks.jsonl à embedder")
    ap.add_argument("--selftest", help="JSON [{text, stored_embedding[, tag]}] — vérif espace vectoriel")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--dim", type=int, default=DIM)
    ap.add_argument("--batch", type=int, default=100, help="contenus par requête embed (baisser si 429)")
    ap.add_argument("--sleep", type=float, default=0.2, help="pause (s) entre requêtes")
    ap.add_argument("--max-retries", type=int, default=6, help="retries sur 429 (backoff)")
    args = ap.parse_args()
    client = make_client(get_key())
    if args.selftest:
        return do_selftest(client, args.selftest, args.model, args.dim)
    if not args.files:
        ap.error("aucun fichier .chunks.jsonl fourni (ni --selftest)")
    return do_embed_files(client, args.files, args.model, args.dim,
                          batch=args.batch, sleep=args.sleep, max_retries=args.max_retries)


if __name__ == "__main__":
    raise SystemExit(main())
