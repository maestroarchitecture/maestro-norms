# Changelog

Évolutions notables de la base de normes Maestro (`maestro-norms`).
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/).

## [Non publié] — 2026-06-29

### Ajouté — Intégration de la documentation FFB (accès adhérent, citation seule)
- **Répertoire FFB « Techniques du bâtiment »** (`docs/ffb-techniques-index.yaml` + `.md`) :
  693 documents techniques indexés et classés par lot Maestro (titre + type + lien).
  Contenu adhérent protégé → **références seules, aucun texte recopié**.
- **Plan d'enrichissement du registre** (`docs/ffb-enrichment-plan.md`, `docs/ffb-gap-analysis.json`) :
  27 DTU manquants priorisés, par recoupement des guides FFB avec `dtu_rules.yaml`.
- **Savoir de chiffrage par lot** (`docs/ffb-savoir-chiffrage-lot02..10.md` + `…-INDEX.md`, JSON associés) :
  pour chaque sous-poste — périmètre (inclus/exclu), facteurs de prix, règles de métré,
  points de vigilance, matériaux, normes. **Reformulé** depuis la doc FFB : aucun verbatim,
  aucun seuil chiffré inventé.

### Ajouté — Enrichissement du registre DTU (brouillon, à valider)
- **`dtu_rules.draft.yaml`** : 22 règles tirées des 5 DTU prioritaires (NF DTU 60.1 P1-1-3,
  26.2 P1-1, 25.42 P1-1, 53.12 P1-1-1, 68.3 P1-1-1) + bonus NF DTU 36.2 §6.9, **lues à la
  source primaire (Reef)**. Toutes en `statut: a_verifier`, chaque seuil portant sa clause
  source. **Fichier volontairement séparé** du registre live (`dtu_rules.yaml` n'est pas
  filtré sur le statut) : promotion vers le registre + mise à jour de l'allowlist de
  `check_dtu_refs.py` **seulement après validation (licence)**.

### Outillage & qualité (suite revue Codex)
- **`tools/check_dtu_draft.py`** (NOUVEAU) : valide `dtu_rules.draft.yaml` (6 champs, lot 00..12,
  statut autorisé, source non vide, pas de placeholder) et `--emit` les règles `verifie` prêtes à
  insérer dans le live (promotion **non destructive**, ne touche pas au fichier commenté).
- **`docs/ffb-techniques-index.yaml`** restructuré : séparation `lots:` (00..12, lots de devis) /
  `categories:` (META, REGL, `--` transversales) — un consommateur filtrant par lot ne lit plus que `lots`.

### Notes
- Politique **citation seule** maintenue (FFB et DTU : faits paraphrasés, jamais de verbatim).
- 6 références à ajouter à l'allowlist `check_dtu_refs.py` lors de la promotion :
  NF DTU 25.42, 26.2, 36.2, 53.12, 60.1, 68.3.
