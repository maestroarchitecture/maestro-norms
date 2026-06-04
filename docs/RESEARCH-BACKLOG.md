# Backlog de recherche — corpus normatif & intégration devis

> Sujets restant à **rechercher / récupérer / décider** pour finir la base de
> justification normative et son branchement dans l'expert‑travaux / le devis.
> Voir aussi : `docs/lot-norms-mapping.md`, `manifest-rage.json`,
> `maestro-platform/docs/HANDOFF-norms-corpus.md`.
> Màj : 2026-06-04.

## 1. Corpus RAGE/PACTE/PROFEEL à compléter (gratuit, plein texte)

Reco Pro identifiées mais **non récupérables** depuis cet environnement (accès gâté).
Statut détaillé dans `manifest-rage.json › a_recuperer`.

| Sujet | Lot | Source(s) | Bloqueur | Piste |
|---|---|---|---|---|
| **Chaudières à granulés MI** — conception / mise en œuvre / entretien (trilogie COSTIC) | 04 | Pro'Réno, programmepacte, COSTIC, REX‑BP | Pro'Réno = SPA JS ; programmepacte → HTML ; COSTIC = login | Compte COSTIC, ou URL PDF directe, ou machine sans proxy strict |
| Appareils divisé **granulés/bûches** — conception / installation | 04 | programmepacte, Pro'Réno (storage 00404…) | URLs périmées → 404/HTML | idem ; chercher slug exact via cache moteur |
| **Ossature bois / CLT** (FCBA) | 07 | fcba.fr | Certificat TLS rejeté par le proxy egress | Corriger chaîne cert fcba, ou CA côté proxy, ou miroir |
| **ITE enduit sur PSE / sur isolant** | transversal | programmepacte, PROFEEL | programmepacte PDF → HTML | Page PROFEEL « ITE par enduit sur isolant » |
| **GTB — G3090** | 05 | enviroboite.net | Host 503 (egress) | Miroir / autre hub |
| **Verrières 2013‑09** | 07 | reglesdelart‑…fr | Domaine d'origine parqué | web.archive.org (cf. §5) |

## 2. Lots sans Reco Pro mappée — à investiguer

Existe‑t‑il des Reco Pro RAGE/PACTE/PROFEEL (ou guides gratuits) pour ces lots,
aujourd'hui en **DTU citation seule** ?

- **03 Plomberie / Sanitaires** (DTU 60.1/60.11) — ex. réseaux d'eau, ECS.
- **06 Menuiseries intérieures** (DTU 36.1/36.5).
- **08 Carrelage / Faïence** (DTU 52.x, 55.2) — étanchéité sous carrelage (SPEC/SEL).
- **09 Revêtements de sol** (DTU 51.x/53.x).
- **10 Peinture / Ravalement** (NF DTU 59.1, 59.4) — ravalement façade.

## 3. FFB — citation seule (pas de copie)

- Récupérer les **titres exacts des Calepins de chantier®** par corps d'état
  (lots) → nécessite un **export d'un compte adhérent FFB**.
- Compléter l'index FFB de `lot-norms-mapping` (références + liens, sans contenu).

## 4. DTU / NF — citation (payant)

- Confirmer, par lot, les **DTU/NF les plus cités** (les `dtu_refs` de
  `knowledge.yaml` sont une base ; vérifier versions en vigueur / révisions RE2020).
- Pas de plein texte (CSTB/AFNOR payant) → citation de la référence uniquement.

## 5. Guides RAGE 2012 « historiques »

- Récupérer les originaux via **web.archive.org** (CDX) — **bloqué** par l'egress
  (`403 hostname_blocked`). À débloquer : ajouter `web.archive.org` à l'allowlist,
  puis CDX → `…/web/<ts>id_/<url>` → `corpus/rage/`.

## 6. Infra & intégration (technique)

- [ ] **Embeddings du `corpus/rage/`** : les 6 Reco Pro ne sont PAS encore dans
      l'index Supabase (`maestro_norms_chunks` = 3 311 chunks des 348 docs AQC
      seulement). → chunker + embed (Gemini `gemini-embedding-001`) ; **nécessite
      une clé** (régénérer celle exposée).
- [ ] **OCR** du seul PDF image sans texte : `Fiche-Attestations-VDI-PE01-…`.
- [ ] **Brancher `get_norms_for_lot()` dans la génération du devis/CCTP**
      (`maestro_document_agent`) pour citer DTU + Reco Pro par lot — *en cours*.
- [ ] **Réseau** : chaîne TLS `fcba.fr` ; politique vis‑à‑vis du login COSTIC (CGU).
- [ ] **Qualité chunks** : dé‑duplication par `doc_id` au retrieval (chunks
      multiples d'un même doc remontent ensemble).

## 7. Décisions ouvertes

- **Branche** : consolider `claude/trusting-ramanujan-pFULL` → `claude/weekly-recap-4PfeQ` / PR #9.
- **Périmètre des lots pilotes** vs lots complets (00→12) côté `knowledge.yaml`.
- **Sécurité** : régénérer la clé Gemini exposée ; révoquer le token GitHub (handoff §6).
