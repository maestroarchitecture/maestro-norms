# Revue de provenance normative — 26 juillet 2026

Statut : **revue documentaire, sans modification de `dtu_rules.yaml`**  
Périmètre : 50 règles déclarées `verifie` mais rejetées du registre runtime  
Licence : faits paraphrasés et citations seules ; aucune reproduction de DTU

## Décision synthétique

Les 50 rejets ne correspondent pas à 50 erreurs de fond démontrées. Ils se
répartissent en trois cohortes :

| Cohorte | Règles | Décision |
|---|---:|---|
| Validation Namur inscrite et reliée au commit de promotion | 22 | Métadonnées structurées récupérables à partir du commit `4a31b4b` |
| Source primaire publique Legifrance, revue de nouveau le 26/07 | 4 | Trois règles exactes ; une exacte sur le fond mais à nettoyer d'une phrase de confort Maestro avant promotion |
| Lecture Reef déclarée, sans relecteur nommé | 24 | Reste bloqué jusqu'à revue nominative ; ne pas déduire un relecteur de la seule date de lecture |

À ces 50 règles s'ajoutent **26 règles `a_valider_namur`**, et non 16 comme
l'indique encore `docs/liste-courses-reef.md`. Elles ne sont pas comptées dans
les 50 rejets du runtime : lots 02 (3), 05 (14), 07 (2) et 08 (7).

## Cohorte A — 22 validations Namur déjà explicites

Les champs `source` portent littéralement « validé Namur 2026-06-29 ». Le
commit `4a31b4b`, auteur `namurmatos`, est intitulé
« promotion des 5 DTU prioritaires au registre live (validation Namur) ».

Le handoff du début de session indiquait encore que les règles attendaient la
validation ; le commit de promotion, postérieur, clôt ce point. La conversion
proposée est donc purement structurante :

- `source_type: primaire` ;
- `edition`: édition déjà portée par `ref` ;
- `localisateur`: code Reef et paragraphes déjà portés par `source` ;
- `reviewed_by: Namur` ;
- `reviewed_at: 2026-06-29`.

Règles concernées :

- lot 02 : règles 7 à 9 — Reef `AETD-2`, NF DTU 25.42 ;
- lot 03 : règles 2 à 8 — Reef `AESM-1`, NF DTU 60.1 P1-1-3 ;
- lot 04 : règles 8 à 10 — Reef `AEZJ-2`, NF DTU 68.3 P1-1-1 ;
- lot 06 : règles 5 et 6 — Reef `AHHV-2`, NF DTU 36.2 P1-1 ;
- lot 08 : règles 2 à 5 — Reef `ABEW-2`, NF DTU 26.2 P1-1 ;
- lot 09 : règles 2 à 4 — Reef `ALWL-1`, NF DTU 53.12 P1-1-1.

**Décision proposée : acceptables pour migration de métadonnées**, sans
nouvelle modification de fond. Le commit `4a31b4b` doit être conservé dans la
preuve d'audit comme racine de la revue.

## Cohorte B — quatre règles ventilation relues sur Legifrance

Source primaire consolidée :

- arrêté du 24 mars 1982, article 3 :
  `LEGIARTI000006830557`, version en vigueur depuis le 27 mars 1982 ;
- arrêté du 24 mars 1982, article 4 :
  `LEGIARTI000006830558`, version en vigueur depuis le 15 novembre 1983,
  modifiée par l'arrêté du 28 octobre 1983.

### Lot 04, règle 1 — cuisine

**Décision documentaire : conforme.**

La série 75 / 90 / 105 / 120 / 135 m³/h pour 1 / 2 / 3 / 4 / 5 pièces
principales et plus correspond au tableau de l'article 3. La réserve relative à
une hotte raccordée est également portée par cet article.

Métadonnées proposées :

- `source_type: primaire`
- `edition: version consolidée en vigueur depuis le 27/03/1982`
- `localisateur: Legifrance LEGIARTI000006830557, article 3, tableau`

### Lot 04, règle 2 — salle de bains ou douche

**Décision documentaire : conforme sous réserve éditoriale.**

Les minima 15 m³/h pour 1 à 2 pièces et 30 m³/h à partir de 3 pièces sont
corrects. La valeur de 15 m³/h pour une autre salle d'eau est également
correcte.

La phrase citant un exemple Maestro à 75 m³/h n'est pas une disposition de
l'arrêté. Elle doit être retirée de la règle normative ou déplacée dans une
politique de confort distincte avant promotion.

Métadonnées proposées après nettoyage :

- `source_type: primaire`
- `edition: version consolidée en vigueur depuis le 27/03/1982`
- `localisateur: Legifrance LEGIARTI000006830557, article 3, tableau`

### Lot 04, règle 3 — cabinet d'aisances

**Décision documentaire : conforme.**

Les valeurs WC unique/multiple et le cas de la sortie commune dans un logement
d'une pièce correspondent au tableau et aux précisions de l'article 3.

Métadonnées proposées :

- `source_type: primaire`
- `edition: version consolidée en vigueur depuis le 27/03/1982`
- `localisateur: Legifrance LEGIARTI000006830557, article 3, tableau et alinéa suivant`

### Lot 04, règle 4 — débits réduits

**Décision documentaire : conforme.**

Les deux séries de débits réduits correspondent à l'article 4 consolidé. La
réduction automatique reste conditionnée à une autorisation ministérielle.

Métadonnées proposées :

- `source_type: primaire`
- `edition: version consolidée en vigueur depuis le 15/11/1983`
- `localisateur: Legifrance LEGIARTI000006830558, article 4, tableaux`

**Arbitrage requis avant écriture :** désigner le relecteur humain autorisé et
la date de revue. La vérification documentaire Codex du 26/07 n'est pas
transformée automatiquement en approbation métier.

## Cohorte C — 24 lectures primaires sans relecteur nommé

La date et le localisateur de lecture sont présents dans les chaînes `source`,
mais aucune mention ne permet d'attribuer honnêtement `reviewed_by`.

| Lot | Nombre | Sources principales |
|---|---:|---|
| 02 | 6 | Reef `ABCR-5`, NF DTU 25.41 |
| 03 | 1 | Reef `AESP-1`, NF DTU 60.11 |
| 04 | 3 | Reef `ALUF-1` et `ANVY-1`, NF DTU 24.1 et 65.14 |
| 05 | 1 | Reef `ALR-1`, DTU 70.1 — source/édition/localisateur déjà structurés |
| 06 | 4 | Reef `AHHV-2`, NF DTU 36.2 |
| 07 | 6 | Reef `ABKY-1`, `ABKZ-1`, `ACJL-1`, NF/FD DTU 36.5 |
| 08 | 1 | Reef `ABQO-3`, NF DTU 52.2 |
| 09 | 1 | Reef `ABYY-4`, NF DTU 51.2 |
| 10 | 1 | Reef `AEZO-2`, NF DTU 59.1 |

Décision : **maintenir rejetées** jusqu'à ce qu'un relecteur autorisé confirme
chaque groupe depuis l'exemplaire licite correspondant.

## Ordre de revue recommandé

1. Migrer les métadonnées des 22 règles rattachées au commit `4a31b4b`.
2. Nommer le relecteur des quatre règles Legifrance et nettoyer la règle
   salle de bains.
3. Revoir la règle DTU 70.1 du lot 05, presque complète.
4. Traiter les 23 autres lectures Reef par document, et non règle par règle :
   une lecture peut couvrir plusieurs règles partageant le même code Reef.
5. Ouvrir ensuite le chantier distinct des 26 règles `a_valider_namur`.

## Critère de promotion

Une règle ne rejoint le runtime que si les cinq champs sont présents et
documentés : `source_type`, `edition`, `localisateur`, `reviewed_by`,
`reviewed_at`. La présence d'une source et d'une date de lecture ne vaut pas à
elle seule revue métier.
