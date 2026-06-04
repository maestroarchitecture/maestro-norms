# maestro-norms — mémoire projet

> Base de **justification normative** pour Maestro : Recommandations Pro
> RAGE/PACTE/PROFEEL (gratuit, plein texte) + DTU/NF (citation) **mappées par
> lot**, branchées dans l'expert‑travaux/devis pour citer la règle de l'art
> applicable. PDF stockés en **git‑LFS** (`corpus/**`).

## État (fait)
- `corpus/aqc/` (334) + `corpus/profeel/` (14) + `corpus/rage/` (9 Reco Pro) ; `manifest.json` + `manifest-rage.json` (SHA‑256).
- Mapping lot↔DTU↔Reco Pro : `docs/lot-norms-mapping.{md,yaml}`.
- Index sémantique : Supabase **« Maestro Platform V2 »** (`ppvuecbtfsyggnoompbq`), table `maestro_norms_chunks` (3 311 chunks, HNSW cosine, RLS).
- Code (repo `maestro-platform`, branche `claude/trusting-ramanujan-pFULL`) :
  `expert_travaux/norms_by_lot.py` (+ `norms_by_lot.yaml`), `compliance_agent.get_dtu_reference/get_norms_for_lot`,
  section « Justification normative par lot » dans `maestro_document_agent` (devis).

## Tâches à faire (archive)
- [ ] **Compléter le corpus RAGE** (sources gâtées) — détail : `docs/RESEARCH-BACKLOG.md`
      (chaudières granulés trilogie · FCBA bois cert TLS · ITE · GTB · verrières).
- [ ] **Embeddings du `corpus/rage/`** dans `maestro_norms_chunks` — nécessite une **clé Gemini**
      (`tools/extract_chunks.py` puis embed `gemini-embedding-001` 768d). Actuellement seuls les 348 AQC sont indexés.
- [ ] **OCR** du PDF image `Fiche-Attestations-VDI-PE01-…` (texte non extractible).
- [x] **Lots DTU‑citation‑seule** investigués (03/06/08/09/10) → pas de Reco Pro RAGE gratuite (cf. RESEARCH-BACKLOG §2).
- [ ] **FFB** : titres exacts des Calepins par lot (export adhérent) — citation seule.
- [ ] **CI** : lancer la pytest `maestro-platform` (valider la section devis + `test_norms_by_lot`) — non lançable dans le sandbox (`pydantic` absent).
- [ ] **Consolider la branche** `claude/trusting-ramanujan-pFULL` → `claude/weekly-recap-4PfeQ` / **PR #9**.
- [ ] ⚠️ **Sécurité** : régénérer la **clé Gemini** exposée en chat ; révoquer le **token GitHub** (handoff §6).
- [ ] Optionnel : `web.archive.org` (allowlist) pour les guides RAGE 2012 d'origine.

## Repères
- Handoff complet : `maestro-platform/docs/HANDOFF-norms-corpus.md`.
- Lots canoniques + `dtu_refs` : `maestro-platform/.../expert_travaux/knowledge.yaml`.
- Licence : RAGE/PACTE/PROFEEL = libre diffusion ; DTU/NF & FFB = citation seule (cf. `README.md`).
