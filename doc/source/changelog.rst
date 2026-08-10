Changelog
=========

All notable changes to this project will be documented in this file.  This
project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

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
    aligned its return values with the documented vector and scalar structure.
    Callers relying on the previous duplicated scalar values must be updated.
  * Corrected ENSDF spin-parity range parsing to advance by whole spin units
    and to apply common, endpoint-specific, and unspecified parities according
    to the ENSDF format specification.
  * Defined the zero-temperature transition-rate limit so that induced
    absorption and emission vanish while spontaneous decay remains.
  * Changed XML validation to raise ``lxml.etree.DocumentInvalid`` when a
    document does not conform to the species collection schema instead of
    silently returning the same result as a valid document.
  * Fixed rate-matrix filtering to honor the ENSDF ``useability`` level flag
    while retaining ``useable`` as a backwards-compatible alias.
  * Included a pinned XML schema snapshot in source and wheel distributions so
    validation works after a standard installation without a build-time schema
    download.
  * Refreshed the pinned XML schemas to the 2026-07-25 upstream revision,
    updated their published namespace URLs, and corrected the XML catalog
    mapping for ``zone_types.xsd``.
  * Corrected ENSDF spin-only assignments so unknown parity is not silently
    treated as a definite positive parity, and made parity-only assignments
    safe to parse.
  * Corrected grouped ENSDF alternatives such as ``(3,4)-`` so the parity
    outside the parentheses applies to every spin in the group.
  * Disabled XML external-entity resolution, network access, and automatic
    XInclude processing. XInclude now requires an explicit opt-in argument.
  * Corrected effective isomer transition rates to include direct transitions
    between the two reference levels in addition to paths through intermediate
    levels.
  * Preserved half-integer nuclear spins when computing Weisskopf estimates so
    odd-mass nuclei use the correct range of photon multipoles in ordinary and
    ambiguous ENSDF transition paths.
  * Stabilized equilibrium probabilities by using excitation energies relative
    to the ground state and weighting degenerate ground levels by
    multiplicity at zero temperature.
  * Fixed ENSDF export for transitions without the optional reduced-matrix
    coefficient and ensured continuation records end on their own line.
  * Normalized ENSDF reduced-matrix coefficient values in memory while
    reconstructing the fixed-width continuation record only when writing ENSDF
    output.
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
  * Removed the legacy top-level core modules in favor of the explicit
    ``lvlspy.core`` package, making the import-path change a documented
    breaking change for version 5.0.0.
  * Removed the legacy ``lvlspy.calculate`` and ``lvlspy.io`` compatibility
    packages; calculation and input/output APIs now live exclusively under
    ``lvlspy.extensions``.
  * Performed an architectural package refactor by splitting the layout into
    ``lvlspy.core`` for the domain model and ``lvlspy.extensions`` for
    calculation and IO functionality.
  * Moved ``fill_missing_transitions()`` out of ``Species`` and replaced the
    parity-normalization helper with an extension-layer API, keeping the core
    model free of extension-layer behavior.
  * Moved the ENSDF spin-expression parser out of ``lvlspy.core`` and into the
    ENSDF extension layer, keeping core properties free of format-specific
    parsing logic.

Internal:

  * Added regression tests for sparse evolution, population conservation,
    fugacity calculation, level energy updates, XML transition round trips,
    ensemble weights with non-default reference levels, ENSDF spin-parity
    variants, and zero-temperature transition rates.
  * Added tests for XML schema validation, rate-matrix filtering and
    conservation, direct and cascade isomer rates, half-integer spin handling,
    energy-offset invariance, low-temperature probabilities, ENSDF
    continuation records, zero-rate isomer edge cases, XML round trips for
    legacy and canonical flags, renamed species, Einstein-A and multiplicity
    validation, solve-based isomer linear algebra, evolution input validation,
    ENSDF fixed-width record hardening, XML transition references, XML
    property-key validation, and negative-temperature thermal calculations.
  * Added SciPy to the declared runtime dependencies because the evolution and
    Weisskopf calculation modules require it.
  * Replaced ``setup.py`` metadata with ``pyproject.toml``, added schema
    provenance and update tooling, and configured schema imports to resolve
    locally with network access disabled.
  * Updated the documentation, package metadata, tests, and build tooling to
    reflect the new layout and preserve the vendored XML schema resources in
    the relocated XML package.

Version 4.0.0
-------------

New:

  * Added modular IO support for ENSDF and XML.
  * Added a calculations module to evolve a system and calculate Weisskopf estimates.
  * Added an isomer module for calculations relevant to isomers.
  * Added support for changing the name of a species, which is useful when
    converting between formats.
  * Added a check for usable levels when calculating the rate matrix.
  * Added support for filling in undefined or missing transitions in a species.

Fix:

  * Linked the application to the README.

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
