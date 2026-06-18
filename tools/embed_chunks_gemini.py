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

Modèle : par défaut ``text-embedding-004`` (= modèle de la table actuelle, cf.
maestro-platform/core/model_config.py). Si la table devait migrer vers
``gemini-embedding-001``, passer ``--model gemini-embedding-001`` : à 768d ce modèle
n'est PAS L2-normalisé nativement → ce script renormalise (option par défaut).

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

DEFAULT_MODEL = "text-embedding-004"   # modèle de la table maestro_norms_chunks
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


def embed(client, texts, model, task_type, dim=DIM, normalize=None, batch=100):
    """Vecteurs pour `texts`. `normalize` None → auto (gemini-embedding-001 → True)."""
    from google.genai import types
    if normalize is None:
        normalize = model.startswith("gemini-embedding")   # 768d non normalisé nativement
    cfg = {"task_type": task_type}
    if model.startswith("gemini-embedding"):
        cfg["output_dimensionality"] = dim
    out = []
    for i in range(0, len(texts), batch):
        part = texts[i:i + batch]
        resp = client.models.embed_content(
            model=model, contents=part, config=types.EmbedContentConfig(**cfg),
        )
        vecs = [e.values for e in resp.embeddings]
        if normalize:
            vecs = [_l2_normalize(v) for v in vecs]
        out.extend(vecs)
        print(f"  embeddings {min(i + batch, len(texts))}/{len(texts)}", file=sys.stderr)
        time.sleep(0.2)
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


def do_embed_files(client, paths, model, dim) -> int:
    total = 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            chunks = [json.loads(l) for l in f if l.strip()]
        if not chunks:
            print(f"  (vide) {path}", file=sys.stderr)
            continue
        vecs = embed(client, [c["text"] for c in chunks], model, "RETRIEVAL_DOCUMENT", dim=dim)
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
    args = ap.parse_args()
    client = make_client(get_key())
    if args.selftest:
        return do_selftest(client, args.selftest, args.model, args.dim)
    if not args.files:
        ap.error("aucun fichier .chunks.jsonl fourni (ni --selftest)")
    return do_embed_files(client, args.files, args.model, args.dim)


if __name__ == "__main__":
    raise SystemExit(main())
