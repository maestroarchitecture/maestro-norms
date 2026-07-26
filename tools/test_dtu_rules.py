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
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dtu_rules  # noqa: E402

VALID_LOTS = {f"{i:02d}" for i in range(0, 13)}
FIELDS = ("exigence", "seuil", "condition", "ref")
PROVENANCE_FIELDS = ("source_type", "edition", "localisateur", "reviewed_by", "reviewed_at")

# Tant que dtu_rules.yaml n'est pas créé (authoring + vérification, cf. HANDOFF),
# on skippe proprement au lieu d'échouer la collecte.
pytestmark = pytest.mark.skipif(
    not os.path.exists(dtu_rules._RULES_PATH),
    reason="dtu_rules.yaml pas encore créé — à rédiger + vérifier (cf. docs/HANDOFF)",
)


def _authored_lots():
    try:
        return sorted((dtu_rules._load().get("rules") or {}).keys())
    except FileNotFoundError:
        return []


def test_yaml_present_and_has_rules():
    assert dtu_rules._load().get("rules"), "dtu_rules.yaml ne contient aucun lot avec règles"


@pytest.mark.parametrize("lot_id", _authored_lots())
def test_every_rule_has_four_non_empty_fields(lot_id):
    rules = (dtu_rules._load().get("rules") or {}).get(lot_id, [])
    assert rules, f"lot {lot_id} déclaré mais sans règle d'authoring"
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
    assert by_id == by_kw, "alias mot-clé ≠ id pour le lot 05"


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


def test_live_registry_ne_contient_aucun_brouillon_a_verifier():
    """Le loader ne filtre pas les statuts : un brouillon doit rester dans le
    fichier draft ou le catalogue, jamais dans le registre consommable."""
    data = yaml.safe_load(open(dtu_rules._RULES_PATH, encoding="utf-8")) or {}
    fautifs = []
    for lot_id, rules in (data.get("rules") or {}).items():
        for index, rule in enumerate(rules or []):
            if rule.get("statut") == "a_verifier":
                fautifs.append(f"lot {lot_id}, règle {index + 1}: {rule.get('ref', '?')}")
    assert not fautifs, (
        "entrée a_verifier dans le registre vivant ; déplacer vers "
        "dtu_rules.draft.yaml ou normes-par-lot.yaml :\n  " + "\n  ".join(fautifs)
    )


def test_lookup_n_expose_que_les_regles_verifiees():
    """Le YAML peut conserver des candidates Namur, jamais la sortie servable."""
    for lot_id in dtu_rules.lots_with_rules():
        rules = dtu_rules.rules_for_lot(lot_id)
        assert rules
        assert all(rule.get("statut") == "verifie" for rule in rules)

    data = yaml.safe_load(open(dtu_rules._RULES_PATH, encoding="utf-8")) or {}
    assert any(
        rule.get("statut") == "a_valider_namur"
        for rules in (data.get("rules") or {}).values()
        for rule in rules
    ), "fixture attendue : le registre contient des candidates non servables"


def test_registre_courant_expose_exactement_les_26_regles_revue_tracee():
    authored = [
        rule
        for rules in (dtu_rules._load().get("rules") or {}).values()
        for rule in rules
        if rule.get("statut") == "verifie"
    ]
    assert len(authored) == 50
    assert dtu_rules.lots_with_rules() == ["02", "03", "04", "06", "08", "09"]
    assert {
        lot_id: len(dtu_rules.rules_for_lot(lot_id))
        for lot_id in dtu_rules.lots_with_rules()
    } == {"02": 3, "03": 7, "04": 7, "06": 2, "08": 4, "09": 3}
    assert sum(
        len(dtu_rules.rules_for_lot(lot_id))
        for lot_id in dtu_rules.lots_with_rules()
    ) == 26
    assert all(
        rule.get("reviewed_by") == "Namur"
        for lot_id in dtu_rules.lots_with_rules()
        for rule in dtu_rules.rules_for_lot(lot_id)
    )


def test_regle_ventilation_sdb_ne_melange_plus_norme_et_confort_maestro():
    rules = dtu_rules.rules_for_lot("04")
    sdb = next(
        rule for rule in rules
        if rule.get("exigence") == "Débit d'air extrait minimal en salle de bains ou de douches"
    )
    assert "75 m³/h" not in sdb["condition"]
    assert "confort" not in sdb["condition"].lower()


def test_provenance_verifiee_est_fail_closed():
    complete = {
        "statut": "verifie", "source_type": "primaire", "edition": "mai 1998",
        "localisateur": "§7.2", "reviewed_by": "Namur", "reviewed_at": "2026-06-19",
    }
    assert dtu_rules.is_verified_rule(complete)
    for field in PROVENANCE_FIELDS:
        mutated = dict(complete)
        mutated.pop(field)
        assert not dtu_rules.is_verified_rule(mutated), field


@pytest.mark.parametrize("source_type", ["secondaire", "notice", ""])
def test_provenance_secondaire_ou_notice_ne_peut_pas_etre_verifiee(source_type):
    rule = {
        "statut": "verifie", "source_type": source_type, "edition": "mai 1998",
        "localisateur": "§7.2", "reviewed_by": "Namur", "reviewed_at": "2026-06-19",
    }
    assert not dtu_rules.is_verified_rule(rule)


def test_lot_05_ne_sert_que_la_regle_consuel_reef_tracee():
    rules = dtu_rules.rules_for_lot("05")
    assert rules == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
