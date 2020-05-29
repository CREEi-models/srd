import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="srd", # Replace with your own username
    version="0.1.0",
    author="Équipe CREEi",
    author_email="pierre-carl.michaud@hec.ca",
    description="Modele de simulation du revenu disponible Quebec",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://creei-models.github.io/srd/",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
   'pandas',
   'numpy',
   'xlrd',
   'srpp'
    ],
    python_requires='>=3.6',
)