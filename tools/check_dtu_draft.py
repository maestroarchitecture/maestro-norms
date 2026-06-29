#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validateur du brouillon de registre `dtu_rules.draft.yaml` + aide à la promotion.

Pourquoi : la chaîne devis (`tools/dtu_rules.py:rules_for_lot`) ne filtre PAS le statut.
Toute règle présente dans `dtu_rules.yaml` (live) part telle quelle en devis. Le brouillon
vit donc dans un fichier SÉPARÉ (`draft_rules:`), jamais consommé. Ce script garantit que :
  1. chaque règle brouillon est bien formée (mêmes 6 champs que le live, lot valide, statut
     autorisé, source non vide, seuil non-placeholder) ;
  2. la promotion vers le live n'expose JAMAIS une règle `a_verifier` (seules les `verifie`
     migrent). La promotion est NON DESTRUCTIVE : on émet les blocs YAML à insérer à la main
     dans les bonnes sections de `dtu_rules.yaml` (qui est commenté et curé — on ne le réécrit
     pas automatiquement).

Usage :
  python tools/check_dtu_draft.py --check      # valide le brouillon (sortie != 0 si erreur)
  python tools/check_dtu_draft.py --emit        # affiche les règles `verifie` prêtes à coller
"""
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parents[1]
DRAFT = HERE / "dtu_rules.draft.yaml"

FIELDS = ("exigence", "seuil", "condition", "ref", "statut", "source")
STATUTS = {"a_verifier", "verifie"}
LOTS = {f"{i:02d}" for i in range(0, 13)}  # 00..12


def _load_draft():
    data = yaml.safe_load(DRAFT.read_text(encoding="utf-8")) or {}
    return data.get("draft_rules") or {}


def validate():
    draft = _load_draft()
    errs, n = [], 0
    for lot, rules in draft.items():
        if lot not in LOTS:
            errs.append(f"lot inconnu hors taxonomie 00..12 : {lot!r}")
        for r in rules or []:
            n += 1
            tag = f"lot {lot} / {r.get('ref', '?')}"
            miss = set(FIELDS) - set(r)
            if miss:
                errs.append(f"{tag} : champs manquants {sorted(miss)}")
            if r.get("statut") not in STATUTS:
                errs.append(f"{tag} : statut invalide {r.get('statut')!r}")
            if not (r.get("source") or "").strip():
                errs.append(f"{tag} : source vide (traçabilité obligatoire)")
            if not (r.get("ref") or "").strip():
                errs.append(f"{tag} : ref vide")
            if "RELEVER" in (r.get("seuil", "") or "").upper():
                errs.append(f"{tag} : seuil resté en placeholder (« à relever »)")
    return n, errs


def emit_verified():
    """Émet les règles `statut: verifie` en YAML, par lot, prêtes à insérer dans dtu_rules.yaml."""
    draft = _load_draft()
    blocks = {}
    for lot, rules in draft.items():
        ready = [
            {k: r[k] for k in FIELDS if k in r}
            for r in (rules or [])
            if r.get("statut") == "verifie"
        ]
        if ready:
            blocks[lot] = ready
    if not blocks:
        print("# Aucune règle au statut `verifie` à promouvoir pour l'instant.")
        print("# (Les règles restent `a_verifier` tant que Namur ne les a pas validées.)")
        return
    print("# À INSÉRER dans dtu_rules.yaml sous la clé rules[<lot>] (vérifier l'allowlist check_dtu_refs.py) :")
    for lot, rules in blocks.items():
        print(f'\n  "{lot}":')
        print(yaml.safe_dump(rules, allow_unicode=True, sort_keys=False, width=100,
                             indent=2).rstrip())


def main(argv):
    if "--emit" in argv:
        emit_verified()
        return 0
    n, errs = validate()
    print(f"[dtu-draft] {n} règle(s) brouillon contrôlée(s) dans {DRAFT.name}")
    if errs:
        print(f"[dtu-draft] {len(errs)} ERREUR(S) :")
        for e in errs:
            print("  ✗", e)
        return 1
    print("[dtu-draft] OK — brouillon bien formé, aucune règle a_verifier ne peut fuiter (fichier séparé).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
