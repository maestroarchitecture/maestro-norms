# maestro-norms — corpus de normes & règles de l'art (bâtiment FR)

Corpus documentaire **technique et normatif** (PDF) servant de base de
connaissances RAG à la plateforme Maestro. Les documents sont des publications
**publiques** de l'**Agence Qualité Construction (AQC)** et du **Programme
PROFEEL**, téléchargées depuis leurs sites officiels puis indexées.

> ℹ️ Ce dépôt agrège des documents **sous droits d'auteur** à des fins
> documentaires internes. Il ne s'agit pas d'un miroir officiel. Voir la
> section [Licences & droits](#licences--droits).

## Contenu

| Source | Organisation | Dossier | Fichiers |
|---|---|---|---|
| `qualiteconstruction.com` | Agence Qualité Construction (AQC) | `corpus/aqc/` | 334 |
| `programmeprofeel.fr` | Programme PROFEEL | `corpus/profeel/` | 14 |
| **Total** | | `corpus/` | **348** (≈ 625 Mo) |

L'inventaire complet, horodaté et vérifiable, est dans [`manifest.json`](manifest.json) :
chaque entrée porte le chemin, l'URL source, le titre, la date d'origine, le
type MIME, la date de téléchargement et l'**empreinte SHA-256**.

## Critères de sélection

Seul le **sous-ensemble technique/normatif** est collecté. Sont **exclus** :
communiqués de presse, plaquettes commerciales, offres de recrutement,
concours photo, replays d'événements, conventions, dépliants.

**Familles incluses (AQC)** : Fiches pathologie du bâtiment · Mémos Chantier ·
Rapports REX Bâtiment Performant · Fiches qualité réglementaire (séries
B→H : RE2020, acoustique, accessibilité, ventilation, structure…) · Fiches
réception & autocontrôle (PROFEEL) · Fiches interfaces · Fiches prévention ·
Fiches maîtrise d'ouvrage · Fiches attestation d'essais · Guides pratiques ·
Recommandations professionnelles · Calepins de chantier.

**Familles incluses (PROFEEL)** : fiches **RENOSTANDARD** (typologies & projets
de maisons individuelles).

## À propos des guides RAGE 2012

Le dossier `corpus/rage/` initialement envisagé **n'a pas été créé** : les
guides *RAGE — Règles de l'Art Grenelle Environnement 2012* ne sont plus
disponibles en ligne. Le domaine dédié
`reglesdelart-grenelle-environnement-2012.fr` est aujourd'hui reparqué (0 PDF),
et ces guides ne figurent ni dans la médiathèque de l'AQC ni dans celle de
PROFEEL. La structure retenue est donc **`corpus/aqc/` + `corpus/profeel/`**.
Une récupération via archive web (Wayback Machine) reste possible si besoin.

## Intégrité

```bash
# Vérifier que les fichiers correspondent au manifeste
python3 - <<'PY'
import json, hashlib, pathlib
m = json.load(open("manifest.json"))
bad = 0
for f in m["files"]:
    p = pathlib.Path(f["path"])
    h = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    if h != f["sha256"]:
        bad += 1; print("MISMATCH", f["path"])
print("OK" if not bad else f"{bad} fichier(s) en écart", "/", len(m["files"]))
PY
```

## Reconstruction

Le corpus est reproductible : énumération des médias via l'API REST WordPress
(`/wp-json/wp/v2/media?mime_type=application/pdf`) des deux sites, filtrage par
familles documentaires (voir ci-dessus), téléchargement avec validation de
l'en-tête PDF et calcul SHA-256.

## Licences & droits

Les documents de ce corpus **ne sont pas en domaine public** et **ne sont pas
sous licence libre**. Ils restent la propriété de leurs éditeurs respectifs :

- **AQC** — © Agence Qualité Construction. Documents diffusés gratuitement sur
  [qualiteconstruction.com](https://qualiteconstruction.com) à destination des
  professionnels de la construction. Toute reproduction ou rediffusion publique
  relève des conditions de l'AQC et requiert en principe son autorisation.
- **PROFEEL** — © Programme PROFEEL et ses partenaires (AQC, organisations
  professionnelles et techniques du bâtiment). Documents diffusés gratuitement
  sur [programmeprofeel.fr](https://programmeprofeel.fr).

**Usage dans ce dépôt.** Les PDF sont conservés à des fins **documentaires et
de recherche internes** (alimentation d'une base de connaissances / RAG au sein
de Maestro). L'**attribution est préservée** : `manifest.json` conserve pour
chaque fichier l'URL source d'origine et l'éditeur. Ce dépôt **n'est pas** une
rediffusion officielle ; pour toute citation ou version faisant autorité,
se référer aux documents **originaux et à jour** sur les sites des éditeurs.

**Garantie.** Contenu fourni « en l'état », sans garantie d'exhaustivité,
d'exactitude ni d'actualité.

**Retrait.** À la demande d'un ayant droit, tout document concerné sera retiré
sans délai. Contact : `namur@maestroarchitecture.com`.
