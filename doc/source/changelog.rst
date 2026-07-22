Changelog
=========

All notable changes to this project will be documented in this file.  This
project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

Version 5.0.0
-------------

Fix:

  * Fixed the sparse CSC evolution solver so that each output column contains
    the evolved state at its requested time.
  * Corrected ``Level.update_energy()`` to convert eV, keV, MeV, and GeV to the
    internal keV representation consistently with level construction.
  * Fixed XML transition imports for degenerate and arbitrarily ordered levels
    by resolving destinations using both energy and multiplicity after all
    levels have been loaded.
  * Corrected ``ensemble_weights()`` for arbitrary reference-level indices and
    made its return values match the documented vector and scalar structure.
    Callers relying on the previous duplicated scalar values must be updated.
  * Corrected ENSDF spin-parity range parsing to advance by whole spin units
    and to apply common, endpoint-specific, and unspecified parities according
    to the ENSDF format specification.
  * Defined the zero-temperature transition-rate limit so that induced
    absorption and emission vanish while spontaneous decay remains.
  * Changed XML validation to raise ``lxml.etree.DocumentInvalid`` for documents
    that do not conform to the species collection schema instead of silently
    returning the same result as a valid document.
  * Fixed rate-matrix filtering to honor the ENSDF ``useability`` level flag
    while retaining ``useable`` as a backwards-compatible alias.
  * Included a pinned XML schema snapshot in source and wheel distributions so
    validation works after a standard installation without a build-time schema
    download.
  * Corrected ENSDF spin-only assignments so unknown parity is not silently
    treated as a definite positive parity, and made parity-only assignments
    safe to parse.
  * Corrected grouped ENSDF alternatives such as ``(3,4)-`` so the parity
    outside the parentheses applies to every spin in the group.
  * Disabled XML external-entity resolution, network access, and automatic
    XInclude processing. XInclude is now available only through an explicit
    opt-in argument on XML validation and import.
  * Corrected effective isomer transition rates to include direct transitions
    between the two reference levels in addition to paths through intermediate
    levels.
  * Preserved half-integer nuclear spins when computing Weisskopf estimates so
    odd-mass nuclei use the correct range of photon multipoles in ordinary and
    ambiguous ENSDF transition paths.
  * Stabilized equilibrium probabilities by using excitation energies relative
    to the ground state and corrected the zero-temperature limit to weight
    degenerate ground levels by multiplicity.
  * Fixed ENSDF export for transitions without the optional reduced-matrix
    coefficient and ensured supplied continuation records end on their own
    line.
  * Prevented division by zero in isomer branching probabilities when a
    reference or intermediate level has no outgoing transitions, keeping
    effective and cascade rates finite at zero temperature.
  * Fixed ENSDF gamma-energy parsing for blank fields and for symbolic offsets
    written before or after the numeric energy, such as ``X+100`` and
    ``100+X``.
  * Preserved Boolean ``useability`` and legacy ``useable`` flags across XML
    round trips so excluded levels remain absent from rate matrices.
  * Preserved ENSDF level energy uncertainties during export and re-import by
    using the canonical ``energy uncertainty`` property key while accepting
    ``energy_uncertainty`` as a compatibility alias.
  * Prevented blank, symbolic-only, and unresolved zero-energy ENSDF gamma
    records from being linked back to their emitting level as self-transitions.
  * Kept species collections synchronized with species renames so lookups,
    removals, and XML export use the current species name.
  * Rejected non-finite and negative Einstein ``A`` coefficients in transition
    construction and updates instead of propagating invalid rates through later
    calculations.
  * Rejected zero, negative, nonintegral, and non-finite level multiplicities
    in construction and updates instead of letting invalid statistical weights
    reach later calculations.
  * Replaced explicit matrix inversion in isomer transfer calculations with a
    direct solve and a descriptive singular-system error.
  * Validated evolution inputs and changed Newton-Raphson convergence to use
    the absolute correction magnitude instead of the signed maximum component.
  * Hardened ENSDF reduced-matrix-coefficient parsing so malformed continuation
    records raise descriptive errors instead of failing with index or value
    errors.
  * Rejected ENSDF output values that do not fit in their fixed-width level or
    gamma fields instead of emitting malformed records.
  * Changed XML import to raise a descriptive error when a transition refers
    to a destination energy and multiplicity that are absent, instead of
    silently dropping the transition.
  * Replaced process-terminating and accidental errors for malformed XML
    optional-property keys with descriptive ``ValueError`` exceptions.
  * Rejected nonpositive energy gaps in default radiative transition-rate
    calculations instead of producing zero-frequency divisions or nonphysical
    rates, while retaining custom-rate support for specialized models.
  * Rejected negative temperatures in Boltzmann and default blackbody
    calculations instead of returning overflowed or negative thermal rates,
    while preserving the zero-temperature limits and custom callbacks.

Internal:

  * Added analytic regression tests for sparse evolution, population
    conservation, fugacity calculation, level energy updates, and XML
    transition round trips, as well as ensemble weights with non-default
    reference levels, ENSDF spin-parity range variants, and zero-temperature
    transition rates, together with valid and invalid XML schema checks and
    rate-matrix filtering and conservation, plus definite and incomplete ENSDF
    spin-parity assignments and grouped-parity alternatives, and effective
    rates containing direct and cascade contributions, plus half-integer spin
    conversion and Weisskopf multipole selection, energy-offset invariance, and
    zero- and low-temperature equilibrium probabilities, plus ENSDF transition
    round trips with and without reduced-matrix continuation records, and
    zero-rate reference and disconnected intermediate isomer levels, plus
    blank and symbolic-offset ENSDF gamma energies, and XML round trips of
    canonical and legacy level-usability flags, plus ENSDF level energy
    uncertainties using canonical and legacy property names, and unresolved
    gamma records that must not produce self-transitions, plus renamed-species
    collection synchronization, plus Einstein-A validation, plus multiplicity
    validation, plus isomer solve-based linear algebra, plus evolution input
    validation and absolute-convergence Newton iteration, plus ENSDF RMC and
    fixed-width field hardening, plus missing-energy and wrong-multiplicity XML
    transition references, and invalid XML optional property key and attribute
    shapes, plus degenerate and reversed radiative transitions and custom
    nonradiative rate callbacks, and negative-temperature thermal calculations.
  * Added SciPy to the declared runtime dependencies because it is required by
    the evolution and Weisskopf calculation modules.
  * Replaced ``setup.py`` metadata with ``pyproject.toml``, added schema
    provenance and update tooling, and made schema imports resolve locally with
    network access disabled.

Version 4.0.0
-------------

New:

  * Added and modularized the IO for various formats have been setup. Currently ENSDF and XML are
    supported.
  * Added calculations module to evolve a system and calculate Weisskopf estimates.
  * Added isomer module in the caculation module that handles calculation relevant to isomers.
  * Added feature in species to change the name of a species. Particularly helpful when going
    between formats.
  * Added check for useable level when calculating rate matrix. 
  * Added feature that fills in undefined or missing transitions in a species.

Fix:

  * Linked the application to the readme

Version 3.0.3
-------------

Fix:

  * Removing a level now removes all transitions to and from the level before removing 
    the level itself. This alleviates any issues that arise after removing the level.

Version 3.0.2
-------------

Fix:

  * Version mismatch has been addressed

Version 3.0.1
-------------

Fix:

  * sphinx-rtd-theme has been added to the documentation requirements to properly 
    compile on Read the Docs

Version 3.0.0
-------------

Fix:

  * Misleading methods to retrieve upward and downward transitions have been
    replaced with methods to retrieve levels linked by transitions to a
    given level.  This is a backwards-incompatible change.
  * If a level or transition already exists in the respective collection,
    the API now updates the level or transition instead of adding a new version.
  * An overflow on the Boltzmann factor for zero temperature has been fixed.
  * The extraneous search has been removed from the index.
  * The instructions for exporting the appropriate software reference from
    Zenodo are now clearer.
 

Version 2.0.0
-------------

New:

  * Tests and linting have been added to the package integration.
  * New methods to update a transition's Einstein A coefficient, retrieve
    upward and downward transitions from a level, and to retrieve a transition
    between particular levels have been added to the API.

Fix:

  * A number of method names have been changed to align with pylint.  These are
    backwards-incompatible changes.

Version 1.4.0
-------------

New:

  * A link to the readthedocs page has been added to the overview to increase visibility.

Version 1.3.0
-------------

Internal:

  * Astropy has been replaced with gslconsts for consistency with Webnucleo codes.

Version 1.2.0
-------------

New:

  * An Acknowledgment has been added.

Internal:

  * The XML validator now uses XML Catalogs.  The appropriate schemas are
    included in the distribution.
  	
Version 1.1.1
-------------

Fix:

  * Updated ReadMe with note about installing the package with Anaconda
  	
  	
Version 1.1.0
-------------

New:

  * It is now possible to select species to update from XML with an XPath
    expression.

Fix:

  * Non-string properties are now properly written to XML as strings.

Version 1.0.2
-------------

Internal:

  * A required package has been added to the documentation

Version 1.0.1
-------------

Internal:

  * The base class Properties namespace has been renamed.
  * A configuration variable has been set to avoid warnings.

Fix:

  * A URL link has been fixed.
  * Some documentation has been extended.

Version 1.0.0
-------------

New:

  * Initial release
