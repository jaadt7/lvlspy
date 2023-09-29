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

Atoms and molecules are examples of quantum level systems in which the allowed energy states take on discrete values.  These states, which are eigenstates of the system's Hamiltonian, are *levels*, which are characterized by the energy relative to the lowest energy level (the "ground state"), and by their *multiplicity* which accounts for states that have exactly the same energy, in which case the states are *degenerate* (for example, see [@griffiths_introduction_2018]).  Interaction with the external world allows a quantum level system to transition between one level and another.  The rate of transition between levels depends on the details of the levels and the nature of the interaction between the system and the external world.  In an ensemble of quantum level systems in contact with the external world at a given temperature (a "heat bath"), there will be a probability of a given system existing in a particular level.  Level probabilities will evolve with time, but, as long as the heat bath changes slowly compared to transition times between levels, the ensemble can achieve an equilibrium characterized by the temperature of the heat bath.  

The Python package ``lvlspy`` stores generic quantum level system data, particularly level energies, multiplicities, and spontaneous transition rates, for levels in any species.  The API includes built-in functions that calculate induced transition rates from detailed balance, rate matrices, and equilibrium probabilites.  Optional properties may be added to any species, level, or spontaneous transition rate, and API routines allow the user to input the relevant data from XML with a well-defined schema.  The source code for ``lvlspy`` has been archived to Zenodo at the linked DOI [@jaad_tannous_2023_8193379].  

# Statement of Need

Proper modeling of many physical and astrophysical phenomena requires detailed knowledge of the population of constituent atoms, molecules, or nuclei among their discrete energy levels and transition rates between those levels.  For example, calculation of opacity in a stellar atmosphere requires knowledge of the abundance of different species in the atmosphere, the levels in each species, the fraction of each species that exists in a given energy level, and the transition rate to a different level (either spontaneous or induced).  As another example, *astromers*, isotopes with long-lived isomeric states, can provide key information on various astronomical phenomena [@misch2020astromers].  In order to evaluate the importance of a given astromer, howeever, one requires calculation of the effective transition rates between the long-lived isomer and the ground state of the nucleus in a heat bath, which, in turn, requires knowledge of transition rates between energy levels and efficient storage of those rates in an easily managed data structure, such as a matrix [@gupta2001internal].

Apart from their key role in scientific research, models of quantum level systems provide excellent insight into quantum mechanics.  Energy-level diagrams in a textbook introduce the essential ideas behind such systems, but a simple-to-use software package that allows students to build their own level systems will greatly reinforce those ideas.

These examples point to the need for a straightforward software package that is able to store and retrieve data about generic level systems, add, remove, and update information about levels, and compute transition rates between levels and their equilibrium populations.  A C library [liblvls](https://liblvls.sourceforge.net) is available for carrying out these tasks but requires familiarity with C, installation of a number of libraries, and compilation of the codes.  ``lvlspy`` is a stand-alone Python package that has most of the same features as *liblvls* but is easier to install and use.  ``lvlspy`` also has routines to read data from and store data to XML with a well-defined [schema](https://liblvls.sourceforge.net/xsd_pub/2022-10-14/spcoll.xsd), which it shares with liblvls.

# Acknowledgements

This work was partially supported by NASA Emerging Worlds grant 80NSSC20K0338.  The authors thank G. Wendell Misch and Matt Mumpower for valuable discussions and advice.

# References
