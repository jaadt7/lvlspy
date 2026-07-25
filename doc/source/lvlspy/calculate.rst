calculate
=========

Calculation extensions built on top of :mod:`lvlspy.core`.

Public helpers:

- ``fill_missing_transitions(sp, a)``: fill in absent transitions using
  Weisskopf estimates.
- ``normalize_parity_pair(parities)``: convert a parity pair from
  ``+``/``-`` strings to integer values.

.. toctree::
   :maxdepth: 1

   calculate/evolve
   calculate/weisskopf
   calculate/isomer
