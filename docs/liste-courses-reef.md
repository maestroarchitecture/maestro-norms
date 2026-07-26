# Liste de courses Reef — session licenciee Namur (Batipedia)

Generee le 2026-07-09 a partir du catalogue canonique `maestro-norms/normes-par-lot.yaml`
(consolidation des 4 recensements de groupe) et du registre `maestro-norms/dtu_rules.yaml`.

Objectif de la session : lire les sources PRIMAIRES au Reef (citation seule, jamais de
copie de prose), promouvoir les entrees `a_valider_namur` en `verifie`, et lire les
references candidates du lot 12 avant toute inscription dans le registre vivant.

Rappel protocole registre : source primaire lue verbatim -> fait paraphrase
{exigence, seuil, condition, ref} -> statut `verifie` -> allowlist `check_dtu_refs.py`.

Deux statuts vivent dans le registre, a ne pas confondre :
- `verifie`         : source PRIMAIRE lue et recoupee -> seuil chiffre autorise, citable client.
- `a_valider_namur` : seuil ecrit depuis une source SECONDAIRE, en attente de confirmation.
Les references `a_verifier` restent dans `normes-par-lot.yaml` ou
`dtu_rules.draft.yaml` : le lecteur du registre vivant ne filtre pas le statut.

MISE A JOUR DU 26/07/2026 — travaux hors Reef DEJA FAITS, a ne pas refaire :
- Lot 12 catalogue : 10 references candidates recensees sans un seul chiffre
  (NF DTU 20.1, 20.13, 21, 13.1, 13.3, 26.1, Eurocodes 1/6/7, NF P 94-500).
  Elles restent HORS du registre vivant jusqu'a lecture de la source primaire.
- Coquille « NF DTU 52.11 » corrigee A LA SOURCE (savoir de chiffrage du lot 08, version
  lisible et version machine) : la reference exacte est NF DTU 52.10, juin 2013, indice de
  classement P 61-203, verifie sur les fiches publiques de la boutique AFNOR.
- NF DTU 53.1 et 53.2 marques ANNULES-REMPLACES par le NF DTU 53.12 (decembre 2020) dans le
  savoir de chiffrage du lot 09 et dans le mapping ; ils ne subsistent qu'en repere historique.
- Travail en hauteur : la formule « protection collective obligatoire au-dela de 3 m » est
  FAUSSE et a ete retiree du catalogue. Les trois articles R4323-58, R4323-59 et R4323-60 y
  sont desormais decrits pour ce qu'ils disent reellement (lus sur Legifrance le 26/07/2026).
  Aucune lecture Reef n'est necessaire : ces textes sont gratuits sur Legifrance.

---

## 0. AVANT TOUT : les 16 entrees du registre en `a_valider_namur` a confirmer

Ce sont les entrees DEJA ecrites dans `dtu_rules.yaml` qui attendent leur confirmation
sur source primaire (ou l'arbitrage Namur). Les purger en priorite : elles bloquent
des postes existants.

### Lot 02 — Platrerie (3 entrees du 08/07 soir, source secondaire fiche FFB)
1. NF DTU 58.1 (plafond suspendu modulaire) — confirmer le domaine d'emploi (plenum <= 6 m) sur le texte Reef (edition mai 2019).
2. NF DTU 25.51 (plafond staff) — confirmer l'absence de PV standardise pour la variante acoustique sur le texte Reef (mai 2011 + A1 mars 2018).
3. NF DTU 45.11 (soufflage combles) — ATTENTION : relire sur la NOUVELLE edition novembre 2025 (le registre a ete redige sur la base de l'edition 2020 via fiche FFB) : humidite 5 g/m3, piges, arretoirs, deflecteurs, etiquette.

### Lot 05 — Electricite (4 entrees du 08/07, sources Schneider/Promotelec — HORS Reef)
La NF C 15-100 n'est PAS dans le Reef : ces confirmations passent par l'ACHAT du texte
officiel AFNOR (serie 2024) ou par un arbitrage Namur assumant les sources secondaires.
4. ETEL/GTL : dimensions mini (600 x 250 mm, hauteurs 0,50-1,80 m) — §10.1.7.
5. Liaison equipotentielle supplementaire salle d'eau : 2,5 mm2 protege / 4 mm2 non protege — §544.2.
6. Parafoudre residentiel : IdF = AQ1, non obligatoire sauf paratonnerre — Tableau 10-1H (reserve : niveau keraunique par departement a confirmer).
7. Volumes 0/1/2 salle d'eau + IP minimaux — partie 7-701 et Tableau 10-1C.

### Lot 07 — Menuiseries exterieures (2 entrees du 09/07, sources primaires PUBLIQUES deja lues)
Pas de lecture Reef necessaire : textes Legifrance/ecologie.gouv.fr deja lus integralement.
Il ne manque que la VALIDATION NAMUR (arbitrage obligation vs condition d'aide deja cadre le 09/07).
8. Arrete du 3 mai 2007 art. 9 (RT existant) : Uw <= 1,9 obligation au remplacement.
9. Fiche CEE BAR-EN-104 v. A54-2 + arrete du 17/11/2020 art. 9 : seuils d'aide Uw/Sw.

### Lot 08 — Carrelage (7 entrees du 08/07, sources secondaires)
10. NF DTU 52.2 : simple vs double encollage selon local/format/porosite — a confirmer sur Reef ABQO-3 (edition juin 2022).
11. NF DTU 52.2 : classes de mortier-colle C1/C2, S1/S2 selon support et format — Reef ABQO-3.
12. SPEC classes d'exposition EA->EC + domaine d'emploi — croiser e-Cahier 3756_V3 (public, deja lu) avec la nouvelle partie P1-1-4 du NF DTU 52.2 (Reef) ; verifier aussi la version du classement des locaux (3567_V2 de novembre 2021, le registre cite encore 2006).
13. SPEC/SEL dispositions chiffrees (releve >= 5 cm, debord >= 20 cm, planeite) — croiser 3756_V3 §7.2 avec NF DTU 52.2 P1-1-4 (Reef).
14. NF DTU 52.1 : epaisseurs nominales du mortier de scellement (§7.3.1/7.3.2) — Reef, code a ouvrir.
15. NF DTU 52.1 : joints de fractionnement et peripheriques (§8.3/8.4) — Reef.
16. NF DTU 52.1 : tolerances de planeite support et ouvrage fini (§6.3/§10.1) — Reef.

---

## 1. PRIORITE HAUTE — textes payants a ouvrir au Reef (seuils de chiffrage manquants)

### Lot 02 — Platrerie - Cloisonnement
- NF DTU 45.11 (edition novembre 2025) — chercher « NF DTU 45.11 » dans Batipedia.
  Extraire : conditions d'interdiction du soufflage (humidite du comble), obligations de chantier chiffrees (piges, deflecteurs, distances aux conduits de fumee).
  Registre : a_valider_namur (entree 3 ci-dessus) — a confirmer sur la nouvelle edition.

### Lot 03 — Plomberie - Sanitaires
- NF DTU 60.11 P2 (aout 2013) — chercher « NF DTU 60.11 » (le P1-1 est deja lu : Reef AESP-1).
  Extraire : diametres minimaux d'evacuation par appareil sanitaire (tableaux P2) + pentes associees.
  Registre : absent (seul le Tableau 1 alimentation P1-1 est verifie).

### Lot 04 — Chauffage - Ventilation - Climatisation
- NF DTU 65.16 (juin 2017) — chercher « NF DTU 65.16 ».
  Extraire : exigences chiffrees d'installation PAC (dimensionnement par deperditions, volume tampon/inertie annexe J, distances et supports unite exterieure).
  Registre : absent.

### Lot 05 — Electricite (HORS Reef — geste separe)
- NF C 15-100 serie 2024 — ACHAT AFNOR (pas dans Batipedia/Reef).
  Extraire : confirmation des 4 entrees a_valider_namur (section 0) + nouveautes 2024 du TODO registre (DDR type F pour PAC/clim, detecteurs d'arc DPDA, partie 7-722 IRVE).
  Registre : 4 entrees a_valider_namur + TODO explicite en meta.

### Lot 07 — Menuiseries exterieures
- FD DTU 36.5 P3 (octobre 2010) — chercher « FD DTU 36.5 P3 » (Reef ACJL-1, deja ouvert le 19/06).
  Extraire : la combinaison Tableau 8 pour l'Ile-de-France (region x terrain x hauteur) pour deriver la classe AEV par defaut des briques fenetres — puis faire valider Namur avant de la figer.
  Registre : le principe (Tableaux 5/6/7/8) est verifie ; la derivation IdF est [a completer] en KB.

### Lot 08 — Carrelage - Faience
- NF DTU 52.2 (juin 2022) — chercher « NF DTU 52.2 » (Reef ABQO-3).
  Extraire : confirmation encollage + classes de colle (entrees 10-11) + contenu de la nouvelle partie P1-1-4 SPEC (articulation avec CPT 3756_V3/3788).
  Registre : 4 entrees a_valider_namur a promouvoir.
- NF DTU 52.1 (fevrier 2020) — chercher « NF DTU 52.1 » (code Reef a ouvrir).
  Extraire : confirmation epaisseurs de scellement, joints, tolerances (entrees 14-16).
  Registre : 3 entrees a_valider_namur a promouvoir.

### Lot 09 — Revetements de sols
- NF DTU 53.12 (decembre 2020) — chercher « NF DTU 53.12 ».
  Extraire : tolerances de planeite du support et conditions de pose par famille (PVC, textile, lino) ; en profiter pour migrer les citations presets 53.1/53.2 (annules) vers 53.12.
  Registre : 3 seuils support verifies ; complements absents.
- NF DTU 51.11 (mai 2024) — chercher « NF DTU 51.11 ».
  Extraire : seuil d'humidite du support en pose flottante + exigences sous-couche/pare-vapeur — pose PAR DEFAUT des presets, aucun seuil au registre.
  Registre : absent (dans l'allowlist sans aucun seuil = anomalie a corriger en priorite).

### Lot 10 — Peinture
- NF DTU 59.1 (juin 2013) — chercher « NF DTU 59.1 ».
  Extraire : definitions normatives des etats de finition A/B/C, nombre maximal de teintes sans plus-value, regles de rechampis — les trois [a completer] de la KB.
  Registre : 1 seule regle verifiee (conditions hygrothermiques §7.1).

### Lot 12 — Maconnerie - Gros oeuvre - Structure (registre a alimenter apres lecture)
- Mise a jour R1 du 26/07/2026 : huit candidats de controles d'execution ont ete
  documentes dans `maestro-platform/docs/audits/2026-07-26-experts-metier/08-preuves/R1-lot12-maconnerie.yaml`.
  Ils proviennent de guides publics locaux RAGE/AQC et restent `a_valider_namur` :
  ils ne constituent ni une lecture primaire des editions ci-dessous ni une autorisation
  de promotion. Au Reef, controler en priorite les renvois P1-1/P1-2/P4 et les clauses
  indiquees dans le fichier de preuve ; conserver les gardes BET avant toute reutilisation.
- NF DTU 20.1 (juillet 2020) — chercher « NF DTU 20.1 » (verifier P1-1 + P3).
  Extraire : epaisseurs minimales des murs selon exposition, regles de chainages, mortiers de montage — socle du nouveau bloc 12.
  Registre : absent.
- NF DTU 13.1 (septembre 2019) — chercher « NF DTU 13.1 ».
  Extraire : profondeur hors gel, dimensions minimales de semelles, exigences de reconnaissance de sol — re-sourcage des ordres de grandeur du Memo AQC.
  Registre : absent.
- NF DTU 26.1 (avril 2008) — chercher « NF DTU 26.1 ».
  Extraire : epaisseurs d'enduit par type, nombre de passes, delais entre couches, preparation des supports anciens (meuliere/moellon).
  Registre : absent.

---

## 2. PRIORITE MOYENNE — a ouvrir si le temps de session le permet

### Lot 02 — Platrerie - Cloisonnement
- NF DTU 25.42 (dec. 2012 + A1 avril 2026) — extraire les nouvelles epaisseurs d'isolant admises par l'A1 (PSE 160 mm, PU 140 mm) et le biseautage en tableau de baie. Registre : seuils verifies sur base 2012 (Reef AETD-2), A1 non lu.
- NF DTU 25.31 (avril 2017) — extraire les regles cloisons carreaux de platre (hauteurs limites, hydrofuge pieces humides). Registre : absent.
- NF DTU 25.51 (mai 2011 + A1 2018) — confirmer l'entree staff a_valider_namur (section 0). Registre : a_valider_namur.

### Lot 03 — Plomberie - Sanitaires
- NF DTU 60.1 P1-1-1 et P1-1-2 (dec. 2012) — extraire les regles reseaux (alimentation, evacuation) non couvertes par le P1-1-3 deja lu. Registre : verifie partiel (P1-1-3 seul).
- NF DTU 60.5 (dec. 2007) — extraire supports/faconnage/incorporation du cuivre. Registre : absent.
- NF DTU 60.33 (oct. 2007) — extraire pentes et ventilation de chute PVC. Registre : absent.

### Lot 04 — Chauffage - Ventilation - Climatisation
- NF DTU 68.3 P1-1-2 et P1-1-4 (2013/2017) — extraire le dimensionnement VMC simple flux et les exigences double flux. Registre : verifie partiel (P1-1-1 seul).
- NF DTU 24.1 P1-1-2 (sept. 2020) — extraire les exigences appareils gaz type B (si postes gaz). Registre : verifie partiel (P1-1-1 seul, Reef ALUF-1).
- NF DTU 61.1 (juin 2010) — extraire les regles de mise en oeuvre gaz citees par le savoir FFB (detalonnage 2 cm, amenee d'air). Registre : absent.

### Lot 06 — Menuiseries interieures - Agencement
- NF DTU 36.2 (novembre 2025) — extraire la hauteur de detalonnage chiffree ([a completer] en KB). Registre : 6 regles verifiees (Reef AHHV-2), detalonnage manquant.

### Lot 07 — Menuiseries exterieures
- NF DTU 39 P4 + FD P5 (2006/2017) — extraire epaisseurs de vitrage et cas de vitrage de securite obligatoire (alleges basses, portes vitrees). Registre : absent.
- NF DTU 34.4 (sept. 2013 + FD P3 2015) — extraire les regles de pose volets roulants/stores citees par la fiche FFB motorisation. Registre : absent (hors allowlist).
- NF P 01-012 (revision novembre 2024) — extraire les dimensions garde-corps applicables aux alleges basses apres remplacement de fenetre. Registre : absent.

### Lot 08 — Carrelage - Faience
- NF DTU 26.2 A1 (mai 2015) — verifier que l'A1 ne modifie pas les seuils chapes deja verifies et dater l'A1 au registre. Registre : verifie (base avril 2008, Reef ABEW-2).
- NF DTU 52.10 (juin 2013, indice de classement P 61-203) — extraire les regles sous-couches isolantes sous chape ou dalle flottantes et sous carrelage scelle (acoustique copropriete). Registre : absent. Coquille « 52.11 » : CORRIGEE A LA SOURCE le 26/07/2026 dans le savoir de chiffrage du lot 08 (versions lisible et machine) ; reste a purger toute occurrence de « 52.11 » dans la base de connaissance du lot 08 cote moteur.

### Lot 09 — Revetements de sols
- NF DTU 51.2 (mars 2023) — completer tolerances et regles supports chauffants du parquet colle. Registre : verifie partiel (humidite <= 3 %).
- NF DTU 53.12 (decembre 2020) — POINT PRECIS A VERIFIER, ajoute le 26/07/2026 : quelle METHODE DE MESURE de l'humidite du support le 53.12 retient-il ? Le savoir de chiffrage du lot 09 tenait de l'ex-NF DTU 53.1 (annule) que « seule la bombe a carbure » etait admise ; cette affirmation est desormais etiquetee NON VERIFIEE et ne doit pas etre presentee comme opposable avant lecture du 53.12.

### Lot 10 — Peinture
- DTU 59.4 (fevrier 1998) — extraire preparation des supports et conditions de pose toile de verre/revetements muraux ; ATTENTION revision en cours (PR NF DTU 59.4) : verifier avant d'investir. Registre : absent.
- NF DTU 42.1 (novembre 2007) — extraire classes d'impermeabilite I1-I4 et preparation des supports (regulariser la citation du devis ESPARON). Registre : absent.

### Lot 12 — Maconnerie - Gros oeuvre - Structure
Depuis le 26/07/2026 ces textes sont catalogues dans `normes-par-lot.yaml`, mais restent
absents du registre vivant. La lecture Reef sert a produire une regle paraphrasee avec
clause exacte et source, directement au statut `verifie`.
- NF DTU 20.13 (oct. 2008 + A1 2016) — extraire hauteurs/epaisseurs limites des cloisons maconnees. Registre : absent.
- NF DTU 21 (juin 2017) — extraire tolerances d'execution des petits ouvrages beton (linteaux, reprises). Registre : absent.
- NF DTU 13.3 (dec. 2021) — extraire epaisseurs minimales de dallage maison individuelle (P1-1-2). Registre : absent.
- NF P 94-500 (nov. 2013) — confirmer le routage G1-G5 depuis un exemplaire licite et tracable. Registre : absent.
- NF DTU 23.5 (mai 2019, planchers a poutrelles) — present au catalogue et au mapping du lot 12, PAS au registre : a ajouter si un chantier plancher se presente.
RAPPEL BLOQUANT : aucune entree du lot 12 ne rejoint le registre avant lecture primaire.
On n'ecrit de memoire AUCUN chiffre — ni epaisseur, ni profondeur hors gel, ni dimension de semelle, ni dosage. Et la
regle metier ne bouge pas : l'expert ne dimensionne jamais une structure a distance.

---

## 3. Rappels de session

- Citation seule : on paraphrase des FAITS chiffres {exigence, seuil, condition, ref}, jamais la prose du texte.
- Chaque lecture -> entree `dtu_rules.yaml` avec `source` (code Reef + clause + date de lecture) -> puis extension de l'allowlist `check_dtu_refs.py` AVANT toute citation en description client.
- Textes GRATUITS (Legifrance, RAGE/PACTE, e-Cahiers CSTB publics, regles pro FFB) : ne pas consommer de temps Reef dessus — voir `normes-par-lot.yaml` (priorite_reef: basse).
- Le registre ne filtre PAS le statut a la lecture : tout ce qui y figure peut etre repris tel
  quel dans un document. Une entree `a_verifier` reste donc obligatoirement hors du registre
  vivant. Un outil client ne doit retenir que les entrees `verifie`.
- Nettoyages hors Reef — ETAT AU 26/07/2026 :
  - FAIT : coquille « NF DTU 52.11 » -> NF DTU 52.10 (savoir de chiffrage lot 08, 2 fichiers).
  - FAIT : NF DTU 53.1 / 53.2 declares annules-remplaces par le 53.12 (savoir lot 09 + mapping).
  - FAIT : mapping — lot 12 renomme « Maconnerie - Gros oeuvre - Structure », nettoyage de fin
    de chantier deplace au lot 00.
  - FAIT : travail en hauteur — R4323-58/59/60 decrits exactement, formule des « 3 m » corrigee.
  - FAIT : migration de l'allowlist, du catalogue et des presets actifs 53.1/53.2 -> 53.12 ;
    purge des occurrences actives de « 52.11 » dans la base de connaissance du lot 08.
  - RESTE : e-Cahier 3567 -> 3567_V2 (nov. 2021) ; ne plus citer l'arrete du 22 mars 2004 (feu, abroge
    par l'arrete du 22 mars 2026) ; regeneration complete du mapping sur les 13 lots (lot 06 :
    NF DTU 36.1 annule et NF DTU 36.5 mal range ; lot 08 : NF DTU 55.2 hors perimetre ;
    lot 04 : DTU 65.10 annule ; lot 11 : intitule perime ; lots 00 et 01 : reglementaire
    transverse absent).
