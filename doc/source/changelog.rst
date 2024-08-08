Changelog
=========

All notable changes to this project will be documented in this file.  This
project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

Version 3.1.0
-------------

New:

  * Modularized the IO for various fomats have been setup. Currently ENSDF and XML are
    supported.
  

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

