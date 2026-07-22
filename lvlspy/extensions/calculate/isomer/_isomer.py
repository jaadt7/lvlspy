"""
Module to handle isomer related calculations. Functions are built based on the method in
`Gupta and Meyer (2001) <https://ui.adsabs.harvard.edu/abs/2001PhRvC..64b5805G/abstract>`_
"""

import numpy as np


def _safe_divide(numerator, denominator):
    """Divide rates while assigning zero where the total rate is zero."""

    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)
    return np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator, dtype=float),
        where=denominator != 0,
    )


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

    f_low_out = _safe_divide(lambda_low_out, lambda_sum[level_low])
    f_high_out = _safe_divide(lambda_high_out, lambda_sum[level_high])

    f_low_in = _safe_divide(lambda_low_in, lambda_red)
    f_high_in = _safe_divide(lambda_high_in, lambda_red)

    # setting up the transfer matrix
    tpm = rate_matrix
    tpm = tpm.T
    # remove the columns
    tpm = np.delete(tpm, [level_low, level_high], axis=1)
    # remove the rows
    tpm = np.delete(tpm, [level_low, level_high], axis=0)

    # Divide the row by the diagonal term
    tpm = _safe_divide(tpm, lambda_red[:, None])

    # set the diagonal to 0
    np.fill_diagonal(tpm, 0.0)

    return [tpm, f_low_in, f_low_out, f_high_in, f_high_out, lambda_sum]


def _solve_transfer_system(transfer_matrix, rhs, level_low, level_high):
    """Solve the reduced transfer system or raise a descriptive error."""

    if transfer_matrix.size == 0:
        return np.zeros_like(rhs, dtype=float)

    system = np.identity(len(transfer_matrix)) - transfer_matrix

    if np.linalg.matrix_rank(system) < system.shape[0]:
        raise ValueError(
            "Isomer transfer system is singular for reference levels "
            f"{level_low} and {level_high}"
        )

    try:
        return np.linalg.solve(system, rhs)
    except np.linalg.LinAlgError as exc:
        raise ValueError(
            "Isomer transfer system is singular for reference levels "
            f"{level_low} and {level_high}"
        ) from exc


def effective_rate(t, sp, level_low=0, level_high=1):
    """
    Method to calculate the effective transition rates between the isomeric and ground states

    Args:
        ``t`` (:obj:`float`) The temperature in K.

        ``sp`` (:obj:`lvlspy.core.species.Species`) The species of which the level system belongs to.

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
    # f_n = _partial_sum(trans_props[0])

    reduced_transfer = trans_props[0]

    # Lambda_high_low_eff: direct transition plus all paths through
    # intermediate levels.
    l_high_low = rate_matrix[level_low, level_high] + trans_props[5][
        level_high
    ] * np.matmul(
        trans_props[4].T,
        _solve_transfer_system(
            reduced_transfer, trans_props[1], level_low, level_high
        ),
    )
    # Lambda_low_high_eff: direct transition plus all paths through
    # intermediate levels.
    l_low_high = rate_matrix[level_high, level_low] + trans_props[5][
        level_low
    ] * (
        np.matmul(
            trans_props[2].T,
            _solve_transfer_system(
                reduced_transfer.T, trans_props[3], level_low, level_high
            ),
        )
    )

    return (
        l_low_high,
        l_high_low,
    )


def cascade_probabilities(t, sp, level_low=0, level_high=1):
    """
    Method to calculate the cascace probability vectores (gammas)

    Args:
        ``t`` (:obj:`float`) The temperature in K

        ``sp`` (:obj:`lvlspy.core.species.Species`) The species of which the
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

    # f_n = _partial_sum(trans_props[0])

    reduced_transfer = trans_props[0]

    g1_in = _solve_transfer_system(
        reduced_transfer, trans_props[1], level_low, level_high
    )
    g2_in = _solve_transfer_system(
        reduced_transfer, trans_props[3], level_low, level_high
    )

    g1_out = _solve_transfer_system(
        reduced_transfer.T, trans_props[2], level_low, level_high
    )
    g2_out = _solve_transfer_system(
        reduced_transfer.T, trans_props[4], level_low, level_high
    )

    return [g1_in, g2_in, g1_out, g2_out]


def ensemble_weights(t, sp, level_low=0, level_high=1):
    """
    Method to calculate the ensemble weights

    Args:
        ``t`` (:obj:`float`) The temperature in K

        ``sp`` (:obj:`lvlspy.core.species.Species`) The species of which the ensemble weights
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
    eq_prob = sp.compute_equilibrium_probabilities(t)
    gammas = cascade_probabilities(t, sp, level_low, level_high)
    w_low, w_high, big_w_low, big_w_high, r_lowk, r_highk = (
        _build_ensemble_weights(eq_prob, gammas, level_low, level_high)
    )
    levels = sp.get_levels()
    g_low = levels[level_low].get_multiplicity() * big_w_low
    g_high = levels[level_high].get_multiplicity() * big_w_high

    return [
        w_low,
        w_high,
        big_w_low,
        big_w_high,
        r_lowk,
        r_highk,
        g_low,
        g_high,
    ]


def _build_ensemble_weights(eq_prob, gammas, level_low, level_high):
    """Construct the ensemble weight arrays and intermediate ratios."""

    n = len(eq_prob)
    intermediate_levels = [
        i for i in range(n) if i not in (level_low, level_high)
    ]
    r_lowk = eq_prob[intermediate_levels] / eq_prob[level_low]
    r_highk = eq_prob[intermediate_levels] / eq_prob[level_high]

    w_low = np.zeros(n)
    w_high = np.zeros(n)
    w_low[level_low] = 1.0
    w_high[level_high] = 1.0
    w_low[intermediate_levels] = gammas[0] * r_lowk
    w_high[intermediate_levels] = gammas[1] * r_highk

    return (
        w_low,
        w_high,
        np.sum(w_low),
        np.sum(w_high),
        r_lowk,
        r_highk,
    )
