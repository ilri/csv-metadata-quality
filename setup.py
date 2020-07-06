import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "pandas",
    "python-stdnum",
    "requests",
    "requests-cache",
    "pycountry",
    "langid",
]

setuptools.setup(
    name="csv-metadata-quality",
    version="0.4.2",
    author="Alan Orth",
    author_email="aorth@mjanja.ch",
    description="A simple, but opinionated CSV quality checking and fixing pipeline for CSVs in the DSpace ecosystem.",
    license="GPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alanorth/csv-metadata-quality",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    packages=["csv_metadata_quality"],
    entry_points={
        "console_scripts": ["csv-metadata-quality = csv_metadata_quality.__main__:main"]
    },
    install_requires=install_requires,
)
