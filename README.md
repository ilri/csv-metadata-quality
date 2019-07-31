# CSV Metadata Quality [![Build Status](https://travis-ci.org/alanorth/csv-metadata-quality.svg?branch=master)](https://travis-ci.org/alanorth/csv-metadata-quality) [![builds.sr.ht status](https://builds.sr.ht/~alanorth/csv-metadata-quality.svg)](https://builds.sr.ht/~alanorth/csv-metadata-quality?)
A simple, but opinionated metadata quality checker and fixer designed to work with CSVs in the DSpace ecosystem. The implementation is essentially a pipeline of checks and fixes that begins with splitting multi-value fields on the standard DSpace "||" separator, trimming leading/trailing whitespace, and then proceeding to more specialized cases like ISSNs, ISBNs, languages, etc.

Requires Python 3.6 or greater. CSV and Excel support comes from the [Pandas](https://pandas.pydata.org/) library, though your mileage may vary with Excel because this is much less tested.

## Functionality

- Validate dates, ISSNs, ISBNs, and multi-value separators ("||")
- Validate languages against ISO 639-2 and ISO 639-3
- Validate subjects against the AGROVOC REST API
- Fix leading, trailing, and excessive (ie, more than one) whitespace
- Fix invalid multi-value separators (`|`) using `--unsafe-fixes`
- Fix problematic newlines (line feeds) using `--unsafe-fixes`
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

## Unsafe Fixes
You can enable several "unsafe" fixes with the `--unsafe-fixes` option. Currently this will attempt to fix invalid multi-value separators and remove newlines.

### Invalid Multi-Value Separators
This is considered "unsafe" because it is *theoretically* possible for a single `|` character to be used legitimately in a metadata value, though in my experience it is always a typo. For example, if a user mistakenly writes `Kenya|Tanzania` when attempting to indicate two countries, the result will be one metadata value with the literal text `Kenya|Tanzania`. The `--unsafe-fixes` option will correct the invalid multi-value separator so that there are two metadata values, ie `Kenya||Tanzania`.

### Newlines
This is considered "unsafe" because some systems give special importance to vertical space and render it properly. DSpace does not support rendering newlines in its XMLUI and has, at times, suffered from parsing errors that cause the import process to fail if an input file had newlines. The `--unsafe-fixes` option strips Unix line feeds (U+000A).

## Todo

- Reporting / summary
- Real logging

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

The license allows you to use and modify the work for personal and commercial purposes, but if you distribute the work you must provide users with a means to access the source code for the version you are distributing. Read more about the [GPLv3 at TL;DR Legal](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)).
