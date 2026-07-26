from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_runtime_registry as exporter  # noqa: E402


def _rule(**overrides):
    rule = {
        "exigence": "Exigence test", "seuil": "1", "condition": "condition", "ref": "NF test §1",
        "statut": "verifie", "source_type": "primaire", "edition": "mai 1998",
        "localisateur": "§1", "reviewed_by": "Namur", "reviewed_at": "2026-06-19",
    }
    rule.update(overrides)
    return rule


def _write_source(path: Path, rules: dict):
    path.write_text(yaml.safe_dump({"rules": rules}, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_export_est_deterministe_et_conserve_la_provenance(tmp_path):
    source = tmp_path / "source.yaml"
    first = tmp_path / "first.yaml"
    second = tmp_path / "second.yaml"
    rule = _rule()
    _write_source(source, {"05": [rule]})

    first_audit = tmp_path / "first.audit.json"
    second_audit = tmp_path / "second.audit.json"
    exporter.export_runtime_registry(source, first, "abc123", first_audit)
    exporter.export_runtime_registry(source, second, "abc123", second_audit)

    assert first.read_bytes() == second.read_bytes()
    assert first_audit.read_bytes() == second_audit.read_bytes()
    output = yaml.safe_load(first.read_text(encoding="utf-8"))
    assert output["schema_version"] == exporter.SCHEMA_VERSION
    assert output["source_commit"] == "abc123"
    assert output["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert output["rules"]["05"] == [rule]


def test_export_detecte_mutation_m1_source_secondaire_et_m2_metadonnee_manquante(tmp_path):
    source = tmp_path / "source.yaml"
    output = tmp_path / "runtime.yaml"
    complete = _rule()
    # M1 : promotion depuis une source secondaire. M2 : provenance incomplète.
    m1 = _rule(source_type="secondaire")
    m2 = _rule()
    del m2["reviewed_at"]
    candidate = _rule(statut="a_valider_namur", source_type="secondaire")
    _write_source(source, {"05": [complete, m1, m2, candidate]})

    audit_output = tmp_path / "runtime.audit.json"
    exporter.export_runtime_registry(source, output, "abc123", audit_output)

    assert yaml.safe_load(output.read_text(encoding="utf-8"))["rules"] == {"05": [complete]}
    audit = __import__("json").loads(audit_output.read_text(encoding="utf-8"))
    assert audit["totals"] == {"authored_verified": 3, "exported": 1, "rejected": 2}
    assert [entry["reasons"] for entry in audit["lots"]["05"]["rejections"]] == [
        ["source_type doit être 'primaire'"], ["reviewed_at manquant"],
    ]


def test_audit_empeche_toute_chute_silencieuse(tmp_path):
    source = tmp_path / "source.yaml"
    _write_source(source, {"05": [_rule(), _rule(reviewed_by="")]})

    audit = exporter.audit_report(source, "abc123")

    assert audit["totals"]["authored_verified"] == 2
    assert audit["totals"]["exported"] + audit["totals"]["rejected"] == 2
    assert audit["lots"]["05"]["rejections"][0]["reasons"] == ["reviewed_by manquant"]
