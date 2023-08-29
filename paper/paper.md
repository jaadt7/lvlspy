---
title: 'lvlspy: A Python Package for Quantum Level Systems'
tags:
    - python
    - nuclear levels
    - atomic levels
authors:
    - name: Jaad A. Tannous
      orcid: 0000-0002-9970-6454
      equal-contrib: true
      affiliation: 1
    - name: Bradley S. Meyer
      orcid: 0000-0001-6307-9818
      equal-contrib: true
      affiliation: 1

affiliations:
    - name: Department of Physics and Astronomy, Clemson University, Clemson, SC, 29634
      index: 1

date: July 15 2023
bibliography: paper.bib
---

# Summary

Atoms and molecules are examples of quantum level systems in which the allowed energy states take on discrete values.  These states, which are eigenstates of the system's Hamiltonian, are *levels*, which are characterized by the energy relative to the lowest energy level (the "ground state") and by their *multiplicity* if a set of states has exactly the same energy, in which case the states are *degenerate* (for example, see [@griffiths_introduction_2018]).  Interaction with the external world allows a quantum level system to transition between one level and another.  The rate of transition between levels depends on the details of the levels and the nature of the interaction between the system and the external world.  In an ensemble of quantum level systems in contact with the external world at a given temperature (a "heat bath"), there will be a probability of a given system existing in a particular level.  Level probabilities will evolve with time, but, as long as the heat bath changes slowly compared to transition times between levels, the ensemble can achieve an equilibrium characterized by the temperature of the heat bath.  ``lvlspy'' is a Python package that stores generic quantum level system data, particularly level energies, multiplicities, and spontaneous transition rates, and includes built-in functions that calculate induced transition rates from detailed balance, rate matrices, and equilibrium probabilites.  Optional properties may be added to any species, level, or spontaneous transition rate, and API routines allow the user to input the relevant data from XML with a well-defined schema.

# Statement of Need

Apart from permitting detailed calculations of the time-evolution of quantum level systems, educators can use ``lvlspy`` to build interactive tools and visual aids to supplement course material in chemistry or physics classes. The source code for ``lvlspy`` has been archived to Zenodo at the linked DOI[@jaad_tannous_2023_8193379]

# Acknowledgments

This work was partially supported by NASA Emerging Worlds grant 80NSSC20K0338.  The authors that G. Wendell Misch and Matt Mumpower for valuable discussions and advice.

# References
