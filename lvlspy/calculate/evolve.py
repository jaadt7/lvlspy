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
        Evolves a system using Newton Raphson method
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
        """evolves a system using sparse solver"""

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
