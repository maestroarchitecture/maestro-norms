# Intégration de l'étage 0 (`dtu_rules.yaml`) dans `norms_by_lot`

L'étage 0 (`dtu_rules.yaml` + `tools/dtu_rules.py`, repo **maestro-norms**) ajoute
des **règles chiffrées déterministes par lot** aux deux sources déjà branchées
dans l'expert-travaux (repo **maestro-platform**) :

| Source | Fichier (platform) | Contenu | Licence |
|---|---|---|---|
| DTU/NF | `expert_travaux/knowledge.yaml` | `dtu_refs[]` | citation seule |
| Reco Pro RAGE | `expert_travaux/norms_by_lot.yaml` | guides plein texte | libre |
| **Étage 0** | **`dtu_rules.yaml` (ce repo)** | **`{exigence, seuil, condition, ref}`** | **faits + citation** |

But : un lookup par lot répond avec les **seuils chiffrés** (débits, sections,
30 mA, nombre de socles…) **sans** recherche sémantique ni lecture PDF → **~0 token**.

## Recette de branchement (côté maestro-platform)

1. **Synchroniser** la KB à côté de `norms_by_lot.yaml` (sous-module, copie CI, ou
   submodule git de `maestro-norms`) : `expert_travaux/dtu_rules.yaml`.

2. **Étendre `norms_by_lot.py`** — fonction additive, lenient (mêmes conventions
   que `reco_pro_for_lot`) :

   ```python
   _RULES_PATH = _DIR / "dtu_rules.yaml"

   def rules_for_lot(lot_id: str) -> List[dict]:
       """Étage 0 : règles {exigence, seuil, condition, ref} du lot (≈0 token)."""
       rules = _load(_RULES_PATH)
       return list((rules.get("rules") or {}).get(str(lot_id), []))
   ```

3. **Enrichir `norms_for_lot`** (clé additive, rétro-compatible) :

   ```python
   return {
       "lot": lot_id,
       "name": lot.get("name"),
       "dtu_refs": list(lot.get("dtu_refs", [])),   # citation seule
       "reco_pro": reco_pro_for_lot(lot_id),         # gratuit, plein texte
       "rules": rules_for_lot(lot_id),               # étage 0 — seuils chiffrés
   }
   ```

4. **Section devis** — dans `norms_section_for_lots`, ajouter une colonne/bloc
   « Exigences chiffrées » par lot à partir de `rules_for_lot(lid)` :
   chaque ligne `exigence — seuil (condition) — réf`. La `ref` est une
   **citation** ; on n'insère jamais le texte verbatim du DTU.

## Ordre de résolution recommandé (consommation par l'agent)

1. **Étage 0** `rules_for_lot(lot)` → si une règle couvre la question (un seuil) :
   réponse déterministe, **0 token**, on cite la `ref`.
2. Sinon **étage 1** : RAG `maestro_norms_chunks` filtré `lot` → top-k.
3. Le PDF n'est jamais relu en prod (étage 2 = ingestion seule).

## Garde-fou licence

`exigence` = **paraphrase** d'un fait (un nombre, une condition) — non protégeable.
La prose de la clause DTU l'est : on **cite** `ref`, on ne **recopie** pas. Pour
un DTU payant, cf. `docs/RUNBOOK-DTU-pivot.md §5`.

## Vérification des seuils

Chaque seuil de `dtu_rules.yaml` est **web-vérifié** (2 angles indépendants :
valeur chiffrée + actualité/amendement) avant d'être retenu — cf. workflow
`dtu-rules-draft-verify`. Les règles non corroborées sont écartées (jamais
sorties de mémoire).
