# Ingestion RAG du corpus

Pipeline en **2 étapes**, store-agnostique. L'étape 1 est déjà exécutée et son
résultat (`index/chunks.jsonl`) est versionné. L'étape 2 nécessite une **clé
d'embedding Gemini** et une cible (locale ou Supabase) — à lancer dans un
environnement qui dispose de la clé.

```
PDF (corpus/**) ──[1] extract_chunks.py──▶ index/chunks.jsonl ──[2] embed_and_load.py──▶ index RAG
        │ poppler/pdftotext                  (texte + métadonnées)        │ Gemini text-embedding-004
        └ déjà fait                                                       └ local .npy  OU  Supabase pgvector
```

## Variante recommandée — pivot Markdown *section-aware*

Pour une **consultation interne** (recherche plein-texte, 0 token LLM) **et** une
ingestion plus précise, on passe par un `.md` structuré intermédiaire au lieu du
texte brut. Le `.md` est la **source unique** ; le LLM n'en consomme jamais
l'intégralité (seulement le top-k au retrieval).

```
PDF ──[A] pdf_to_md.py──▶ .md structuré ──[B] chunk_md.py──▶ chunks.jsonl ──▶ embed_and_load.py
     │ sommaire embarqué    (front-matter:           │ découpe par SECTION       (inchangé)
     │ + pdftotext          lot/dtu_refs/source)      │ + breadcrumb + lot
     └ titres #/##/###                                └ compatible INSERT Supabase
```

```bash
# A) PDF → Markdown navigable (front-matter manifest : lot, dtu_refs, source_url, sha256)
python3 tools/pdf_to_md.py corpus/rage/<fichier>.pdf      # → index/sample/<doc>.md

# B) Markdown → chunks par section (respecte les frontières, porte lot + dtu_refs)
python3 tools/chunk_md.py index/sample/<doc>.md           # → index/sample/<doc>.chunks.jsonl

# C) Embeddings + chargement : identique à l'étape 2 ci-dessous (mêmes champs)
python3 tools/embed_and_load.py --target supabase --chunks index/sample/<doc>.chunks.jsonl
```

**Pourquoi** vs `extract_chunks.py` (fenêtres de 300 mots à l'aveugle) :
- chunk = une sous-section cohérente → retrieval plus précis, citation exacte (`§7.2`) ;
- chaque chunk porte `lot` + `dtu_refs` → **filtrage déterministe avant** la recherche
  sémantique (0 token) ;
- le `.md` sert aussi de doc interne navigable (humain) — utile surtout pour les **DTU**
  payants (lecture interne sous licence, jamais de verbatim côté client).

Exemple versionné : `index/sample/recommandation-pro-rage-appareils-…-granules-…md`
(+ `.chunks.jsonl`) — Reco Pro RAGE, libre de droits.

## Étape 1 — Extraction + chunking (faite)

```bash
sudo apt-get install -y poppler-utils      # fournit pdftotext
python3 tools/extract_chunks.py            # → index/chunks.jsonl + index/stats.json
```

État actuel (`index/stats.json`) : **348 docs → 3 311 chunks** (~300 mots,
recouvrement 50), modèle cible `text-embedding-004` (dim 768).
Chaque chunk porte : `id`, `doc_id`, `chunk_index`, `text`, `title`,
`site`, `source_url`, `source_date`, `doc_sha256`, `extract_quality`.

> ⚠️ 1 document sans texte extractible (PDF image) : `Fiche-Attestations-VDI-PE01-Portiers-Electroniques-AQC.pdf`
> → nécessiterait de l'**OCR** (hors périmètre). 1 document marqué `low_quality`.

## Étape 2 — Embeddings + chargement (à lancer)

```bash
pip install -r tools/requirements.txt
export GEMINI_API_KEY=...        # ou GOOGLE_API_KEY

# A) Index local portable
python3 tools/embed_and_load.py --target local
#   → index/embeddings.npy (3311×768 float32) + index/embeddings_ids.json

# B) Supabase / Postgres + pgvector
export DATABASE_URL=postgres://...    # ou SUPABASE_DB_URL
python3 tools/embed_and_load.py --target supabase
#   → CREATE EXTENSION vector + table maestro_norms_chunks (HNSW cosine), upsert idempotent
```

### Schéma Supabase (créé automatiquement par le script)

Table `maestro_norms_chunks(id pk, doc_id, doc_path, title, site, source_url,
source_date, doc_sha256, chunk_index, text, embedding vector(768))` +
index HNSW `vector_cosine_ops`. L'upsert est idempotent (`ON CONFLICT (id)`).

## Recherche (démo)

```bash
python3 tools/embed_and_load.py --target local \
    --query "ventilation VMC double flux réglementation" --k 5
```

## Notes

- **Modèle** : `text-embedding-004` (Gemini), aligné sur
  `maestro-platform/packages/maestro/core/model_config.py` et réutilisable via
  `gemini_client.embed_content_async`.
- `task_type` = `RETRIEVAL_DOCUMENT` à l'indexation, `RETRIEVAL_QUERY` à la
  requête.
- Idempotence : l'`id` de chunk = `sha256(doc_sha256:chunk_index)` → ré-ingestion
  sûre.
