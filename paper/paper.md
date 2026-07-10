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
      affiliation: 2
    - name: Bradley S. Meyer
      orcid: 0000-0001-6307-9818
      equal-contrib: true
      affiliation: 1

affiliations:
    - name: Department of Physics and Astronomy, Clemson University, Clemson, SC, 29634
      index: 1
    - name: Department of Physics and Astrophysics, University of North Dakota, Grand Forks, ND, 58202
      index: 2

date: July 2026
bibliography: paper.bib
---

# Summary

The Python package `lvlspy` provides a framework for storing and manipulating generic quantum level system data, including level energies, multiplicities, and spontaneous transition rates. The core module provides fundamental functionality for constructing level systems and calculating induced transition rates from detailed balance, transition-rate matrices, and equilibrium populations. These calculations are particularly relevant for systems in thermal environments, where transition rates between excited states and the ground state determine the equilibrium distribution among levels [@gupta2001internal]. Additional properties can be attached to species, levels, and transitions without modifying the underlying data structures, allowing the package to accommodate diverse applications. The `io` module provides input and output routines for XML-based data exchange using a well-defined schema shared with [liblvls](https://liblvls.sourceforge.net), and supports import and export of the Evaluated Nuclear Structure Data File (ENSDF) format, which is widely used for experimentally determined nuclear structure data. A collection of additional calculation utilities, including system evolution and Weisskopf estimates, is provided in a separate module [@Kaplan1962-yy]. The modular architecture of `lvlspy` allows users to extend the package by adding new data formats, physical calculations, and analysis tools while maintaining compatibility with existing level-system objects. The source code for `lvlspy` has been archived on Zenodo [@tannous_2025_15121463].

# Statement of Need

Proper modeling of many physical and astrophysical phenomena requires detailed knowledge of the population of constituent atoms, molecules, or nuclei among their discrete energy levels and transition rates between those levels. For example, calculation of opacity in a stellar atmosphere requires knowledge of the abundance of different species, the levels available within each species, the fraction of each species occupying a given energy level, and the transition rates between levels (either spontaneous or induced). As another example, astromers, isotopes with long-lived isomeric states, can provide key information on various astronomical phenomena [@misch2020astromers]. Evaluating the impact of a given astromer requires calculating effective transition rates between long-lived isomeric states and the nuclear ground state in a thermal environment. This calculation depends on the transition rates among intermediate levels and requires efficient storage and manipulation of these rates, typically represented as matrices [@gupta2001internal].

Apart from their role in scientific research, models of quantum level systems provide valuable tools for exploring fundamental concepts in quantum mechanics. Energy-level diagrams introduce students to the discrete nature of quantum systems, but an interactive software framework that allows users to construct, modify, and evolve their own level systems can provide a more direct connection between theoretical concepts and computational modeling.

These applications demonstrate the need for a flexible software package capable of representing generic level systems, storing and retrieving information about levels and transitions, and calculating transition rates and equilibrium populations. Existing software, such as the C library liblvls, provides functionality for managing such systems but requires familiarity with C programming, external dependencies, and compilation. lvlspy provides a standalone Python interface that enables users to construct and analyze quantum level systems without requiring compilation or knowledge of lower-level programming languages.

The design of lvlspy emphasizes extensibility and interoperability. Level systems are represented using modular data structures that allow users to add or modify properties associated with species, levels, and transitions without altering the underlying framework. Input and output operations are separated from the core data structures, allowing additional data formats to be incorporated as needed. Similarly, calculation routines are implemented independently from the core representation of a level system, enabling users to add new physical models or analysis methods while preserving compatibility with existing objects. lvlspy supports XML-based data exchange through a well-defined schema shared with liblvls, as well as import and export of the Evaluated Nuclear Structure Data File (ENSDF) format used for experimentally determined nuclear structure data.

# Acknowledgements

This work was partially supported by NASA Emerging Worlds grant 80NSSC20K0338.  The authors thank G. Wendell Misch and Matthew Mumpower for valuable discussions and advice.

# References
