"""Civic Decoder — smoke tests."""
from __future__ import annotations
import pandas as pd
import pytest
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
DATA_ROOT = DATA


def test_mps_load():
    df = pd.read_csv(DATA / "mps" / "mps_seed.csv")
    assert len(df) >= 10
    required = {"mp_id", "name", "party", "constituency", "county",
                "attendance_pct", "bills_sponsored", "questions_asked", "source", "verified"}
    assert required.issubset(df.columns)


def test_confirmed_rows_are_backed_by_the_verification_log():
    """'confirmed' must be earned. The old test required EVERY row to say confirmed, so the label could only ever go up and no evidence was needed.
    A row may claim confirmed only if data/VERIFICATION_LOG.csv records evidence for it."""
    import csv
    log = list(csv.DictReader(open(DATA_ROOT / "VERIFICATION_LOG.csv", encoding="utf-8")))
    logged = {(r["file"], r["row_key"]) for r in log if r["evidence_url"].strip() and r["verified_by"].strip() and r["verified_on"].strip()}
    for rel, key in [('mps/mps_seed.csv', 'mp_id'), ('bills/bills_seed.csv', 'bill_id'), ('cdf/cdf_seed.csv', 'constituency')]:
        df = pd.read_csv(DATA_ROOT / rel)
        assert set(df["verified"]) <= {"confirmed", "unverified"}, rel
        claimed = {(rel, str(v)) for v in df[df["verified"] == "confirmed"][key]}
        assert claimed <= logged, f"{rel}: rows claim 'confirmed' with no logged evidence: {sorted(claimed - logged)[:5]}"


def test_mps_attendance_range():
    df = pd.read_csv(DATA / "mps" / "mps_seed.csv")
    assert df["attendance_pct"].between(0, 100).all(), "Attendance out of 0–100 range"


def test_bills_load():
    df = pd.read_csv(DATA / "bills" / "bills_seed.csv")
    assert len(df) >= 5
    required = {"bill_id", "title", "sponsor", "status", "category", "source", "verified"}
    assert required.issubset(df.columns)


def test_bills_no_fabricated_votes():
    df = pd.read_csv(DATA / "bills" / "bills_seed.csv")
    # Bills with a recorded vote must have votes_for > 0
    voted = df[df["passed"] == True]
    assert (voted["votes_for"] > 0).all(), "Passed bills must have recorded votes_for"


def test_bills_withdrawn_not_passed():
    df = pd.read_csv(DATA / "bills" / "bills_seed.csv")
    withdrawn = df[df["status"] == "Withdrawn"]
    assert (withdrawn["passed"] == False).all(), "Withdrawn bills must not be marked passed"


def test_cdf_load():
    df = pd.read_csv(DATA / "cdf" / "cdf_seed.csv")
    assert len(df) >= 10
    required = {"constituency", "county", "mp_name", "absorption_pct", "source", "verified"}
    assert required.issubset(df.columns)


def test_cdf_absorption_range():
    df = pd.read_csv(DATA / "cdf" / "cdf_seed.csv")
    assert df["absorption_pct"].between(0, 100).all(), "Absorption out of 0–100 range"


def test_cdf_utilised_le_allocated():
    df = pd.read_csv(DATA / "cdf" / "cdf_seed.csv")
    assert (df["utilised_kes_m"] <= df["allocated_kes_m"]).all(), \
        "Utilised must not exceed allocated"
