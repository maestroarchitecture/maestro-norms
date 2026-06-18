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
| Ossature bois ✅ / **CLT** (FCBA) | 07 | fcba.fr, **cndb.org** | fcba = cert TLS ; façade ossature bois **obtenue via cndb.org** | CLT : miroir / cndb |
| **ITE enduit sur PSE / sur isolant** | transversal | programmepacte, PROFEEL | programmepacte PDF → HTML | Page PROFEEL « ITE par enduit sur isolant » |
| **GTB — G3090** | 05 | enviroboite.net | Host 503 (egress) | Miroir / autre hub |
| **Verrières 2013‑09** | 07 | reglesdelart‑…fr | Domaine d'origine parqué | web.archive.org (cf. §5) |

## 2. Lots sans Reco Pro — investigué ✅ (conclusion)

Recherche faite (RAGE/PACTE/PROFEEL) : **pas de Reco Pro gratuite dédiée** pour
ces lots → **DTU/CSTB citation seule** (classification du mapping confirmée).

- **03 Plomberie / Sanitaires** (DTU 60.1/60.11) — le corpus « eau » RAGE est côté chauffage/ECS (lot 04), pas plomberie sanitaire.
- **06 Menuiseries intérieures** (DTU 36.1/36.5) — rien de spécifique.
- **08 Carrelage / Faïence** (DTU 52.x, 55.2) — étanchéité pièces humides = **SPEC/SEL → CSTB Cahier 3756** (CPT, citation) ; pas de Reco Pro RAGE.
- **09 Revêtements de sol** (DTU 51.x/53.x) — rien.
- **10 Peinture / Ravalement** (NF DTU 59.1, 59.4) — rien.

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

## 8. Référentiels & enrichissement externes (BDNB / CSTB / BNTEC)

Sources publiques identifiées pour **enrichir l'intake** et **étendre la justification**.
Accès **vérifié** en session. À prototyper.

| Source | Données | Accès (vérifié) | Où câbler |
|---|---|---|---|
| **BDNB** | Bâtiment : `annee_construction`, classe **DPE**, inertie, commune/IRIS, **adresse BAN**, arrêté 2021… (400+ champs) | ✅ **API PostgREST OUVERTE** : `GET https://api.bdnb.io/v1/bdnb/donnees/batiment_groupe_complet?<filtre>` (ex. `code_departement_insee=eq.75`). Gratuit, sans clé. *Testé → renvoie un bâtiment réel.* | **`BDNBLookup`** (cf. `price_lookup.py`) → intake `profiler`/`collector` → pré‑remplir `ProjetUnifie` (adresse → année/type/DPE) |
| **CSTB — Avis Techniques / Certificats / Ecoscale** | Validation **produits/procédés** (ATec, NF/QB) | Reachable (`database.cstb.fr` 302) ; **accès = recherche web** (pas d'API confirmée) → à scraper/cadrer | **`CSTBLookup`** → `compliance_agent`/`expert_travaux` : vérifier qu'un produit/procédé du devis est sous **ATec/certif** (assurabilité décennale) |
| **BNTEC → Norminfo AFNOR** | Catalogue **NF/DTU** : réf, titre, statut *en vigueur*, remplacements (métadonnées) | Norminfo joignable (200) ; **pas d'API/URL propre trouvée** (recherche SPA) ; plein texte DTU **payant** | **Back‑office norms** (PAS un agent runtime) : valider/rafraîchir `knowledge.yaml › dtu_refs` + veille « travaux en cours » BNTEC |
| **Batipedia** (CSTB) | **Reef** = plein texte DTU/NF (payant) · **`/atec`** = Avis Techniques (**GRATUIT**) · Bati CCTP (payant) | Reef/CCTP : login payant → **citation seule**. **`/atec` : recherche publique + export** — `POST /atec/services/recherche.html?searchProduct=ATEC`, `/atec/recherche/export.txt` (formulaire avec jetons `__fp`/`_sourcePage` + session ; robots : `crawl-delay 10`, `/atec/pdf/` interdit) | **Reef → citer** ; **`/atec` → EXTRACTIBLE → `CSTBLookup`** (assurabilité, = ligne CSTB ci-dessus) |

**Licences** : BDNB = open data · CSTB ATec/Certif = gratuit (consultation) · DTU plein texte = payant → **citation seule** (politique en place).

**Prochaines actions** :
1. ✅ **`BDNBLookup` prototypé** — API PostgREST + injection `orchestrator._trigger_fusion` (opt-in `ENABLE_BDNB_ENRICHMENT`), 9 tests → **PR #27**.
2. Cadrer l'accès **CSTB** (ATec/Certif) → `CSTBLookup` pour l'**assurabilité** par lot/poste.
3. Vérifier l'accès **Norminfo** (recherche/export) → script de validation des `dtu_refs`.

> Valeur : BDNB `année`+`type` → alimente directement `compliance_agent` + notre `norms_by_lot`
> (RT2012 vs RE2020 → quels DTU/Reco Pro). CSTB ATec = couche **assurabilité** au‑dessus.
