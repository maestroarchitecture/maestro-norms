#!/usr/bin/env python3
"""Étage 0 — KB de règles normatives déterministes par lot (lookup ~0 token).

Troisième source de justification normative, en plus de :
  • ``knowledge.yaml``      → ``dtu_refs`` (DTU/NF, payant → citation seule) ;
  • ``norms_by_lot.yaml``   → Recommandations Pro RAGE (gratuit, plein texte).

Ici : ``dtu_rules.yaml`` porte des **règles structurées** ``{exigence, seuil,
condition, ref}`` par lot — des **faits** (un nombre, une section, une condition),
paraphrasés, **jamais le texte verbatim** du DTU (droit d'auteur). Un lookup par
lot répond sans recherche sémantique ni lecture de PDF : **~0 token**, couvre
l'essentiel des justifications chiffrées du devis.

La ``ref`` reste une **citation** (``NF C 15-100 §x.y``) : on cite la règle, on
ne reproduit pas sa prose.

Usage CLI (démo lookup déterministe) :
    python3 tools/dtu_rules.py 05
    python3 tools/dtu_rules.py electricite --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RULES_PATH = os.path.join(ROOT, "dtu_rules.yaml")
_cache: Dict[str, dict] = {}

# Mots-clés métier → id de lot (aligné sur expert_travaux/norms_by_lot._LOT_ALIASES).
_LOT_ALIASES = {
    "platrerie": "02", "cloisons": "02", "doublage": "02",
    "plomberie": "03", "sanitaire": "03", "sanitaires": "03",
    "chauffage": "04", "ventilation": "04", "vmc": "04", "cvc": "04",
    "climatisation": "04", "ecs": "04",
    "electricite": "05", "électricité": "05", "elec": "05",
    "menuiseries_interieures": "06",
    "menuiseries": "07", "menuiserie": "07", "fenetres": "07", "fenetre": "07",
    "carrelage": "08", "faience": "08", "faïence": "08",
    "sols": "09", "revetements_sols": "09", "parquet": "09",
    "peinture": "10", "ravalement": "10",
}

_FIELDS = ("exigence", "seuil", "condition", "ref")


def _load() -> dict:
    if _RULES_PATH not in _cache:
        with open(_RULES_PATH, encoding="utf-8") as f:
            _cache[_RULES_PATH] = yaml.safe_load(f) or {}
    return _cache[_RULES_PATH]


def resolve_lot(lot: str) -> str | None:
    """Mot-clé métier OU id de lot → id de lot (``None`` si inconnu)."""
    s = str(lot).strip().lower()
    if s in (_load().get("rules") or {}):
        return s
    return _LOT_ALIASES.get(s)


def rules_for_lot(lot_id: str) -> List[dict]:
    """Règles ``{exigence, seuil, condition, ref}`` du lot (liste, éventuellement vide).

    Lenient : un lot inconnu renvoie ``[]`` (pas d'exception). Accepte un mot-clé
    métier (``"electricite"``) ou un id de lot (``"05"``).
    """
    lid = resolve_lot(lot_id) or str(lot_id)
    return list((_load().get("rules") or {}).get(lid, []))


def lots_with_rules() -> List[str]:
    """Lots disposant d'au moins une règle étage 0."""
    return sorted((_load().get("rules") or {}).keys())


def justification_rows_for_lot(lot_id: str) -> List[dict]:
    """Lignes prêtes pour la section « Justification normative » d'un devis/CCTP.

    Format aligné sur ``norms_by_lot.norms_section_for_lots`` (table). Chaque
    ligne : ``{exigence, seuil, condition, ref}``.
    """
    return [{k: r.get(k, "") for k in _FIELDS} for r in rules_for_lot(lot_id)]


def meta() -> dict:
    """Métadonnées de la KB (génération, licence, vérification)."""
    return dict(_load().get("meta") or {})


# --------------------------------------------------------------------------- #
def _cli() -> int:
    ap = argparse.ArgumentParser(description="Lookup déterministe étage 0 (dtu_rules.yaml).")
    ap.add_argument("lot", nargs="?", help="id de lot (04) ou mot-clé (electricite). Vide = liste les lots.")
    ap.add_argument("--json", action="store_true", help="sortie JSON")
    args = ap.parse_args()

    if not args.lot:
        lots = lots_with_rules()
        print(json.dumps(lots) if args.json else "Lots avec règles étage 0 : " + ", ".join(lots))
        return 0

    lid = resolve_lot(args.lot)
    rows = rules_for_lot(args.lot)
    if args.json:
        print(json.dumps({"lot": lid, "rules": rows}, ensure_ascii=False, indent=2))
        return 0 if rows else 1

    if not rows:
        print(f"Lot '{args.lot}' (résolu : {lid or '—'}) : aucune règle étage 0.", file=sys.stderr)
        return 1
    print(f"Lot {lid} — {len(rows)} règle(s) (lookup ~0 token) :\n")
    for i, r in enumerate(rows, 1):
        print(f"{i}. {r.get('exigence', '')}")
        print(f"   seuil     : {r.get('seuil', '')}")
        print(f"   condition : {r.get('condition', '')}")
        print(f"   réf       : {r.get('ref', '')}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
