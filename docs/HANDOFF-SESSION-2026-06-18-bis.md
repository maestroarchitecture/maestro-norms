# HANDOFF — Session 2026-06-18 bis — 3 actions (RAGE / étage 0 / DTU) + accès Reef

> Suite de `docs/HANDOFF-SESSION-2026-06-18.md`. Le repo se clone à neuf ; ce
> fichier + `CLAUDE.md` suffisent à reprendre. Branche de dev :
> **`claude/trusting-ramanujan-pFULL`** (développer/commiter/pusher seulement ici).
>
> ⚠️ **Reprise = ce fichier.** Décision utilisateur : exécuter **les 3 actions en
> séquence**. Cette session a fait toute la prep sans-secret + corrigé une erreur
> du handoff précédent + exploré l'accès Reef. Reste : 1 secret (clé Gemini),
> 1 licence (acquise), et la rédaction+vérif de `dtu_rules.yaml`.

## TL;DR — état des 3 actions

> **MAJ 2026-06-18 (session bis-2)** : Actions 2 et 3 **faites** (commits `d3b48b0`
> et `0b06f13` sur `claude/trusting-ramanujan-pFULL`, poussés). **Seul bloqueur
> restant : `GEMINI_API_KEY`** (Action 1, et l'embed du POC Action 3).

| Action | État | Bloqueur restant |
|---|---|---|
| **1. Ré-ingestion RAGE section-aware** | Prep **finie** (9 `.md` + 9 chunks dans `index/rage/`). Mécanique de remplacement validée. | **`GEMINI_API_KEY`** (embed) — voir §Action 1. |
| **2. `dtu_rules.yaml` (étage 0)** | ✅ **Fait** (`d3b48b0`) : **18 règles vérifiées**, 6 lots (03/04/05/08/09/10). Tests verts (13). Lot 04 = sources primaires (Arrêté 1982 + DTU Reef) ; lot 05 = NF C 15-100 recoupé web (secondaire). | — |
| **3. Pivot DTU réel** | ✅ **POC fait** (`0b06f13`) : NF DTU 65.14 → pivot `.md` **interne** (`private/`, gitignoré) → 5 chunks `licence=dtu_payant`. `chunk_md.py` propage le flag licence. | Embeddings/insert = `GEMINI_API_KEY` (idem Action 1). |

> **TODO plateforme** (PR séparée) : la couche de restitution doit **consommer**
> le flag `licence=dtu_payant` pour exclure le `text` des chunks DTU des sorties
> client. Aujourd'hui le flag est **posé** (chunk_md) mais **pas encore appliqué**
> par un consommateur — pas de risque live (rien publié, embed gated).

## ⚠️ CORRECTION CRITIQUE — modèle d'embedding

Le handoff précédent affirme `gemini-embedding-001`. **C'est FAUX.** La table
Supabase `maestro_norms_chunks` (projet `ppvuecbtfsyggnoompbq`, 4 049 chunks dim 768)
est en **`text-embedding-004`**. Preuve (source primaire) :
`maestro-platform/packages/maestro/core/model_config.py:43`
(`MODEL_NAME_EMBEDDING = "text-embedding-004"`) + `gemini_client.embed_content_async` ;
`tools/embed_and_load.py:27` et `extract_chunks.py` aussi. `index/stats.json`
(text-embedding-004) est correct.

**Conséquence** : ré-embedder pour cette table **DOIT** utiliser `text-embedding-004`
(même espace vectoriel). NE PAS « migrer » vers gemini-embedding-001 (casserait le
retrieval des 4 049). Avant tout insert : auto-test cosinus (cf. Action 1, étape 3).

## État repo / environnement

- Branche `claude/trusting-ramanujan-pFULL`. Travail de cette session **non encore
  mergé/poussé au moment de la rédaction** → committé dans le même commit que ce
  handoff.
- **git-LFS** : `corpus/**` est en LFS. `git-lfs` **n'était pas installé** → installé
  via `brew install git-lfs` ; `git lfs install --local` ; **9 PDF RAGE récupérés**
  via `git lfs pull --include="corpus/rage/*"` (réels, vérifiés `%PDF`).
- Deps : `pdftotext` (poppler 26.04) OK, `python3` 3.10, `pypdf` 6.13.3 installé, `pyyaml` OK.
- **WebSearch** : quota de session épuisé (reset 18h Europe/Paris) — a bloqué la
  vérif web des seuils cette session. Perplexity : clé invalide (401).
- Repo cloné dans `~/Documents/GitHub/maestro-norms` (n'existait pas localement ;
  vit sur GitHub `maestroarchitecture/maestro-norms`, **public**).

## Fichiers créés cette session (dans maestro-norms)

- `index/rage/` — 9 `.md` pivots + 9 `.chunks.jsonl` **section-aware** (prep action 1).
- `tools/dtu_rules.py` — loader étage 0 (`rules_for_lot`, `justification_rows_for_lot`,
  `resolve_lot` alias métier, CLI démo lookup ~0 token).
- `tools/test_dtu_rules.py` — tests du loader + invariants (skip tant que YAML absent).
- `tools/embed_chunks_gemini.py` — **embeddings Gemini + auto-test de modèle** (cosinus
  vs vecteur stocké, gestion normalisation gemini-embedding-001). Écriture DB **non**
  incluse (pilotée via MCP Supabase).
- `docs/RUNBOOK-DTU-pivot.md` — procédure pivot réutilisable + garde-fou citation-seule.
- `docs/INTEGRATION-dtu-rules.md` — recette de branchement de l'étage 0 dans
  `norms_by_lot` (côté maestro-platform).
- `.gitignore` — exclut `__pycache__`, `*.emb.jsonl`, secrets (`.env`, `probes.json`).

---

## Action 1 — Ré-ingestion RAGE section-aware (prep finie, embed key-gated)

**Fait** : `index/rage/<doc>.md` + `<doc>.chunks.jsonl` pour les 9 RAGE (via
`pdf_to_md.py --out index/rage` puis `chunk_md.py`). Counts section-aware vs
window (en base) :

| doc_sha256 (court) | doc | section (neuf) | window (base) |
|---|---|---|---|
| ab3c20…| PAC air-eau | 106 | 108 |
| f54a86…| VMC SF indiv | 49 | 50 |
| 27b731…| schémathèque PAC | 93 | 104 |
| 2357df…| granulés | 46 | 44 |
| be4a04…| façades ossature bois | 164 | 172 |
| 4469749…| isolation sous-faces | 33 | 35 |
| fcaa70…| maçonnerie | 45 | 53 |
| 1b46c2…| VMC DF collectif | 83 | 79 |
| 7a401e…| VMC SF collectif réno | 93 | 93 |

(Total neuf ≈ 712 vs 738 en base.)

**Schéma d'`id` confirmé sur la vraie base** : `id = sha256("{doc_sha256}:{chunk_index}")[:24]`
(idem ancien chunker `extract_chunks.py:82`) → collision ancien/nouveau sur les
`chunk_index` communs (vérifié : granulés idx 0/1/43 = `706fc8…`/`bc5f54…`/`e7c08d…`).

**Remplacement sûr et idempotent (par doc, via MCP Supabase — jamais zéro chunk)** :
1. UPSERT des nouveaux chunks embeddés (`ON CONFLICT (id) DO UPDATE`).
2. `DELETE FROM maestro_norms_chunks WHERE doc_sha256='<sha>' AND chunk_index >= <M>`
   (`M` = nb de nouveaux chunks du doc) → supprime la seule queue orpheline.
3. Vérifier les counts.

**Étapes restantes (clé requise)** :
1. Utilisateur crée `maestro-norms/.env` avec `GEMINI_API_KEY=...` (gitignoré ; jamais committé).
2. **Auto-test modèle** (OBLIGATOIRE) : extraire via MCP 2 sondes (1 RAGE + 1 AQC :
   `text` + `embedding` d'un chunk existant) → `probes.json` →
   `GEMINI_API_KEY=… python3 tools/embed_chunks_gemini.py --selftest probes.json`.
   cosinus ≥ 0.999 attendu. Si non concordant pour text-embedding-004 **et**
   gemini-embedding-001 → **escalade** (la table serait dans un modèle indispo ⇒
   ré-embed total des 4 049, hors périmètre des 9). NB : tester d'abord si
   `text-embedding-004` répond encore (rumeur de retrait Google non vérifiée — l'appel API tranche).
3. `GEMINI_API_KEY=… python3 tools/embed_chunks_gemini.py index/rage/*.chunks.jsonl`
   → `index/rage/<doc>.emb.jsonl`.
4. Pour chaque doc : UPSERT + DELETE-queue (SQL ci-dessus) via MCP Supabase. Vérifier.

## Action 2 — `dtu_rules.yaml` (étage 0) — À RÉDIGER + VÉRIFIER

**Fait** : `tools/dtu_rules.py` (loader), `tools/test_dtu_rules.py`,
`docs/INTEGRATION-dtu-rules.md`. **À faire** : créer `dtu_rules.yaml` (racine repo).

Schéma attendu par le loader/tests :
```yaml
meta:
  generated: "2026-..."
  licence: "Faits/seuils paraphrasés — AUCUN texte DTU verbatim. ref = citation seule."
rules:
  "04":
    - exigence: "<paraphrase courte d'une exigence>"
      seuil: "<valeur chiffrée>"
      condition: "<champ d'application>"
      ref: "<NF DTU 68.3 §x.y / Arrêté 24/03/1982>"
  "05":
    - { exigence: ..., seuil: ..., condition: ..., ref: "NF C 15-100 §..." }
```
Lots à prototyper (cf. `docs/lot-norms-mapping.yaml`) : **04 Chauffage/VMC**
(NF DTU 68.3 ventilation/débits, DTU 24.1 conduits granulés, DTU 65.10/65.14) et
**05 Électricité** (NF C 15-100 : 30 mA, sections, socles/pièce, circuits spécialisés).

**Vérification (impératif — pas de seuil de mémoire ; risque client)** :
- **Lot 04** : sources autoritaires dans le **Reef** (NF DTU 68.3, DTU 24.1, DTU 65.x —
  voir §Action 3) + Arrêté 24/03/1982 (débits, gratuit sur Legifrance).
- **Lot 05** : **NF C 15-100 = AFNOR, ABSENT du Reef** → vérifier via web (quota reset
  18h) / Promotelec / Consuel / Legrand-Schneider (guides).
- Approche outillée : le workflow `dtu-rules-draft-verify` (script sauvegardé, voir
  `.claude/.../workflows/scripts/dtu-rules-draft-verify-*.js`) faisait draft + vérif
  2-angles web par règle. **Il a été aborté** cette session (WebSearch throttlé).
  Le relancer quand le quota web est dispo, OU vérifier à la main via Reef (lot 04).
- Filtrer côté client sur un `statut: verifie` (ne jamais sortir une règle non vérifiée).

Tests : `python3 -m pytest tools/test_dtu_rules.py -q` (skip tant que YAML absent ;
vert une fois le YAML rempli avec les 4 champs non vides par règle).

## Action 3 — Pivot DTU réel (licence acquise ; contraintes Reef)

**Licence Reef Collection DTU acquise** (compte = e-mail utilisateur ; la connexion
doit être faite **par l'utilisateur** — politique : Claude ne saisit pas de mot de
passe). Portail : **batipedia.com** → SSO `sso/go-to-external-product.html?reef`.
> Le mot de passe a été partagé en clair dans le chat de la session précédente →
> **le faire changer**. NE PAS le stocker dans le repo.

**Constats d'accès (importants)** :
- Reef = **lecteur en ligne HTML** (`/reef/document/texte/<CODE>.html`), **pas** de
  téléchargement PDF en masse. Le menu « Actions » d'un document déclenche une
  **impression native bloquante** (a fait planter la page une fois).
- **CGU** : service par abonnement, **extraction systématique/automatisée restreinte**
  → ne PAS scraper en masse (risque pour le compte). Accès « comme un utilisateur ».
- **Stockage** ⚠️ : maestro-norms est **public** → un DTU (texte sous licence) ne doit
  **jamais** y être committé. Pivot `.md` d'un DTU = **interne/gitignoré uniquement**.
- Recherche : `/reef/rechercheREEF.html` (taper la requête dans le champ ; le param
  d'URL `options.query` se réinitialise). Fiche document : `/reef/document/fiche/<CODE>.html`.

**Usage recommandé & conforme** : utiliser l'accès pour **lire et extraire les faits/
seuils** (lot 04) → alimente la vérif de `dtu_rules.yaml` (lecture + extraction de
faits = légitime ; les seuils ne sont pas protégeables, on cite la clause). Pour un
vrai pivot DTU (POC), traiter **1 DTU**, stockage interne gitignoré, garde-fou
citation-seule (cf. `docs/RUNBOOK-DTU-pivot.md §5`).

## Prochaines actions concrètes (ordre suggéré)

1. **Action 2** d'abord (aucun secret) : rédiger `dtu_rules.yaml` lot 04 vérifié via
   Reef (+ Arrêté 1982) ; lot 05 quand le web est dispo. Tests verts. Commit.
2. **Action 1** dès que `.env`/`GEMINI_API_KEY` fourni : auto-test modèle → embed →
   UPSERT+DELETE-queue (MCP) → vérif. Commit (sans `.emb.jsonl`, gitignoré).
3. **Action 3** : POC pivot sur 1 DTU (NF DTU 68.3) en interne gitignoré, citation-seule.
4. Brancher l'étage 0 dans `maestro-platform/expert_travaux/norms_by_lot.py`
   (cf. `docs/INTEGRATION-dtu-rules.md`) — PR séparée côté platform.

## Repères / gotchas

- Garde-fou licence : RAGE/PACTE/PROFEEL = plein texte OK ; **DTU/NF & FFB = citation
  seule**. DTU payant : lecture interne + `.md` pivot OK, **jamais de verbatim client**.
- MCP Supabase connecté (`execute_sql`/`apply_migration`) → écritures DB sans
  `SUPABASE_DB_URL`. Project id : `ppvuecbtfsyggnoompbq`.
- `embed_and_load.py` exige `DATABASE_URL` (psycopg) ; alternative MCP utilisée ici.
- Handoffs antérieurs : `docs/HANDOFF-SESSION-2026-06-18.md`, `…-06-05.md`,
  `docs/HANDOFF-tests.md`. Backlog : `docs/RESEARCH-BACKLOG.md`.
