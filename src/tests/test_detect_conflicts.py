
import pandas as pd
from src.domain.cpa import detect_conflicts


def make_snapshot(rows):
    """
    Helper to create snapshot DataFrame.
    """
    return pd.DataFrame(rows)


def test_detects_simple_horizontal_conflict():
    """
    Two aircraft flying towards each other at same altitude.
    """
    snapshot = make_snapshot([
        {
            "icao24": "a",
            "lat": 0.0,
            "lon": 0.0,
            "velocity": 100.0,
            "heading": 90.0,
            "baroaltitude": 10_000.0,
            "vertrate": 0.0,
        },
        {
            "icao24": "b",
            "lat": 0.0,
            "lon": 0.09,  # ~10 km east
            "velocity": 100.0,
            "heading": 270.0,
            "baroaltitude": 10_000.0,
            "vertrate": 0.0,
        },
    ])

    conflicts = detect_conflicts(
        snapshot,
        lookahead_s=120,
        sep_nm=5.0,
        sep_ft=1000,
    )

    assert len(conflicts) == 1
    c = conflicts[0]

    assert {"a", "b"} == {c["a"], c["b"]}
    assert c["d_cpa_nm"] < 5.0
    assert c["vert_sep_ft"] < 1000


def test_no_conflict_due_to_vertical_separation():
    """
    Horizontal conflict but sufficient vertical separation.
    """
    snapshot = make_snapshot([
        {
            "icao24": "a",
            "lat": 0.0,
            "lon": 0.0,
            "velocity": 100.0,
            "heading": 90.0,
            "baroaltitude": 10_000.0,
            "vertrate": 0.0,
        },
        {
            "icao24": "b",
            "lat": 0.0,
            "lon": 0.09,
            "velocity": 100.0,
            "heading": 270.0,
            "baroaltitude": 10_000.0 + 1_000.0,  # ~3300 ft
            "vertrate": 0.0,
        },
    ])

    conflicts = detect_conflicts(
        snapshot,
        lookahead_s=120,
        sep_nm=5.0,
        sep_ft=1000,
    )

    assert conflicts == []


def test_conflict_symmetry():
    """
    A <-> B ordering must not matter.
    """
    snapshot = make_snapshot([
        {
            "icao24": "x",
            "lat": 0.0,
            "lon": 0.0,
            "velocity": 120.0,
            "heading": 45.0,
            "baroaltitude": 9_000.0,
            "vertrate": 0.0,
        },
        {
            "icao24": "y",
            "lat": 0.05,
            "lon": 0.05,
            "velocity": 120.0,
            "heading": 225.0,
            "baroaltitude": 9_000.0,
            "vertrate": 0.0,
        },
    ])

    conflicts = detect_conflicts(snapshot)

    assert len(conflicts) == 1
