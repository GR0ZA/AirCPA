import numpy as np
import pandas as pd
from src.domain.cpa import compute_cpa


def test_compute_cpa_head_on():
    """
    Two aircraft 10 km apart, closing head-on at 200 m/s relative speed.
    """
    relative_position_m = np.array([10_000.0, 0.0])
    relative_velocity_mps = np.array([-200.0, 0.0])

    t_cpa, d_cpa = compute_cpa(
        relative_position_m, relative_velocity_mps
    )

    assert t_cpa == 50.0
    assert np.isclose(d_cpa, 0.0)


def test_compute_cpa_parallel_motion():
    """
    Parallel motion → no CPA convergence.
    """
    relative_position_m = np.array([0.0, 5_000.0])
    relative_velocity_mps = np.array([100.0, 0.0])

    t_cpa, d_cpa = compute_cpa(
        relative_position_m, relative_velocity_mps
    )

    assert t_cpa == 0.0 or t_cpa is not None
    assert np.isclose(d_cpa, 5_000.0)


def test_compute_cpa_zero_relative_velocity():
    """
    Zero relative velocity → undefined CPA time.
    """
    relative_position_m = np.array([1_000.0, 1_000.0])
    relative_velocity_mps = np.array([0.0, 0.0])

    t_cpa, d_cpa = compute_cpa(
        relative_position_m, relative_velocity_mps
    )

    assert t_cpa is None
    assert np.isclose(d_cpa, np.linalg.norm(relative_position_m))
