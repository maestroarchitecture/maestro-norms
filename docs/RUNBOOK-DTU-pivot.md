# RUNBOOK — Pivot Markdown : ré-ingestion section-aware & DTU sous licence

Procédure opérationnelle réutilisable du pipeline pivot (`pdf_to_md` → `chunk_md`
→ embeddings → Supabase), avec le **garde-fou licence** pour les DTU payants.

Couvre deux usages :
- **Action 1** — ré-ingérer en *section-aware* des PDF **libres** déjà présents
  (les 9 Reco Pro RAGE de `corpus/rage/`).
- **Action 3** — ingérer un **DTU sous licence** (REEF Collection) en *citation
  seule côté client*.

---

## 0. Pré-requis machine (une fois)

```bash
brew install git-lfs poppler          # pdftotext + LFS
git -C maestro-norms lfs install --local
python3 -m pip install pypdf google-genai numpy      # extraction + embeddings
```

Secret nécessaire **uniquement à l'étape embeddings** : `GEMINI_API_KEY`
(jamais committé). Écriture DB : via le **MCP Supabase** (aucun secret DB requis)
ou via `SUPABASE_DB_URL` + `tools/embed_and_load.py`.

> **Modèle d'embedding** : la table `maestro_norms_chunks` est en
> **`gemini-embedding-001`** (768d, `RETRIEVAL_DOCUMENT`) — **prouvé empiriquement**
> par l'auto-test §3 (cosinus 1.00000 / 0.99956). `text-embedding-004` répond
> désormais **404 NOT_FOUND** (retiré par Google) et n'est PLUS l'espace de la
> table, malgré `model_config.py:43` de la plateforme qui le déclare encore côté
> CONFIG (à corriger côté plateforme, PR séparée). **Ré-embedder avec un autre
> modèle = autre espace vectoriel = retrieval dégradé.** Toujours exécuter
> l'auto-test §3 avant d'insérer ; en cas de conflit, la source de vérité est
> l'auto-test cosinus, pas le code de config.

---

## 1. PDF → Markdown structuré (pivot)

```bash
python3 tools/pdf_to_md.py corpus/rage/<fichier>.pdf --out index/rage
```
Front-matter (lot, dtu_refs, source_url, **doc_sha256**) tiré du manifest. Le
`.md` est la **source de consultation interne** (recherche plein-texte, 0 token
LLM) — pour un DTU, c'est ici que la lecture sous licence se matérialise.

## 2. Markdown → chunks par section

```bash
python3 tools/chunk_md.py index/rage/<fichier>.md
```
`id = sha256("{doc_sha256}:{chunk_index}")[:24]` — **même schéma** que l'ancien
chunker à fenêtres ⇒ collision d'ids sur les `chunk_index` communs (cf. §4).

## 3. Auto-test du modèle (OBLIGATOIRE avant insert)

But : prouver que le modèle reproduit un vecteur **déjà stocké** (même espace).

1. Extraire 2 sondes via MCP/SQL (1 RAGE déjà en base + 1 AQC) :
   ```sql
   SELECT text, embedding FROM maestro_norms_chunks
   WHERE doc_sha256='<sha_rage>' AND chunk_index=0;          -- + 1 chunk AQC
   ```
   Écrire `probes.json` : `[{"tag":"rage", "text":"…", "stored_embedding":[…768…]}, …]`.
2. Lancer :
   ```bash
   GEMINI_API_KEY=… python3 tools/embed_chunks_gemini.py --selftest probes.json
   ```
   - **cosinus ≥ 0.999** pour les 2 → même espace, on continue.
   - sinon : tester `--model gemini-embedding-001`. Si toujours non concordant
     pour la sonde RAGE **et** la sonde AQC → **STOP / escalade** (la table
     est dans un modèle indisponible ⇒ ré-embed total des 4 049, hors périmètre
     d'un patch 9 docs).

## 4. Embeddings + remplacement idempotent

```bash
GEMINI_API_KEY=… python3 tools/embed_chunks_gemini.py index/rage/*.chunks.jsonl
#   → index/rage/<doc>.emb.jsonl  (chunks + champ embedding[768])
```

Écriture (par doc, via MCP Supabase — jamais de fenêtre à zéro chunk) :

1. **UPSERT** des nouveaux chunks (`ON CONFLICT (id) DO UPDATE`) → écrase les
   anciens `chunk_index` 0..min, ajoute la queue.
2. **DELETE** de la seule queue orpheline :
   ```sql
   DELETE FROM maestro_norms_chunks
   WHERE doc_sha256 = '<sha>' AND chunk_index >= <nb_nouveaux_chunks>;
   ```
3. **Vérifier** : `SELECT count(*) … GROUP BY doc_sha256` = nb attendu.

> Filet de sécurité : `SELECT … WHERE doc_sha256 IN (…9…)` dumpé en JSONL avant
> toute écriture (reproductible depuis `corpus/`, mais assurance bon marché).

---

## 5. DTU sous licence (Action 3) — garde-fou citation seule

**Déclencheur** : licence **REEF Collection** (CSTB, ~544 €HT) acquise.

Même pipeline §1–§4, **mais** :

| Étape | DTU sous licence |
|---|---|
| `.md` pivot (§1) | **interne uniquement** : lecture sous licence. Stocker hors corpus public si besoin, ne jamais publier le plein texte. |
| chunks / embeddings (§2–§4) | autorisés pour la **recherche interne** (retrieval), pas pour restitution verbatim. |
| Sortie **devis client** | **JAMAIS de verbatim**. Uniquement : la **référence** (`NF DTU 68.3 §x.y`) + une **paraphrase** de l'exigence (cf. étage 0 `dtu_rules.yaml`). |

Règle : *les faits/seuils (un nombre, une condition) ne sont pas protégeables ;
la prose de la clause l'est.* On **cite**, on ne **recopie** pas.

Garde-fous techniques (implémentés) :
- **Stockage gitignoré** : pivot `.md` + chunks d'un DTU payant sous `private/`
  (cf. `.gitignore`) → jamais publié dans ce repo public.
- **Marquage des chunks** : `chunk_md.py` propage le front-matter `licence` sur
  chaque chunk (`licence: dtu_payant` ; les chunks RAGE portent `licence: …libre…`).
  ⚠️ **Flag posé, pas encore appliqué** : la couche de restitution **devra exclure
  le `text`** des chunks `dtu_payant` des sorties client (retrieval interne →
  l'agent cite la réf, ne recopie pas la prose). **TODO plateforme** (PR séparée) :
  implémenter ce consommateur. Aucun risque live tant que rien n'est publié et que
  l'embed/insert reste gated.
- **Front-matter** `usage: consultation interne — NE PAS injecter au LLM en entier`.

> **POC réalisé** (2026-06-18) : `private/dtu/NF-DTU-65.14-P1-1-1.md` (slice borné
> §6/§7 lu dans le Reef « comme un utilisateur », pas d'extraction systématique) →
> `chunk_md.py` → 5 chunks section-aware `lot=04 · licence=dtu_payant`. Étape
> embeddings/insert **gated** sur `GEMINI_API_KEY` (idem Action 1).

Licences (rappel `README.md`) : RAGE/PACTE/PROFEEL = libre diffusion (plein texte
OK) ; **DTU/NF & FFB = citation seule**.
