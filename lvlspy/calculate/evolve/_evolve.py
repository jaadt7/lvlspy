"""
Module to handle the evolution of the level system based on temperature
"""

import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import expm_multiply


def _validate_evolution_inputs(sp, y0, time, tol):
    """Validate common evolution inputs before solving."""

    y0 = np.asarray(y0, dtype=float)
    time = np.asarray(time, dtype=float)

    if y0.ndim != 1:
        raise ValueError("Initial population vector must be one-dimensional")
    if time.ndim != 1:
        raise ValueError("Evolution time grid must be one-dimensional")
    if len(time) == 0:
        raise ValueError("Evolution time grid must contain at least one value")
    if not np.all(np.isfinite(y0)):
        raise ValueError(
            "Initial population vector must contain only finite values"
        )
    if not np.all(np.isfinite(time)):
        raise ValueError("Evolution time grid must contain only finite values")
    if np.any(np.diff(time) < 0):
        raise ValueError("Evolution time grid must be nondecreasing")
    if len(y0) != sp.compute_rate_matrix(0.0).shape[0]:
        raise ValueError(
            "Initial population vector length must match the number of levels"
        )
    if not np.isfinite(tol) or tol <= 0:
        raise ValueError(
            "Convergence tolerance must be a positive finite value"
        )

    return y0, time


def newton_raphson(sp, temp, y0, time, tol=1e-6):
    """
    Evolves a system using the Newton-Raphson method

    Args:
        ``sp`` (:obj:`lvlspy.species.Species`): The species containing the levels to be evolved

        ``temp`` (:obj:`float`): The temperature in K to evolve the system at.

        ``y0`` (:obj:`numpy.array`): 1D array containing the initial distribution.

        ``time`` (:obj:`numpy.array`,optional): An array containing the time steps.
        ``tol`` (:obj:`float`): The convergence condition for the method. Defaults to 1e-6.

    Returns:
        ``y`` (:obj:`numpy.array`): 2D array of size n_levels*n_time containing the evolved system.

        ``fug`` (:obj:`numpy.array`) 2D array containing the fugacities as a function of time
    """

    y0, time = _validate_evolution_inputs(sp, y0, time, tol)

    y = np.empty((len(y0), len(time)))
    fug = np.empty((len(y0), len(time)))
    y[:, 0] = y0

    rm = sp.compute_rate_matrix(
        temp
    )  # calculate the rate matrix of the species
    eq_prob = sp.compute_equilibrium_probabilities(temp)
    y_dt = y[:, 0]
    fug[:, 0] = y_dt / eq_prob
    for i in range(1, len(time)):
        dt = time[i] - time[i - 1]
        matrix = np.identity(len(y_dt)) - dt * rm
        delta = np.ones(len(y_dt))
        while np.max(np.abs(delta)) > tol:
            delta = np.linalg.solve(
                matrix, -_f_vector(y_dt, y[:, i - 1], matrix)
            )
            y_dt = y_dt + delta
        y[:, i] = y_dt
        fug[:, i] = y[:, i] / eq_prob

    return y, fug


def _f_vector(y_dt, y_i, rm):
    return np.matmul(rm, y_dt) - y_i


def csc(sp, temp, y0, time):
    """Evolves a system using sparse solver

    Args:
        ``sp`` (:obj:`lvlspy.species.Species`): The species containing the levels to be evolved

        ``temp`` (:obj:`float`): The temperature in K to evolve the system at.

        ``y0`` (:obj:`numpy.array`): Array containing the initial condition.

        ``time`` (:obj:`numpy.array`): An array containing the time stamps to evolve the system

    Returns:
        ``sol_expm_solver`` (:obj:`numpy.array`): A 2D array containing the evolved system

        ``fug`` (:obj:`numpy.array`) 2D array containing the fugacities as a function of time
    """

    y0, time = _validate_evolution_inputs(sp, y0, time, 1.0)

    rm = sp.compute_rate_matrix(temp)
    eq_prob = sp.compute_equilibrium_probabilities(temp)
    rm_csc = csc_matrix(rm)
    sol_expm_solver = np.empty([rm.shape[0], time.shape[0]])
    sol_expm_solver[:, 0] = y0
    fug = np.empty((len(y0), len(time)))
    fug[:, 0] = y0 / eq_prob
    for i in range(len(time) - 1):
        dt = time[i + 1] - time[i]
        y = expm_multiply(rm_csc * dt, sol_expm_solver[:, i])
        sol_expm_solver[:, i + 1] = y
        fug[:, i + 1] = y / eq_prob

    return sol_expm_solver, fug
