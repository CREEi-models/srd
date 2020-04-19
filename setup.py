import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="srd", # Replace with your own username
    version="0.0.1",
    author="Équipe CREEi",
    author_email="pierre-carl.michaud@hec.ca",
    description="Modele de simulation du revenu disponible",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://creei-models.github.io/srd/",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=['git+https://github.com/creei-models/cpp']
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)