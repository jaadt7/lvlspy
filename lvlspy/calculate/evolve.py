"""
    Module to handle the evolution of the level system based on temperature
"""

import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import expm_multiply

def newton_raphson(sp,temp,y0, time, tol = 1e-6):
    """
    Evolves a system using the Newton-Raphson method

    Args:
        ``sp`` (:obj:`lvlspy.species.Species`): The species containing the levels to be evolved

        ``temp`` (:obj:`float`): The temperature in K to evolve the system at.

        ``y0`` (:obj:`numpy.array`): 1D array of length n_levels containing the initial distribution.

        ``time`` (:obj:`numpy.array`,optional): An array containing the time steps.
        ``tol`` (:obj:`float`): The convergence condition for the method. Defaults to 1e-6.

    Returns:
        ``y`` (:obj:`numpy.array`): 2D array of size n_levels*n_time containing the evolved system.
    """

    y = np.empty((len(y0),len(time)))
    y[:,0] = y0

    rm = sp.compute_rate_matrix(temp) #calculate the rate matrix of the species

    y_dt = y[:,0]
    for i in range(1, len(time)):
        dt = time[i] - time[i - 1]
        matrix = np.identity(len(y_dt)) - dt * rm
        delta = np.ones(len(y_dt))
        while max(delta) > tol:
            delta = np.linalg.solve(
                matrix, -_f_vector(y_dt, y[:,i-1], matrix)
            )
            y_dt = y_dt + delta
        y[:,i] = y_dt

    return y

def _f_vector(y_dt, y_i, rm):
    return np.matmul(rm, y_dt) - y_i

def csc(sp,temp,y0, time):
    """Evolves a system using sparse solver

    Args:
        ``sp`` (:obj:`lvlspy.species.Species`): The species containing the levels to be evolved

        ``temp`` (:obj:`float`): The temperature in K to evolve the system at.

        ``y0`` (:obj:`numpy.array`): Array containing the initial condition.

        ``time`` (:obj:`numpy.array`): An array containing the time stamps to evolve the system

    Returns:
        ``sol_expm_solver`` (:obj:`numpy.array`): A 2D array containing the evolved system
    """

    rm = sp.compute_rate_matrix(temp)
    rm_csc = csc_matrix(rm)
    sol_expm_solver = np.empty([time.shape[0], rm.shape[0]])
    sol_expm_solver[0, :] = y0

    for i in range(len(time) - 1):
        y = expm_multiply(
            rm_csc,
            y0,
            start=time[i],
            stop=time[i + 1],
            num=2,
            endpoint=True,
        )[0, :]
        sol_expm_solver[i + 1, :] = y
        
    return sol_expm_solver
