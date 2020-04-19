import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cpp",
    version="0.2.0",
    author="Francois Laliberte-Auger, Pierre-Carl Michaud",
    author_email="francois.laliberte-auger@hec.ca",
    description="Module to simulate CPP and QPP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rsi-models/cpp",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "xlrd"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: To BE DETERMINE",
        "Operating System :: OS Independent",
    ]
)
