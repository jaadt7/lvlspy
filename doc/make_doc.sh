rm -f source/lvlspy.*.rst
mkdir -p source/_static source/_templates
sphinx-apidoc -M -f -n -o source ../lvlspy
make html
