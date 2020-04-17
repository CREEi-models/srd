import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

class build_with_submodules(build):
    def run(self):
        if path.exists('.git'):
            check_call(['git', 'submodule', 'init'])
            check_call(['git', 'submodule', 'update'])
        build.run(self)

setuptools.setup(
    name="srd", # Replace with your own username
    version="0.0.1",
    author="Équipe CREEi",
    author_email="pierre-carl.michaud@hec.ca",
    description="Modele de simulation du revenu disponible",
    long_description=long_description,
    long_description_content_type="text/markdown",
    cmdclass={"build": build_with_submodules},
    url="https://creei-models.github.io/srd/",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)