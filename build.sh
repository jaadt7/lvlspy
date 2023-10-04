# Script to automate build for PyPI.

rm -fr dist
cd lvlspy
rm -fr xsd_pub
git clone https://bitbucket.org/mbradle/liblvls_xsd.git xsd_pub
cd ..

OS=$($uname -s)
if [OS = 'Linux']; then
    python3 -m pip install --upgrade build
    python3 -m build
else
    python -m pip install --upgrade build
    python -m build
fi