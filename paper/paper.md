---
title: 'lvlspy: A Python Package for Quantum Level Systems'
tags:
    - python
    - nuclear physics
    - atomic physics
authors:
    - name: Jaad A. Tannous
      orcid: 0000-0002-9970-6454
      equal-contrib: true
      affiliation: "1, 2"
    - name: Bradley S. Meyer
      orcid: 0000-0001-6307-9818
      equal-contrib: true
      affiliation: 1

affiliations:
    - name: Department of Physics and Astronomy, Clemson University, Clemson, SC, 29634
      index: 1
    - name: Department of Physics and Astrophysics, University of North Dakota, Grand Forks, ND, 58202
      index: 2

date: 22 July 2026
bibliography: paper.bib
---

# Summary

Many physical systems are naturally described by discrete energy levels and transitions between them. Examples include atoms, molecules, and nuclei. In these systems, the state of a system is described by a level energy and a multiplicity, and transitions between levels determine how populations change with time and temperature [@griffiths_introduction_2018].

``lvlspy`` is an open-source Python package for representing and analyzing quantum level systems. Its core package provides classes for levels, transitions, species, and collections of species. Extension modules provide XML and ENSDF input and output, level-population evolution, Weisskopf estimates, and isomer-related calculations. The package is organized so that the core data model remains stable while format-specific and calculation-specific functionality can grow in extension modules.

# Statement of Need

Many scientific workflows require detailed knowledge of how a population is distributed among discrete energy levels and how those populations change through spontaneous and induced transitions. In astrophysics, opacity calculations depend on the level structure and transition network of each species. In nuclear physics, long-lived isomeric states can strongly affect reaction flow and thermal equilibration, so evaluating effective rates between isomeric and ground states requires a model that can represent the full level network [@misch2020astromers; @gupta2001internal].

`lvlspy` addresses this need with a Python interface for storing and manipulating level data, computing equilibrium populations and transition-rate matrices, and exchanging level systems with external data formats. A related C library, `liblvls` (<https://liblvls.sourceforge.net>), offers similar functionality, but `lvlspy` is intended to be easier to install, script, and extend in Python workflows. Its XML support uses the same schema family as `liblvls`, which helps users move data between tools without redefining the underlying level structure.

# State of the field

Packages for discrete level systems generally fall into two groups: code focused on one data source or one calculation, and lower-level libraries that expose the entire workflow in a less extensible form. `lvlspy` is designed to sit between those extremes. It provides a general representation for level systems while still supporting common nuclear-data formats and calculation routines.

Compared with `liblvls`, `lvlspy` emphasizes a Python-first interface and a modular package layout. That makes it easier to integrate into analysis scripts, notebooks, and automated pipelines. It also leaves room for future extensions, such as additional import/export formats or graphical tools, without expanding the core domain model.

# Software design

`lvlspy` is organized around a stable core and optional extensions. The `lvlspy.core` package contains the domain model: levels, transitions, species, and species collections. These objects provide the basic operations needed to build and query level systems, including updates, collection management, equilibrium probabilities, and rate matrices.

The `lvlspy.extensions` package contains functionality that is specific to a format or a calculation method. `lvlspy.extensions.io` provides XML and ENSDF import/export. `lvlspy.extensions.calculate` provides time evolution, Weisskopf estimates, and isomer-related rate calculations. This separation keeps parsing rules and specialized numerical routines out of the core domain model, which makes the core easier to test and maintain.

The public import structure keeps the core domain classes available through a
simple top-level API, while specialized functionality is exposed explicitly
through `lvlspy.extensions`.

# Research impact statement

`lvlspy` is intended to support research workflows in nuclear physics and related fields where discrete level systems are central. It can be used to assemble level data from external sources, compute thermodynamic populations, evolve populations in time, and estimate effective rates for isomeric systems.

The package is also useful as a bridge between archived nuclear-data formats and analysis code. In practice, that means it can support data preparation, workflow automation, and prototyping for studies that depend on level networks and transition rates. Its modular structure should also make it straightforward to add future capabilities such as new file formats or visualization-oriented extensions.

Because XML and ENSDF inputs populate the same core model, the package also supports reproducible comparisons between data sources and downstream calculations.

# AI usage disclosure

Generative AI tools were used to assist with drafting and revising this paper. The authors reviewed the text, verified the scientific content, and edited the final version.

# Acknowledgements

Development of `lvlspy` began while both authors were affiliated with Clemson
University; Tannous is now affiliated with the University of North Dakota.

This work was partially supported by NASA Emerging Worlds grant 80NSSC20K0338.
The authors thank G. Wendell Misch and Matthew Mumpower for valuable discussions
and advice.

# References
