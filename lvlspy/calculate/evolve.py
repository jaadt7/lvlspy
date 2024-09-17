"""
    Module to handle the evolution of the level system based on temperature
"""

import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import expm_multiply


class Evolution:
    """
    A class that handles level evolution
    """

    def newton_raphson(self, y, time, tol, rm):
        """
        Evolves a system using the Newton-Raphson method

        Args:
            ``y`` (:obj:`numpy.array`): 2D array of dimensions n_levels X n_time_steps.
            The first column contains the initial setup

            ``time`` (:obj:`numpy.array`): An array containing the time steps

            ``tol`` (:obj:`float`): The convergence condition for the method

            ``rm``  (:obj:`numpy.array`): 2D array containing the transition rates
            between the levels

        Returns:
            ``y`` (:obj:`numpy.array`): The filled up 2D array where each column is
            the updated evolution at that time step
        """
        y_dt = y[0, :]
        for i in range(1, len(time)):
            dt = time[i] - time[i - 1]
            rm = np.identity(len(y_dt)) - dt * rm
            delta = np.ones(len(y_dt))
            while max(delta) > tol:
                delta = np.linalg.solve(
                    rm, -self._f_vector(y_dt, y[i - 1, :], rm)
                )
                y_dt = y_dt + delta
            y[i, :] = y_dt

        return y

    def _f_vector(self, y_dt, y_i, rm):
        return np.matmul(rm, y_dt) - y_i

    def csc_solve(self, y0, rm, time):
        """Evolves a system using sparse solver

        Args:
            ``y0`` (:obj:`numpy.array`): Array containing the initial condition

            ``rm`` (:obj:`numpy.array`): 2D numpy array containing the rate matrix of the system

            ``time`` (:obj:`numpy.array`): An array containing the time stamps to evolve the system

        Returns:
            ``sol_expm_solver`` (:obj:`numpy.array`): A 2D array containing the evolved system
        """

        rm_csc = csc_matrix(rm)
        sol_expm_solver = np.empty([time.shape[0], rm.shape[0]])
        sol_expm_solver[0, :] = y0

        for i in range(sol_expm_solver.shape[1]):
            y = expm_multiply(
                rm_csc,
                y0,
                start=time[i],
                stop=time[i + 1],
                num=2,
                endpoint=True,
            )[0, :]
            sol_expm_solver[i + 1, :] = y
            y0 = y
        return sol_expm_solver
