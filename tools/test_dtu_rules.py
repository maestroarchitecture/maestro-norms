#!/usr/bin/env python3
"""Tests de l'étage 0 (tools/dtu_rules.py + dtu_rules.yaml).

Valide la mécanique du loader ET les invariants de la KB : chaque règle porte
les 4 champs non vides, les lots sont des ids connus, les alias résolvent, et le
lookup est lenient (lot inconnu → []).

Lancer : python3 -m pytest tools/test_dtu_rules.py -q
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dtu_rules  # noqa: E402

VALID_LOTS = {f"{i:02d}" for i in range(0, 13)}
FIELDS = ("exigence", "seuil", "condition", "ref")

# Tant que dtu_rules.yaml n'est pas créé (authoring + vérification, cf. HANDOFF),
# on skippe proprement au lieu d'échouer la collecte.
pytestmark = pytest.mark.skipif(
    not os.path.exists(dtu_rules._RULES_PATH),
    reason="dtu_rules.yaml pas encore créé — à rédiger + vérifier (cf. docs/HANDOFF)",
)


def _safe_lots():
    try:
        return dtu_rules.lots_with_rules()
    except FileNotFoundError:
        return []


def test_yaml_present_and_has_rules():
    assert dtu_rules.lots_with_rules(), "dtu_rules.yaml ne contient aucun lot avec règles"


@pytest.mark.parametrize("lot_id", _safe_lots())
def test_every_rule_has_four_non_empty_fields(lot_id):
    rules = dtu_rules.rules_for_lot(lot_id)
    assert rules, f"lot {lot_id} listé mais sans règle"
    for i, r in enumerate(rules):
        for f in FIELDS:
            assert r.get(f) and str(r[f]).strip(), f"lot {lot_id} règle #{i} : champ '{f}' vide"


def test_lot_keys_are_valid_ids():
    for lot_id in dtu_rules.lots_with_rules():
        assert lot_id in VALID_LOTS, f"lot inconnu dans dtu_rules.yaml : {lot_id!r}"


def test_business_keyword_aliases_resolve():
    assert dtu_rules.resolve_lot("electricite") == "05"
    assert dtu_rules.resolve_lot("chauffage") == "04"
    assert dtu_rules.resolve_lot("vmc") == "04"
    # un id de lot passe tel quel
    assert dtu_rules.resolve_lot("05") == "05"


def test_rules_for_lot_accepts_keyword_and_id():
    by_id = dtu_rules.rules_for_lot("05")
    by_kw = dtu_rules.rules_for_lot("electricite")
    assert by_id == by_kw and by_id, "alias mot-clé ≠ id pour le lot 05"


def test_unknown_lot_is_lenient():
    assert dtu_rules.rules_for_lot("99") == []
    assert dtu_rules.rules_for_lot("inexistant") == []


def test_justification_rows_shape():
    for lot_id in dtu_rules.lots_with_rules():
        for row in dtu_rules.justification_rows_for_lot(lot_id):
            assert set(row.keys()) == set(FIELDS)


def test_meta_declares_licence_and_verification():
    m = dtu_rules.meta()
    assert "licence" in m, "meta.licence manquant (garde-fou citation seule)"
    # le ref doit citer une norme, pas reproduire son texte : heuristique douce
    for lot_id in dtu_rules.lots_with_rules():
        for r in dtu_rules.rules_for_lot(lot_id):
            assert len(str(r["exigence"])) <= 240, "exigence trop longue (risque de verbatim)"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
