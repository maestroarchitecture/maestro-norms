# Justification normative par lot (expert‑travaux ↔ devis)

> **But.** Relier chaque **lot** du devis Maestro à sa **justification normative** :
> DTU/NF de référence (citation seule) + **Recommandations Professionnelles / Guides
> RAGE‑PACTE‑PROFEEL** (gratuit, plein texte). C'est la base que l'agent
> `expert_travaux` / le devis doit pouvoir **citer par lot**.
>
> Source des lots et `dtu_refs` : `maestro-platform/.../expert_travaux/knowledge.yaml`.
> Données machine : [`docs/lot-norms-mapping.yaml`](lot-norms-mapping.yaml).
> Choix de cadrage : **mapping/plan d'abord** — pas de téléchargement de masse ici.

## Règle de licéité

| Famille | Licence | Traitement |
|---|---|---|
| RAGE / PACTE / PROFEEL | Gratuit, libre de diffusion (financé CEE) | ✅ plein texte → ingestion |
| FFB (Calepins de chantier®, guides) | Réservé adhérents | ❌ citation + lien seulement |
| DTU / NF / Eurocodes | Payant (CSTB / AFNOR) | ❌ citation de la référence |

## Synthèse — couverture par lot

| Lot | Intitulé | DTU/NF (citation) | Reco Pro RAGE (gratuit) | Justification |
|---|---|---|---|---|
| 00 | Installation de chantier | — | — | pratique pro |
| 01 | Démolition / Dépose | — | — | pratique pro |
| 02 | Plâtrerie / Cloisons | DTU 25.41 · 25.42 | ITI (doublage) | **reco pro** |
| 03 | Plomberie / Sanitaires | DTU 60.1 · 60.11 | — | DTU citation |
| 04 | **Chauffage / VMC** | DTU 65.10 · 65.14 · NF DTU 68.3 | **11 guides** (VMC, PAC, ECS, solaire, granulés, planchers) | **reco pro ✓✓** |
| 05 | Électricité | NF C 15‑100 · 14‑100 | Photovoltaïque, GTB | **reco pro** |
| 06 | Menuiseries intérieures | DTU 36.1 · 36.5 | — | DTU citation |
| 07 | **Menuiseries extérieures** | DTU 36.5 · 39 | ITE menuiseries, doubles fenêtres, verrières | **reco pro** |
| 08 | Carrelage / Faïence | DTU 52.1 · 52.2 · NF DTU 55.2 | — | DTU citation |
| 09 | Revêtements de sol | DTU 51.1/51.2 · 53.1/53.2 | — | DTU citation |
| 10 | Peinture / Rev. muraux | NF DTU 59.1 · 59.4 | — | DTU citation |
| 11 | Cuisine / SdB (forfaits) | — | — | forfait |
| 12 | Nettoyage fin de chantier | — | — | pratique pro |

**Lecture :**
- **4 lots** justifiables par Reco Pro **gratuite** : **02, 04, 05, 07** — le **lot 04** est de loin le mieux couvert.
- **5 lots** en **DTU citation seule** (pas de Reco Pro RAGE dédiée) : 03, 06, 08, 09, 10.
- **4 lots** pratique pro / forfait : 00, 01, 11, 12.
- **Enveloppe / ITE / maçonnerie** : guides RAGE existants mais **sans lot finition dédié** (gros œuvre/façade hors lots 00‑12) → bloc `transversal_enveloppe` du YAML.

## Détail des lots couverts par Reco Pro

- **Lot 04 — Chauffage / VMC** (NF DTU 68.3, DTU 65.10/65.14) : VMC double/simple flux (collectif & individuel, neuf & réno), PAC < 50 kW, chauffage+ECS individuel, CESI, chauffe‑eau solaires collectifs, schémathèque granulés, planchers chauffants. *2 URL vérifiées (xpair, jurad‑bat).*
- **Lot 07 — Menuiseries extérieures** (DTU 36.5, 39) : menuiseries avec ITE, doubles fenêtres en réno, verrières.
- **Lot 05 — Électricité** (NF C 15‑100) : systèmes photovoltaïques, GTB (G3090).
- **Lot 02 — Plâtrerie/Cloisons** (DTU 25.41) : ITI / doublage.

## Reste à faire (téléchargement, étape suivante)

1. **Réseau** : ajouter à l'allowlist les domaines encore bloqués ici — **`fcba.fr` (503)** et **`costic.com`** — qui portent une partie des Reco Pro/Guides (ossature bois, planchers chauffants, etc.).
2. **Télécharger** les PDF marqués `statut: liste|page` (résoudre les pages ressources → PDF) et **récupérer** ceux en `statut: indisponible` (verrières) via miroir/archive.
3. **Manifeste** : étendre `manifest.json` avec `type`, `lot`, `dtu_refs[]` pour chaque PDF (schéma du handoff).
4. **Compléter** l'index FFB (titres exacts) si un export adhérent est fourni.

## Articulation avec l'existant

- Ce document **complète/structure par lot** le provisoire
  `maestro-platform/docs/norms-guides-index.md` (branche `claude/weekly-recap-4PfeQ`, PR #9).
  À consolider sur cette branche selon ta décision (mon travail est pour l'instant sur
  `claude/trusting-ramanujan-pFULL`).
- Les **348 PDF AQC/PROFEEL** déjà dans `corpus/` (fiches réglementaires RE2020, autocontrôle,
  mémos chantier…) sont un **corpus complémentaire** : utiles, mais à **tagger `lot`/`dtu_refs`**
  pour entrer dans cette logique de justification.
