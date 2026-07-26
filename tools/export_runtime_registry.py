#!/usr/bin/env python3
"""Exporte la vue runtime, déterministe et fail-closed, du registre DTU."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import yaml

import dtu_rules


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "dtu_rules.yaml"
DEFAULT_OUTPUT = ROOT / "dist" / "dtu_rules.runtime.yaml"
DEFAULT_AUDIT_OUTPUT = ROOT / "dist" / "dtu_rules.runtime.audit.json"
SCHEMA_VERSION = "1"


def _source_metadata(source_path: Path, source_commit: str) -> dict:
    source_bytes = source_path.read_bytes()
    return {
        "schema_version": SCHEMA_VERSION,
        "source_commit": source_commit,
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
    }


def runtime_registry(source_path: Path, source_commit: str) -> dict:
    """Construit la vue runtime sans modifier ni paraphraser les règles source."""
    source_bytes = source_path.read_bytes()
    source = yaml.safe_load(source_bytes) or {}
    rules = {
        str(lot_id): [rule for rule in lot_rules if dtu_rules.is_verified_rule(rule)]
        for lot_id, lot_rules in (source.get("rules") or {}).items()
    }
    return {**_source_metadata(source_path, source_commit), "rules": {
        lot_id: lot_rules for lot_id, lot_rules in rules.items() if lot_rules
    }}


def audit_report(source_path: Path, source_commit: str) -> dict:
    """Expose chaque exclusion de runtime : aucune chute n'est silencieuse."""
    source = yaml.safe_load(source_path.read_bytes()) or {}
    lots = {}
    totals = {"authored_verified": 0, "exported": 0, "rejected": 0}
    for lot_id, lot_rules in (source.get("rules") or {}).items():
        verified = [rule for rule in lot_rules if rule.get("statut") == "verifie"]
        if not verified:
            continue
        rejected = [
            {"rule_index": index, "ref": rule.get("ref", ""), "reasons": dtu_rules.provenance_errors(rule)}
            for index, rule in enumerate(lot_rules, start=1)
            if rule.get("statut") == "verifie" and not dtu_rules.is_verified_rule(rule)
        ]
        exported = len(verified) - len(rejected)
        lots[str(lot_id)] = {
            "authored_verified": len(verified),
            "exported": exported,
            "rejected": len(rejected),
            "rejections": rejected,
        }
        totals["authored_verified"] += len(verified)
        totals["exported"] += exported
        totals["rejected"] += len(rejected)
    return {**_source_metadata(source_path, source_commit), "totals": totals, "lots": lots}


def export_runtime_registry(
    source_path: Path, output_path: Path, source_commit: str, audit_output_path: Path,
) -> dict:
    """Écrit les sorties runtime et audit, toutes deux déterministes."""
    registry = runtime_registry(source_path, source_commit)
    payload = yaml.safe_dump(
        registry,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(payload, encoding="utf-8")
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_output_path.write_text(
        json.dumps(audit_report(source_path, source_commit), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return registry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True, help="commit exact du registre source")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="registre YAML source")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="YAML runtime à produire")
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT, help="rapport JSON d'exclusion")
    args = parser.parse_args()
    export_runtime_registry(args.source, args.output, args.source_commit, args.audit_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
