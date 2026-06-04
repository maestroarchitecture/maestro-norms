# HANDOFF — Tests (reprise demain)

> Objectif **livré et mergé sur `main`** (maestro-platform PR #22 ; maestro-norms
> `main`). Ce document sert à **reprendre côté tests**.
> Date : 2026-06-04.

## 1. Où on en est

- **Code (sur `main` maestro-platform, merge `7dfa50a`)** : `expert_travaux/norms_by_lot.{py,yaml}`,
  `compliance_agent.get_dtu_reference/get_norms_for_lot`, section « Justification
  normative par lot » dans `maestro_document_agent._to_maestro_json`.
- **Corpus (sur `main` maestro-norms)** : 348 AQC + 9 Reco Pro RAGE (`corpus/rage/`, LFS),
  manifests SHA-256, mapping lot↔DTU↔Reco Pro, index Supabase **4 049 chunks**.

## 2. État des tests (✅ passent)

| Fichier | Résultat | Couvre |
|---|---|---|
| `…/expert_travaux/test_norms_by_lot.py` | **9 passed** | `norms_for_lot`, `dtu_reference`, `resolve_lot`, `norms_section_for_lots` |
| `…/agents/test_maestro_document_agent.py` | **4 passed, 1 skipped** | `_to_maestro_json` (section devis) ; skip = rendu HTML (skill externe) |
| `…/expert_travaux/test_expert_travaux.py` | **126 passed** | non-régression skill expert-travaux |

Démo e2e validée en direct : un devis (lots 04/03/10) rend la section avec
`04 → NF DTU 68.3 + Reco Pro VMC`, `03/10 → DTU seul, règle de l'art « — »`.

## 3. ⚠️ Environnement de test (sandbox web) — IMPORTANT

`pydantic` & co **ne sont pas préinstallés**. Pour lancer la pytest :

```bash
cd maestro-platform
pip install -q --ignore-installed PyJWT \
    pydantic pytest pytest-asyncio httpx google-genai google-generativeai PyPDF2
```
- `--ignore-installed PyJWT` : contourne un conflit avec le PyJWT système Debian
  (sinon l'install de `supabase`/deps avorte).
- `pytest.ini` met déjà `packages`, `packages/maestro`, `packages/maestro/pro/backend`
  sur le `pythonpath`.
- `agents/__init__.py` importe **tous** les agents → tirer un seul test charge toute
  la chaîne de deps (httpx, gemini client…). D'où la liste ci-dessus.
- Tests `@pytest.mark.requires_db` (Batiprix) : **skippés** sans `batiprix.db`.

Lancer les 3 fichiers clés :
```bash
python3 -m pytest \
  packages/maestro/pro/backend/agents/skills/expert_travaux/test_norms_by_lot.py \
  packages/maestro/pro/backend/agents/test_maestro_document_agent.py \
  packages/maestro/pro/backend/agents/skills/expert_travaux/test_expert_travaux.py -q
```

## 4. Plan de tests — DEMAIN (priorisé)

1. **Figer la démo en test e2e versionné** : créer
   `packages/maestro/pro/backend/agents/test_devis_norms_section.py` (code §5),
   commit + push. → garantit la section devis en CI à chaque commit.
2. **Lancer la suite complète** (`pytest -q` sur tout `packages/maestro/pro/backend`)
   pour voir ce qui casse / nécessite `batiprix.db`, et trier les skips légitimes.
3. **Test recherche sémantique** (index Supabase, projet V2 `ppvuecbtfsyggnoompbq`) :
   recréer une RPC `match_norms_chunks(query_embedding text, k int)` (SECURITY DEFINER),
   embed une requête (`gemini-embedding-001`, 768d, normalisé), vérifier que les
   **9 Reco Pro RAGE** remontent (ex. « pompe à chaleur air-eau » → doc PAC). Penser à
   **dropper la RPC** après (hygiène).
4. **Intégrité corpus** : `git lfs pull` puis vérif `sha256` vs `manifest.json` +
   `manifest-rage.json` (script dans `README.md`).
5. **Cas limites** à ajouter au test e2e : lot inconnu (`"99"`), devis vide,
   poste sans `lot_id` (fallback `resolve_lot` via mot-clé), lots dédupliqués/triés.

## 5. Test e2e prêt à coller (étape 1)

`packages/maestro/pro/backend/agents/test_devis_norms_section.py` :

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from agents.maestro_document_agent import MaestroDocumentAgent          # noqa: E402
from agents.schemas import DevisDetaillee, PosteChiffrage, Gamme        # noqa: E402


def _devis(lots):
    postes = [PosteChiffrage(lot_id=lid, lot_label=lab, designation=f"poste {lid}",
              unite="u", quantite=1, prix_unitaire=100.0, montant_ht=100.0,
              fallback_level=1, source_prix="batiprix", code_batiprix="XX 00")
              for lid, lab in lots]
    d = DevisDetaillee(id_devis="T", projet="T", client="T",
                       date_emission="2026-06-04", postes=postes, gamme=Gamme.STANDARD)
    d.recalculate_totals()
    return d


def _section(devis):
    doc = MaestroDocumentAgent()._to_maestro_json(devis=devis, ref="T", adresse="A", client="C")
    return next(s for s in doc["sections"] if s.get("titre") == "Justification normative par lot")


def test_section_presente_et_typee():
    sec = _section(_devis([("04", "Chauffage / VMC")]))
    assert sec["type"] == "table" and sec["headers"][0] == "Lot"


def test_lot_avec_reco_pro_cite_dtu_et_regle_de_lart():
    row = _section(_devis([("04", "Chauffage / VMC")]))["rows"][0]
    assert "NF DTU 68.3" in row[1]
    assert "vmc" in row[2].lower()            # Reco Pro RAGE citée


def test_lot_dtu_citation_seule_sans_regle_de_lart():
    row = _section(_devis([("03", "Plomberie / Sanitaires")]))["rows"][0]
    assert "DTU 60.1" in row[1] and row[2] == "—"


def test_lots_dedupliques_et_tries():
    sec = _section(_devis([("10", "Peinture"), ("04", "VMC"), ("04", "VMC")]))
    assert [r[0].split(" — ")[0] for r in sec["rows"]] == ["04", "10"]
```

## 6. Repères

- PR mergée : maestro-platform **#22** · Corpus : `maestro-norms` (`main`).
- Backlog non-tests : `maestro-norms/docs/RESEARCH-BACKLOG.md`.
- Mapping : `maestro-norms/docs/lot-norms-mapping.{md,yaml}` ; mémoire : `CLAUDE.md`.
