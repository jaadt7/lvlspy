# Vendored XML schemas

This directory contains the XML schemas required by `lvlspy` validation. They
are vendored so normal checkouts, tests, installations, and builds do not fetch
schemas or depend on mutable upstream schema state.

The schemas and `catalog` come from
<https://bitbucket.org/mbradle/liblvls_xsd>.

Upstream commit: `c5bdac63adff854d42711a1efaa92a654d51056e`

The same revision is recorded in the repository-root `XSD_REVISION` file. The
schema files retain their original GPL-2.0-or-later notices; `lvlspy`
distributes them under those terms alongside its GPL-3.0-or-later code.

Maintainers update this snapshot with:

```console
tools/update_xsd_pub.sh <full-upstream-commit-sha>
```

The tool checks the expected file set, copies only approved schema files,
updates `XSD_REVISION`, runs the unit suite, builds the package, and verifies
the wheel contents. It leaves the resulting source changes uncommitted for
review.
