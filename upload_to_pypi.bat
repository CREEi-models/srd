:: this does not work on dropbox; clone somewhere else before executing this file
del /q dist
python setup.py sdist bdist_wheel 
twine upload --repository pypi dist/* --verbose

:: username: creei-models, password: 12116!Pcm