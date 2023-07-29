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

The allowed energy states of a physical system are the eigenvalues of the Hamiltonian describing the system (for example, see [@griffiths_introduction_2018]).  A *quanutum-level system* is generally considered to be such a system when the energy eigenstates are discrete, and a *level* is an energy state or set of (degenerate) states with a given energy eigenvalue.  The *multiplicity* of the level is the number of states with the given level energy.  A familiar example of a quantum level system is an atom or molecule, whose electrons arrange themselves into discrete energy levels; however, any physical system with discrete energy levels is, in our terminology, a quantum level system.

Interaction with the external world allows a quantum level system to transition between one level and another.  The rate of transition between levels depends on the details of the levels and the nature of the interaction between the system and the external world.  In an ensemble of quantum level systems in contact with a heat bath, there will be a probability of a given system existing in a particular level.  Level probabilities will evolve with time, but, as long as the heat bath changes slowly, the ensemble can achieve an equilibrium characterized by the temperature of the heat bath.

``lvlspy`` is a Python package for handling quantum level system data. The API was designed to provide an object-oriented data model that can be easily implemented with existing models or to act as a foundation for new models. The API handles multiple species, each of which has it own set of levels, characterized by their energy and multiplicity, and by rates of spontaneous transition between levels.  On top of handling level data, ``lvlspy`` has built-in functions that calculate induced transition rates from detailed balance, rate matrices, and equilibrium probabilites.  Optional properties may be added to any species, level, or spontaneous transition rate, and API routines allow the user to input the relevant data from XML with a well-defined schema.

Apart from permitting detailed calculations of the time-evolution of quantum level systems, educators can use ``lvlspy`` to build interactive tools and visual aids to supplement the course material. The source code for ``lvlspy`` has been archived to Zenodo at the linked DOI[@jaad_tannous_2023_8193379]

# References
