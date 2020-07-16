pip install build
rm dist/*
python setup.py sdist bdist_wheel 
twine upload --repository pypi dist/* --verbose