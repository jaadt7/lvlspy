"""Tests for level-system evolution routines."""

import numpy as np
import pytest

from lvlspy.extensions.calculate.evolve import csc
from lvlspy.extensions.calculate.evolve import _evolve as evolve_module


class TwoStateSpecies:
    """Two-state system with equal forward and reverse rates."""

    def compute_rate_matrix(self, temperature):
        del temperature
        return np.array([[-1.0, 1.0], [1.0, -1.0]])

    def compute_equilibrium_probabilities(self, temperature):
        del temperature
        return np.array([0.5, 0.5])


class ThreeStateSpecies:
    """Three-state system used for validation and convergence checks."""

    def compute_rate_matrix(self, temperature):
        del temperature
        return np.array(
            [
                [-2.0, 1.0, 1.0],
                [1.0, -2.0, 1.0],
                [1.0, 1.0, -2.0],
            ]
        )

    def compute_equilibrium_probabilities(self, temperature):
        del temperature
        return np.array([1.0, 1.0, 1.0])


def test_csc_rejects_nonmonotonic_time_grid():
    initial = np.array([1.0, 0.0])
    time = np.array([0.0, 1.0, 0.5])

    with pytest.raises(ValueError, match="time grid must be nondecreasing"):
        csc(TwoStateSpecies(), 1.0, initial, time)


def test_csc_rejects_initial_population_length_mismatch():
    initial = np.array([1.0, 0.0, 0.0])
    time = np.array([0.0, 1.0])

    with pytest.raises(
        ValueError, match="Initial population vector length must match"
    ):
        csc(TwoStateSpecies(), 1.0, initial, time)


def test_newton_raphson_uses_absolute_convergence_magnitude(monkeypatch):
    species = ThreeStateSpecies()
    initial = np.array([1.0, 0.0, 0.0])
    time = np.array([0.0, 1.0])

    deltas = iter([np.array([-1.0, -1.0, -1.0]), np.zeros(3)])
    calls = []

    def fake_solve(matrix, rhs):
        calls.append((matrix.copy(), rhs.copy()))
        return next(deltas)

    monkeypatch.setattr(evolve_module.np.linalg, "solve", fake_solve)

    solution, fugacity = evolve_module.newton_raphson(species, 1.0, initial, time)

    assert len(calls) == 2
    np.testing.assert_allclose(solution[:, 0], initial)
    np.testing.assert_allclose(fugacity[:, 0], initial / species.compute_equilibrium_probabilities(1.0))


def test_csc_matches_two_state_analytic_solution():
    """The sparse solver reports the solution at each requested time."""

    time = np.array([0.0, 0.25, 1.0, 2.0])
    initial = np.array([1.0, 0.0])

    solution, fugacity = csc(TwoStateSpecies(), 1.0, initial, time)

    decay = np.exp(-2.0 * time)
    expected = np.vstack((0.5 * (1.0 + decay), 0.5 * (1.0 - decay)))

    np.testing.assert_allclose(solution, expected)
    np.testing.assert_allclose(solution.sum(axis=0), 1.0)
    np.testing.assert_allclose(fugacity, expected / 0.5)
