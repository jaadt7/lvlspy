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
      equal-contrib: true
      affiliation: 1

affiliations:
    - name: Department of Physics and Astronomy, Clemson University, Clemson, SC, 29634
      index: 1

date: July 15 2023
bibliography: paper.bib
---

# Summary

The shell model is a quantum mechanical model which approximates how the sub-atomic particles of the atom organize themselves in orbitals (shells). This organization is based on three principle quantum numbers n,l, and s which represent the particle's total energy, orbital angular momentum, and the spin projection along the z-axis respectively. According to the Pauli exclusion principle, no two identical fermions can occupy the same quantum state. In combination with the energy and angular momentum, the maximum number of fermions that a shell can hold is dictated. The full derivation can be found in any quantum mechanics book [@griffiths_introduction_2018][@sakurai1995modern]. Applications cover, but are not restricted to, atomic structure, molecular excitations, and nuclear structure. The model allows for communication between the levels, a principle that acts as the basis for the development of this package.

``lvlspy`` is a Python package for handling quantum level system data. The API for ``lvlspy`` was designed to provide an object-oriented data model that can be easily implemented with existing models or to act as a foundation for new models. On top of handling the level data, ``lvlspy`` has built-in functions which calculate thermodynamic quantities at a given temperature, such as equilibrium probabilities and rate matrices.

``lvlspy`` was designed with nuclear physicists in mind who are interested in studying internal transitions of nuclear levels. This can easily be extended to atomic, molecular, and optical (AMO) physicists and chemists alike who are interested in analyzing atomic structure in highly charged states, atoms, and molecules. On the educational level, the package can be used in courses to build interactive tools and visual aids to supplement the course material. The source code for ``lvlspy`` has been archived to Zenodo at the linked DOI

# References