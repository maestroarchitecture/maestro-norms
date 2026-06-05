# HANDOFF — Session « Justification normative ↔ devis Maestro »

> Récapitulatif complet de la session de travail. Claude Code (session **web/distante**).
> Date : **2026-06-05**.

---

## 1. Objectif
Doter le **devis Maestro d'une justification normative par lot** : chaque lot du devis
cite automatiquement le **DTU/NF** applicable + la **Recommandation Professionnelle
RAGE/PACTE** correspondante — au lieu d'un mapping DTU codé en dur. Le tout adossé à un
**corpus normatif** réel, versionné et interrogeable (recherche sémantique).

## 2. Livré ✅

### Corpus — repo `maestro-norms`
- `corpus/aqc/` (334) + `corpus/profeel/` (14) + `corpus/rage/` (**9 Reco Pro RAGE**) en **git-LFS**.
- `manifest.json` + `manifest-rage.json` (**SHA-256**) ; `README.md` (licences).
- Mapping **lot ↔ DTU ↔ Reco Pro** : `docs/lot-norms-mapping.{md,yaml}`.
- **Index sémantique Supabase** « Maestro Platform V2 » (`ppvuecbtfsyggnoompbq`),
  table `maestro_norms_chunks` : **4 049 chunks** (348 AQC + 738 RAGE), HNSW cosine, RLS,
  embeddings `gemini-embedding-001` 768d.
- `tools/extract_chunks.py` + `tools/embed_and_load.py`.
- `main` créé (⚠️ branche par défaut GitHub encore `claude/trusting-ramanujan-pFULL`).

### Code — repo `maestro-platform` (mergé sur `main`)
- `expert_travaux/norms_by_lot.{py,yaml}` : `norms_for_lot`, `dtu_reference`, `resolve_lot`, `norms_section_for_lots`.
- `compliance_agent` : `get_dtu_reference` sourcé sur `knowledge.yaml` + `get_norms_for_lot`.
- `maestro_document_agent._to_maestro_json` : **section « Justification normative par lot »** injectée dans le devis.
- Tests : `test_norms_by_lot.py`, `test_devis_norms_section.py`.
- **PRs** : **#22** (feature) mergée · **#23** (fix revue Codex : noms internes retirés du caption) mergée · **#24** (test e2e) **OUVERTE → à merger**.

### Tests
- Suite `packages/maestro/pro/backend` : **313 passed, 1 skipped**.
- Recherche sémantique validée (les Reco Pro RAGE remontent). Intégrité corpus **357/357**.
- Env test (sandbox web) : `pip install --ignore-installed PyJWT pydantic pytest pytest-asyncio httpx google-genai google-generativeai`.

## 3. Décisions clés
- Périmètre corpus = **sous-ensemble technique** (presse/recrutement exclus) ; structure **par source** (aqc/profeel/rage).
- Guides **RAGE 2012 d'origine indisponibles** → Reco Pro récupérées sur **miroirs** (xpair, jurad-bat, cndb, programmepacte).
- **git-LFS** pour `corpus/**` (sinon push HTTP 413).
- Lots **03/06/08/09/10 = DTU/CSTB citation seule** (pas de Reco Pro gratuite ; SPEC/SEL = CSTB Cahier 3756).

## 4. Contraintes rencontrées
- **Egress** : `web.archive.org` bloqué (RAGE 2012 d'origine), `fcba.fr` **cert TLS** rejeté, `costic.com` **derrière login**, `enviroboite` 503.
- Push **413** → LFS + commits incrémentaux.
- `text-embedding-004` retiré par Google → `gemini-embedding-001`.
- ⚠️ **`maestro-reports` (renderer du devis brandé) = skill LOCAL, hors source control**
  (`~/.claude/skills/maestro-reports/`). Ni la session web ni la CI ne peuvent générer le
  devis brandé — **seule ta machine** le peut aujourd'hui.

## 5. Reste à faire (priorisé)
1. **Merger la PR #24** (test e2e).
2. **Vendorer le skill `maestro-reports`** (`report_generator.py` + `rapport_faisabilite.py` + template/CSS/tokens) dans `maestro-platform` (ex. `packages/maestro/skills-mirror/maestro-reports/`) → rendu brandé **reproductible** en session/CI, et validation visuelle du devis.
3. **Valider le rendu** de la section normative dans le **devis brandé** (une fois le renderer dispo).
4. **Compléter le corpus gâté** (trilogie chaudières granulés, CLT FCBA) — cf. `RESEARCH-BACKLOG.md`.
5. Basculer la **branche par défaut** de `maestro-norms` sur `main` (réglage GitHub).
6. (option) **RAF / rapport de faisabilité** : aucun builder de contenu dans les repos — à définir.

## 6. Repères
- Mémoire auto-chargée : `maestro-norms/CLAUDE.md`.
- Handoffs : `maestro-norms/docs/HANDOFF-tests.md` · `maestro-platform/docs/HANDOFF-norms-corpus.md`.
- Backlog recherche : `maestro-norms/docs/RESEARCH-BACKLOG.md`.
- Mapping : `maestro-norms/docs/lot-norms-mapping.{md,yaml}`.
- Index : Supabase `ppvuecbtfsyggnoompbq`, table `maestro_norms_chunks`.
- Aperçus devis (sandbox, non officiels) : `devis-test.json`, `devis-maestro-brande.html`.

## 7. Note sécurité (record)
- Clé Gemini + clé anon Supabase utilisées en session (présentes dans l'historique chat) — à régénérer selon ta politique.
- Token GitHub mentionné dans un ancien handoff — à révoquer.

## 8. Sauvegarde sur ton Mac
Session **distante** → pas d'accès à ton disque. Ce fichier t'est **envoyé** (à déposer
dans ton dossier `PHD`) et **committé** dans `maestro-norms/docs/` pour durabilité.
