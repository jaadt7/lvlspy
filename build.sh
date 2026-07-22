# Script to automate build for PyPI.

set -e

rm -fr dist

python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pip install black pylint

python -m pytest -v tests

python -m black --check --verbose --line-length=79 ./lvlspy
python -m pylint --extension-pkg-whitelist=lxml.etree --fail-under=9.9 \
    lvlspy

python -m pip install --upgrade build
python -m build

echo ""
echo "All version numbers must be the same:"
echo ""

grep version lvlspy/__about__.py | grep -v ","
grep version CITATION.cff | grep -v "cff-version"
grep Version doc/source/changelog.rst | grep -v Versioning | head -1

echo ""
echo "Check the release date:"
echo ""
grep date CITATION.cff
echo ""
