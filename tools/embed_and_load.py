#!/usr/bin/env python3
"""Embeddings + chargement de l'index RAG (Gemini text-embedding-004).

Étape 2 de l'ingestion (l'étape 1 = tools/extract_chunks.py → index/chunks.jsonl).
Store-agnostique : cible `local` (artefact portable) ou `supabase` (pgvector).

⚠️ Nécessite une clé d'embedding : GEMINI_API_KEY (ou GOOGLE_API_KEY).
   Modèle aligné sur maestro-platform : MODEL_NAME_EMBEDDING = "text-embedding-004"
   (dimension 768).

Exemples:
    # 1) Index local portable (index/embeddings.npy + index/embeddings_ids.json)
    GEMINI_API_KEY=... python3 tools/embed_and_load.py --target local

    # 2) Supabase / Postgres + pgvector
    GEMINI_API_KEY=... DATABASE_URL=postgres://... \
        python3 tools/embed_and_load.py --target supabase

    # 3) Recherche de démonstration (après indexation)
    GEMINI_API_KEY=... python3 tools/embed_and_load.py --target local \
        --query "ventilation VMC double flux réglementation" --k 5
"""
from __future__ import annotations
import argparse, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = "text-embedding-004"          # cf. maestro-platform/packages/maestro/core/model_config.py
DIM = 768
TABLE = "maestro_norms_chunks"

DDL = f"""
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS {TABLE} (
    id           text PRIMARY KEY,
    doc_id       text,
    doc_path     text,
    title        text,
    site         text,
    source_url   text,
    source_date  text,
    doc_sha256   text,
    chunk_index  int,
    text         text,
    embedding    vector({DIM})
);
CREATE INDEX IF NOT EXISTS {TABLE}_embedding_idx
    ON {TABLE} USING hnsw (embedding vector_cosine_ops);
"""

# --------------------------------------------------------------------------- #
def get_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("✗ GEMINI_API_KEY (ou GOOGLE_API_KEY) manquant.")
    return key

def make_client(key):
    from google import genai
    return genai.Client(api_key=key)

def embed(client, texts, task_type, batch=100):
    """Retourne une liste de vecteurs (list[float]) pour `texts`."""
    from google.genai import types
    out = []
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        resp = client.models.embed_content(
            model=MODEL, contents=chunk,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        out.extend([e.values for e in resp.embeddings])
        print(f"  embeddings {min(i+batch, len(texts))}/{len(texts)}", file=sys.stderr)
        time.sleep(0.2)
    return out

def load_chunks(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

# --------------------------------------------------------------------------- #
def do_local(client, chunks, args):
    import numpy as np
    vecs = embed(client, [c["text"] for c in chunks], "RETRIEVAL_DOCUMENT")
    arr = np.asarray(vecs, dtype="float32")
    np.save(os.path.join(ROOT, "index", "embeddings.npy"), arr)
    with open(os.path.join(ROOT, "index", "embeddings_ids.json"), "w", encoding="utf-8") as f:
        json.dump([c["id"] for c in chunks], f)
    print(f"✓ index local : {arr.shape} → index/embeddings.npy")

def do_supabase(client, chunks, args):
    import psycopg
    from pgvector.psycopg import register_vector
    db = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL")
    if not db:
        sys.exit("✗ DATABASE_URL (ou SUPABASE_DB_URL) manquant pour --target supabase.")
    vecs = embed(client, [c["text"] for c in chunks], "RETRIEVAL_DOCUMENT")
    with psycopg.connect(db, autocommit=True) as conn:
        conn.execute(DDL)
        register_vector(conn)
        rows = [(c["id"], c["doc_id"], c["doc_path"], c.get("title"), c.get("site"),
                 c.get("source_url"), c.get("source_date"), c["doc_sha256"],
                 c["chunk_index"], c["text"], v) for c, v in zip(chunks, vecs)]
        with conn.cursor() as cur:
            cur.executemany(
                f"""INSERT INTO {TABLE}
                    (id,doc_id,doc_path,title,site,source_url,source_date,
                     doc_sha256,chunk_index,text,embedding)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (id) DO UPDATE SET
                      text=EXCLUDED.text, embedding=EXCLUDED.embedding""", rows)
    print(f"✓ {len(rows)} chunks upsertés dans {TABLE} (pgvector)")

def do_query(client, args):
    qv = embed(client, [args.query], "RETRIEVAL_QUERY")[0]
    if args.target == "local":
        import numpy as np
        arr = np.load(os.path.join(ROOT, "index", "embeddings.npy"))
        ids = json.load(open(os.path.join(ROOT, "index", "embeddings_ids.json")))
        chunks = {c["id"]: c for c in load_chunks(os.path.join(ROOT, "index", "chunks.jsonl"))}
        q = np.asarray(qv, dtype="float32")
        sims = arr @ q / (np.linalg.norm(arr, axis=1) * np.linalg.norm(q) + 1e-9)
        for rank in sims.argsort()[::-1][:args.k]:
            c = chunks[ids[rank]]
            print(f"\n[{sims[rank]:.3f}] {c['title']}\n  {c['source_url']}\n  {c['text'][:200]}…")
    else:
        import psycopg
        from pgvector.psycopg import register_vector
        db = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL")
        with psycopg.connect(db) as conn:
            register_vector(conn)
            cur = conn.execute(
                f"""SELECT title, source_url, text, 1-(embedding<=>%s) AS score
                    FROM {TABLE} ORDER BY embedding<=>%s LIMIT %s""", (qv, qv, args.k))
            for title, url, text, score in cur.fetchall():
                print(f"\n[{score:.3f}] {title}\n  {url}\n  {text[:200]}…")

# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["local", "supabase"], default="local")
    ap.add_argument("--chunks", default=os.path.join(ROOT, "index", "chunks.jsonl"))
    ap.add_argument("--query", help="si fourni : recherche au lieu d'indexer")
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    client = make_client(get_key())
    if args.query:
        do_query(client, args); return
    chunks = load_chunks(args.chunks)
    print(f"{len(chunks)} chunks → embeddings ({MODEL}, dim {DIM}) → {args.target}")
    (do_local if args.target == "local" else do_supabase)(client, chunks, args)

if __name__ == "__main__":
    main()
