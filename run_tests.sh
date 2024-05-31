export _DO_NOT_IMPORT_JAVA=1

VERSION='3-10'
if [ $(python3 --version | grep -Eo '\.(.*)\.') = ".8." ]; then
    VERSION='3-8'
fi

PREFIX="scalpel/src/main/resources/python$VERSION"
cd $PREFIX
python3 -m unittest pyscalpel/tests/test_*.py qs/tests.py
