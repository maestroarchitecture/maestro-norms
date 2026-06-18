# HANDOFF — Session 2026-06-18 — Pivot Markdown & architecture RAG/embeddings

> Reprise dans un autre chat. Le repo se clone à neuf : ce fichier + `CLAUDE.md`
> (chargé automatiquement) suffisent à reprendre. Branche de dev :
> **`claude/trusting-ramanujan-pFULL`**.

## TL;DR

Objectif global **inchangé** : base de justification normative par lot
(RAGE/PACTE/PROFEEL plein texte + DTU/NF en citation) branchée dans
expert-travaux/devis. Cette session a ajouté un **étage `.md` pivot** au pipeline
d'ingestion et clarifié l'**architecture modèles** (embeddings vs raisonnement).
Rien de cassé, tout poussé. Reprise = choisir une des 3 actions plus bas.

## Ce qui a été fait cette session

1. **Architecture « token-efficient » (3 étages)** — comment utiliser le texte
   normatif sans relire les PDF en entier à chaque requête :
   - **Étage 0** — KB de règles structurée (`dtu_rules.yaml` : `{lot, exigence,
     seuil, condition, ref}`, **réécrite, 0 texte copié**) → lookup déterministe
     par lot, ~0 token. Couvre ~80 % des besoins du devis. **Pas encore construit.**
   - **Étage 1** — RAG sémantique (déjà en place : Supabase `maestro_norms_chunks`)
     → embed une fois, récupérer le **top-k** (k=3-5), pas le PDF entier.
   - **Étage 2** — PDF brut lu **une seule fois** à l'ingestion ; jamais relu en prod.
   - Gain : ~50–150k tokens/devis (relecture PDF) → **200–2 500 tokens/devis**.

2. **HTML vs Markdown** — tranché : le **Markdown** est le bon format-pivot
   (greppable, versionnable, alimente le chunker), pas le HTML (balises = plus de
   tokens). Distinction clé : `.md` pour **consultation humaine** (recherche
   plein-texte, 0 token LLM) **et** comme **source d'ingestion** ; le LLM ne
   consomme jamais le `.md` en entier (seulement le top-k au retrieval).

3. **Outils construits, testés, poussés** (commit `c762418`) :
   - **`tools/pdf_to_md.py`** — PDF → Markdown structuré via le **sommaire
     embarqué** (signets) + `pdftotext` ; front-matter YAML depuis le manifest
     (`lot`, `dtu_refs`, `source_url`, `sha256`, licence) ; suppression
     automatique des en-têtes/pieds récurrents. Tolère les 2 schémas de manifest
     (AQC : `source_url`/`title` ; RAGE : `url_source`/`lot`/`dtu_refs`).
   - **`tools/chunk_md.py`** — Markdown → chunks **par section** (jamais à cheval
     sur deux sections), porteurs du fil d'Ariane + `lot` + `dtu_refs`. **Champs
     100 % compatibles** avec l'INSERT Supabase de `embed_and_load.py` (extras
     ignorés) → drop-in, pas de chemin parallèle.
   - **`tools/README.md`** — documente la variante recommandée (pivot Markdown).
   - **`index/sample/`** — exemple versionné : Reco Pro RAGE granulés (lot 04,
     DTU 24.1, libre de droits) → `.md` (41 sections) + `.chunks.jsonl` (46 chunks).
   - Validé : drop-in OK (10 champs INSERT présents) ; artefacts `pdftotext`
     mineurs connus (texte justifié `A r t i c l e`, césures) — non bloquants.

4. **Architecture modèles (embeddings vs Claude)** — clarifié :
   - **Anthropic ne propose PAS d'API d'embeddings.** Claude est génératif ; pas
     de `/v1/embeddings`, pas de modèle d'embeddings Claude. Fournisseur
     d'embeddings **recommandé par Anthropic = Voyage AI** (tiers).
   - **Deux métiers distincts** : *embeddings* (vectoriser → recherche) =
     Gemini/Voyage/Cohere ; *raisonnement* (lire le top-k, rédiger la
     justification, extraire les règles) = **Claude** (l'agent tourne déjà dessus).
   - **Pourquoi Gemini** : maestro-platform a standardisé sur Gemini embeddings
     (`core/model_config.py`) → même espace vectoriel que le reste de la
     plateforme. Composant **interchangeable** (derrière `embed()`), mais
     **changer d'embedder = ré-embedder tout le corpus** (4 049 chunks).
   - Levier de qualité du **livrable** = le LLM (Claude), pas l'embedder.
   - `prompt caching` Anthropic sur le bloc de règles stable → ~0,1× (‑90 %) sur
     les lectures cachées.

## État du repo (au handoff)

- **maestro-norms** : branche `claude/trusting-ramanujan-pFULL`, dernier commit
  **`c762418`** (pivot MD). `main` officialisé (feature norms mergée).
- **maestro-platform** : feature « justification normative par lot » **mergée sur
  `main`** (PR #22 + fix #23). PR ouvertes : **#24** (test e2e devis), **#27**
  (BDNB lookup). Code clé : `expert_travaux/norms_by_lot.{py,yaml}`,
  `compliance_agent.get_norms_for_lot`, section devis dans
  `maestro_document_agent`, `agents/bdnb_lookup.py` (+ tests).
- **Supabase** : projet « Maestro Platform V2 » (`ppvuecbtfsyggnoompbq`), table
  `maestro_norms_chunks` = **4 049 chunks** (348 AQC + 9 Reco Pro RAGE), HNSW
  cosine, RLS, `gemini-embedding-001` 768d. ⚠️ Ces 9 RAGE ont été ingérés avec
  l'**ancien** chunker à fenêtres (pas section-aware) — d'où l'action 1 ci-dessous.
- **Corpus** (git-LFS) : `corpus/aqc/` (334) + `corpus/profeel/` (14) +
  `corpus/rage/` (9 Reco Pro). `manifest.json` + `manifest-rage.json` (sha256).

## Prochaines actions (au choix — reprise)

1. **Ré-ingérer les 9 Reco Pro RAGE en *section-aware*** dans Supabase (remplace
   leurs chunks actuels par les meilleurs via `pdf_to_md.py` → `chunk_md.py` →
   `embed_and_load.py --target supabase`). ⚠️ **Nécessite une clé Gemini active**
   (`GEMINI_API_KEY`/`GOOGLE_API_KEY`) — ne pas la committer. ~5 min.
2. **Prototyper `dtu_rules.yaml`** (étage 0) sur 1–2 lots (ex. 04 chauffage/ECS,
   05 ventilation/élec), règles écrites à la main (0 texte DTU copié), branché
   dans `norms_by_lot`. Donne le levier « 0 token » par lot.
3. **Appliquer le pivot à un vrai DTU** quand la licence **REEF Collection**
   (~544 €HT) est acquise — même commande, garde-fou **citation-seule côté
   client** (lecture interne sous licence ; jamais de verbatim dans le devis).

Autres en attente : merger #24 et #27 ; compléter le corpus RAGE (sources gâtées,
cf. `docs/RESEARCH-BACKLOG.md` §1) ; OCR du PDF image VDI ; `CSTBLookup` /atec
(assurabilité, §8) ; titres FFB (citation seule).

## Repères / gotchas

- Pipeline d'ingestion : voir `tools/README.md` (variante pivot MD recommandée).
- **Licence** : RAGE/PACTE/PROFEEL = libre diffusion (plein texte OK) ; DTU/NF &
  FFB = **citation seule**. Pour les DTU payants : lecture interne + `.md` pivot
  d'accord, **jamais de verbatim côté client**.
- **pytest** (sandbox) : `pip install --ignore-installed PyJWT pydantic pytest
  pytest-asyncio httpx google-genai google-generativeai PyPDF2`.
- Embeddings : `gemini-embedding-001` 768d (text-embedding-004 retiré par Google).
- Egress sandbox : BAN geocoder et accès DB direct Supabase bloqués → tests
  mockent le réseau ; ingestion via PostgREST/RPC si besoin.
- Backlog complet : `docs/RESEARCH-BACKLOG.md`. Handoffs antérieurs :
  `docs/HANDOFF-tests.md`, `docs/HANDOFF-SESSION-2026-06-05.md`.
