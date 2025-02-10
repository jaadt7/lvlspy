"""
Module to handle isomer related calculations. Functions are built based on the method in
`Gupta and Meyer (2001) <https://ui.adsabs.harvard.edu/abs/2001PhRvC..64b5805G/abstract>`_
"""

import numpy as np


def transfer_properties(rate_matrix, level_low, level_high):
    """Method that calculatest the transfer properties based on the rate matrix

    Args:
        ``rate_matrix`` (:obj:`numpy.array`) A 2D array containing the rate matrix
        of a species at a given temperature

        ``level_low`` (:obj:`int`) Integer indicating the lower level the transition
        is moving to

        ``level_high`` (:obj:`int`) Integer indicating the higher level the transition
        is moving from

    Returns:
        On successful return, an array containing the following variable is passed:

        ``tpm`` (:obj:`numpy.array`) A 2D array containing the Transition Probability Matrix

        ``f_low_in`` (:obj:`numpy.array`) An array containing the branching ratio from all the
        upper levels into the low level

        ``f_low_out`` (:obj:`numpy.array`) An array containing the branching ratio from the lower
        levels into all the other levels

        ``f_high_in`` (:obj:`numpy.array`) An array containing the branching ratio from all the
        levels into the high level

        ``f_high_out`` (:obj:`numpy.array`) An containing the branching ration out of the high
        level into all the other levels

        ``lambda_sum`` (:obj:`numpy.array`) An array containing the diagonal elements of
        the rate matrix

    """

    # setting in the rates going in to the levels
    lambda_low_in = rate_matrix[level_low, :]
    lambda_high_in = rate_matrix[level_high, :]

    # remove entries corresponding the rows and columns to be removed
    lambda_low_in = np.delete(lambda_low_in, [level_low, level_high])
    lambda_high_in = np.delete(lambda_high_in, [level_low, level_high])

    # setting the rates going out of the levels
    lambda_low_out = rate_matrix[:, level_low]
    lambda_high_out = rate_matrix[:, level_high]

    # remove entries corresponding to the rows and columns to be removed
    lambda_low_out = np.delete(lambda_low_out, [level_low, level_high])
    lambda_high_out = np.delete(lambda_high_out, [level_low, level_high])

    # extract the diagonal elements from the rate matrix as they are the
    # sum of all the rates into the level
    lambda_sum = np.diag(rate_matrix)
    # this array is the reduced array above without the removed levels
    lambda_red = np.delete(lambda_sum, [level_low, level_high])

    f_low_out = lambda_low_out / lambda_sum[level_low]
    f_high_out = lambda_high_out / lambda_sum[level_high]

    f_low_in = lambda_low_in / lambda_red
    f_high_in = lambda_high_in / lambda_red

    # setting up the transfer matrix
    tpm = rate_matrix
    tpm = tpm.T
    # remove the columns
    tpm = np.delete(tpm, [level_low, level_high], axis=1)
    # remove the rows
    tpm = np.delete(tpm, [level_low, level_high], axis=0)

    # Divide the row by the diagonal term
    tpm = (
        tpm / lambda_red[:, None]
    )  # This only works if the arrays are numpy arrays

    # set the diagonal to 0
    np.fill_diagonal(tpm, 0.0)

    return [tpm, f_low_in, f_low_out, f_high_in, f_high_out, lambda_sum]


def effective_rate(t, sp, level_low=0, level_high=1):
    """
    Method to calculate the effective transition rates between the isomeric and ground states

    Args:
        ``t`` (:obj:`float`) The temperature in K.

        ``sp`` (:obj:`lvlspy.species.Species`) The species of which the level system belongs to.

        ``level_low`` (:obj:`int`, optional) The lower level the effective transition rates are
        calculated to. Defaults to 0; the ground state.

        ``level_high`` (:obj:`int`, optional) The higher level the effective transtion rates are
        calculated to. Defaults to 1; the first excited state

    Returns:
        Upon successful return, the method returns the effective transition rates between the higher
        and lower level at temperature T

        ``l_low_high`` (:obj:`float`) The effective transition rate from the lower level to the
        higher level

        ``l_high_low`` (:obj:`float`) The effective transition rate from the higher level to the
        lower level
    """

    rate_matrix = np.abs(sp.compute_rate_matrix(t))
    trans_props = transfer_properties(rate_matrix, level_low, level_high)
    f_n = _partial_sum(trans_props[0])

    # Lambda_21_eff
    l_high_low = trans_props[5][level_high] * np.matmul(
        trans_props[4].T, np.matmul(f_n, trans_props[1])
    )
    # Lambda_12_eff
    l_low_high = trans_props[5][level_low] * (
        np.matmul(
            trans_props[2].T,
            np.matmul(f_n, trans_props[3]),
        )
    )

    return (
        l_low_high + rate_matrix[level_high, level_low],
        l_high_low + rate_matrix[level_low, level_high],
    )


def _partial_sum(tpm):
    n_terms = 50000
    f_n = np.identity(tpm.shape[0]) + tpm
    f_p = tpm
    i = 2
    while i < n_terms:
        f_p = np.matmul(f_p, tpm)
        f_n += f_p
        i += 1
        if np.linalg.norm(f_n, np.inf) < 1e-6:
            break

    return f_n


def cascade_probabilities(t, sp, level_low=0, level_high=1):
    """
    Method to calculate the cascace probability vectores (gammas)

    Args:
        ``t`` (:obj:`float`) The temperature in K

        ``sp`` (:obj:`lvlspy.species.Species`) The species of which the
        probability vectors are to be calculated for

        ``level_low`` (:obj:`int`, optional) The lower level the effective transition rates are
        calculated to. Defaults to 0; the ground state.

        ``level_high`` (:obj:`int`, optional) The higher level the effective transtion rates are
        calculated to. Defaults to 1; the first excited state

    Returns:
        Upon successful return, the cascade probability vectors will be returned as an array

        ``g1_out`` (:obj:`numpy.array`) cascade vector out of lower level
        ``g2_out`` (:obj:`numpy.array`) cascade vector out of higher level
        ``g1_in`` (:obj:`numpy.array`) cascade vector into lower level
        ``g2_in`` (:obj:`numpy.array`) cascade vector into higher level
    """

    rate_matrix = np.abs(sp.compute_rate_matrix(t))
    trans_props = transfer_properties(rate_matrix, level_low, level_high)

    f_n = _partial_sum(trans_props[0])

    g1_in = np.matmul(f_n, trans_props[1])
    g2_in = np.matmul(f_n, trans_props[3])

    g1_out = np.matmul(f_n.T, trans_props[2])
    g2_out = np.matmul(f_n.T, trans_props[4])

    return [g1_in, g2_in, g1_out, g2_out]


def ensemble_weights(t, sp, level_low=0, level_high=1):
    """
    Method to calculate the ensemble weights

    Args:
        ``t`` (:obj:`float`) The temperature in K

        ``sp`` (:obj:`lvlspy.species.Species`) The species of which the ensemble weights
        are to be calculated for

        ``level_low`` (:obj:`int`, optional) The lower level the effective transition rates are
        calculated to. Defaults to 0; the ground state.

        ``level_high`` (:obj:`int`, optional) The higher level the effective transtion rates are
        calculated to. Defaults to 1; the first excited state

    Returns:
        Upon successful return, the ensemble weights and their properties will be returned
        as an array

        ``w_low``  (:obj:`numpy.array`) weight factor relative to the low level
        ``w_high`` (:obj:`numpy.array`) weight factor relative to the high level
        ``W_low``  (:obj:`numpy.float`) Enhancement of ensemble abundance over low level
        ``W_high`` (:obj:`numpy.float`) Enhancement of ensemble abundance over high level
        ``R_lowk`` (:obj:`numpy.array`) The reverse ratio relative to the low level
        ``R_highk`` (:obj:`numpy.array`) The reverse ratio relative to the high level
        ``G_low``  (:obj:`numpy.float`) Partition function associated with the low level
        ``G_high`` (:obj:`numpy.float`) Patition function associated with the high level

    """
    # calculate the equilibrium probabilities
    eq_prob = sp.compute_equilibrium_probabilities(t)

    n = len(eq_prob)
    # initialize arrays
    w_low, w_high, r_lowk, r_highk = (
        np.empty(n),
        np.empty(n),
        np.empty(n - 2),
        np.empty(n - 1),
    )

    # get the cascade probabilities
    # gammas structure = [g1_in, g2_in, g1_out, g2_out]
    gammas = cascade_probabilities(t, sp, level_low, level_high)

    for i in range(n - 2):
        r_lowk[i] = eq_prob[i + 2] / eq_prob[level_low]
        r_highk[i] = eq_prob[i + 2] / eq_prob[level_high]

    for i in range(n):
        if i == level_low:
            w_low[i] = 1.0
            w_high[i] = 0.0
        elif i == level_high:
            w_low[i] = 0.0
            w_high[i] = 1.0
        else:
            w_low[i] = gammas[0][i - 2] * r_lowk[i - 2]
            w_high[i] = gammas[1][i - 2] * r_highk[i - 2]

    w_low, w_high = np.sum(w_low), np.sum(w_high)
    # Calculate the partition functions
    levels = sp.get_levels()
    g_low = levels[level_low].get_multiplicity() * w_low
    g_high = levels[level_high].get_multiplicity() * w_high

    return [w_low, w_high, w_low, w_high, r_lowk, r_highk, g_low, g_high]
