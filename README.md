# CSV Metadata Quality [![Build Status](https://travis-ci.org/alanorth/csv-metadata-quality.svg?branch=master)](https://travis-ci.org/alanorth/csv-metadata-quality) [![builds.sr.ht status](https://builds.sr.ht/~alanorth/csv-metadata-quality.svg)](https://builds.sr.ht/~alanorth/csv-metadata-quality?)
A simple but opinionated metadata quality checker and fixer designed to work with CSVs in the DSpace ecosystem. Supports multi-value fields using the standard DSpace value separator ("||"). Despite the name it does support reading Excel files.

Requires Python 3.6 or greater. CSV and Excel support comes from the [Pandas](https://pandas.pydata.org/) library.

## Functionality

- Read/write CSV files
- Read Excel files
- Validate dates, ISSNs, ISBNs, and multi-value separators ("||")
- Validate languages against ISO 639-2 and ISO 639-3
- Validate subjects against AGROVOC REST API
- Fix leading, trailing, and excessive whitespace
- Fix invalid multi-value separators (`|`) using `--unsafe-fixes`
- Remove unnecessary Unicode like [non-breaking spaces](https://en.wikipedia.org/wiki/Non-breaking_space), [replacement characters](https://en.wikipedia.org/wiki/Specials_(Unicode_block)#Replacement_character), etc
- Check for "suspicious" characters that indicate encoding or copy/paste issues, for example "foreˆt" should be "forêt"
- Remove duplicate metadata values

## Installation
The easiest way to install CSV Metadata Quality is with [pipenv](https://github.com/pypa/pipenv):

```
$ git clone https://git.sr.ht/~alanorth/csv-metadata-quality
$ cd csv-metadata-quality
$ pipenv install
$ pipenv shell
```

Otherwise, if you don't have pipenv, you can use a vanilla Python virtual environment:

```
$ git clone https://git.sr.ht/~alanorth/csv-metadata-quality
$ cd csv-metadata-quality
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Usage
Run CSV Metadata Quality with the `--help` flag to see available options:

```
$ python -m csv_metadata_quality --help
```

To validate and clean a CSV file you must specify input and output files using the `-i` and `-o` options. For example, using the included test file:

```
$ python -m csv_metadata_quality -i data/test.csv -o /tmp/test.csv
```

You can enable "unsafe fixes" with the `--unsafe-fixes` option. Currently this will attempt to fix things like invalid multi-value separators (`|`). This is considered "unsafe" because it's theoretically possible for the `|` to be used legitimately in a metadata value, but in my experience it's always a typo where the user was attempting to use multiple metadata values, for example: `Kenya|Tanzania`.

## Todo

- Reporting / summary
- Real logging

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

The license allows you to use and modify the work for personal and commercial purposes, but if you distribute the work you must provide users with a means to access the source code for the version you are distributing. Read more about the [GPLv3 at TL;DR Legal](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)).
