# maestro-norms — mémoire projet

> Base de **justification normative** pour Maestro : Recommandations Pro
> RAGE/PACTE/PROFEEL (gratuit, plein texte) + DTU/NF (citation) **mappées par
> lot**, branchées dans l'expert‑travaux/devis pour citer la règle de l'art
> applicable. PDF stockés en **git‑LFS** (`corpus/**`).
>
> 👉 **Reprise = `docs/HANDOFF-SESSION-2026-06-18.md`** (pivot Markdown + archi
> embeddings/Claude). Branche dev : `claude/trusting-ramanujan-pFULL`.

## État (fait ✅, mergé)
- `corpus/aqc/` (334) + `corpus/profeel/` (14) + `corpus/rage/` (9 Reco Pro) ; `manifest.json` + `manifest-rage.json` (SHA‑256). Repo : **`main`** officialisé.
- Mapping lot↔DTU↔Reco Pro : `docs/lot-norms-mapping.{md,yaml}`.
- Index sémantique : Supabase **« Maestro Platform V2 »** (`ppvuecbtfsyggnoompbq`), table `maestro_norms_chunks` (**4 049 chunks** — 348 AQC + 9 Reco Pro RAGE, HNSW cosine, RLS).
- Code **mergé sur `main`** (maestro-platform, **PR #22**) : `expert_travaux/norms_by_lot.{py,yaml}`, `compliance_agent.get_dtu_reference/get_norms_for_lot`, section « Justification normative par lot » dans `maestro_document_agent` (devis). Tests verts (9 + 4 + 126).

## Tâches à faire (archive)
- [ ] **Demain — TESTS** : figer la démo en `test_devis_norms_section.py`, suite complète, test recherche sémantique, cas limites (cf. `docs/HANDOFF-tests.md`).
- [ ] **Compléter le corpus RAGE** (sources gâtées) — détail : `docs/RESEARCH-BACKLOG.md`
      (chaudières granulés trilogie · FCBA CLT cert TLS · ITE · GTB · verrières).
- [ ] **OCR** du PDF image `Fiche-Attestations-VDI-PE01-…` (texte non extractible).
- [x] **Lots DTU‑citation‑seule** investigués (03/06/08/09/10) → pas de Reco Pro RAGE gratuite (cf. RESEARCH-BACKLOG §2).
- [x] **Embeddings du `corpus/rage/`** → faits (738 chunks, gemini‑embedding‑001 768d).
- [x] **CI / tests** → lancés et verts (norms 9, devis 4/1skip, expert‑travaux 126).
- [x] **Consolidation** → PR #22 mergée sur `main` ; `main` maestro-norms officialisé.
- [ ] **FFB** : titres exacts des Calepins par lot (export adhérent) — citation seule.
- [ ] Optionnel : `web.archive.org` (allowlist) pour les guides RAGE 2012 d'origine.

## Repères
- **Pivot Markdown** (PDF → `.md` structuré → chunks par section → Supabase) :
  `tools/pdf_to_md.py` + `tools/chunk_md.py` (drop-in `embed_and_load.py`),
  exemple `index/sample/`, doc `tools/README.md`. Archi : embeddings = Gemini/Voyage,
  raisonnement = Claude (Anthropic n'a pas d'API d'embeddings).
- Handoff session 2026-06-18 : `docs/HANDOFF-SESSION-2026-06-18.md`.
- Handoff TESTS : `docs/HANDOFF-tests.md` · Handoff corpus : `maestro-platform/docs/HANDOFF-norms-corpus.md`.
- Backlog recherche : `docs/RESEARCH-BACKLOG.md`. Lots + `dtu_refs` : `maestro-platform/.../expert_travaux/knowledge.yaml`.
- Licence : RAGE/PACTE/PROFEEL = libre diffusion ; DTU/NF & FFB = citation seule (cf. `README.md`).
