# Script to automate build for PyPI.

rm -fr dist
cd lvlspy/io/xml
rm -fr xsd_pub
git clone https://bitbucket.org/mbradle/liblvls_xsd.git xsd_pub
cd ../..
black --line-length=79 *.py
pylint --extension-pkg-whitelist=lxml.etree --fail-under=9.9 *.py io/*.py calculate/*.py

cd ../.github/workflows/
pytest
cd ../..

python -m pip install --upgrade twine
python -m pip install --upgrade build
python -m build

echo ""
echo "All version numbers must be the same:"
echo ""

grep version lvlspy/__about__.py | grep -v ","
grep version CITATION.cff | grep -v "cff-version"
grep Version doc/source/changelog.rst | grep -v Versioning | head -1
grep version pyproject.toml

echo ""
echo "Check the release date:"
echo ""
grep date CITATION.cff
echo ""
