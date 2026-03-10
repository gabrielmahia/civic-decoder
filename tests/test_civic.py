"""Civic Decoder — smoke tests."""
from __future__ import annotations
import pandas as pd
import pytest
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"


def test_mps_load():
    df = pd.read_csv(DATA / "mps" / "mps_seed.csv")
    assert len(df) >= 10
    required = {"mp_id", "name", "party", "constituency", "county",
                "attendance_pct", "bills_sponsored", "questions_asked", "source", "verified"}
    assert required.issubset(df.columns)


def test_mps_no_unverified():
    df = pd.read_csv(DATA / "mps" / "mps_seed.csv")
    bad = df[~df["verified"].str.startswith("confirmed")]
    assert len(bad) == 0, f"Unverified MPs: {bad['name'].tolist()}"


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
