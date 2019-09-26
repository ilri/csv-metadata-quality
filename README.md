# CSV Metadata Quality [![Build Status](https://travis-ci.org/ilri/csv-metadata-quality.svg?branch=master)](https://travis-ci.org/ilri/csv-metadata-quality) [![builds.sr.ht status](https://builds.sr.ht/~alanorth/csv-metadata-quality.svg)](https://builds.sr.ht/~alanorth/csv-metadata-quality?)
A simple, but opinionated metadata quality checker and fixer designed to work with CSVs in the DSpace ecosystem. The implementation is essentially a pipeline of checks and fixes that begins with splitting multi-value fields on the standard DSpace "||" separator, trimming leading/trailing whitespace, and then proceeding to more specialized cases like ISSNs, ISBNs, languages, etc.

Requires Python 3.6 or greater. CSV and Excel support comes from the [Pandas](https://pandas.pydata.org/) library, though your mileage may vary with Excel because this is much less tested.

## Functionality

- Validate dates, ISSNs, ISBNs, and multi-value separators ("||")
- Validate languages against ISO 639-1 (alpha2) and ISO 639-3 (alpha3)
- Experimental validation of titles and abstracts against item's Dublin Core language field
- Validate subjects against the AGROVOC REST API (see the `--agrovoc-fields` option)
- Fix leading, trailing, and excessive (ie, more than one) whitespace
- Fix invalid multi-value separators (`|`) using `--unsafe-fixes`
- Fix problematic newlines (line feeds) using `--unsafe-fixes`
- Remove unnecessary Unicode like [non-breaking spaces](https://en.wikipedia.org/wiki/Non-breaking_space), [replacement characters](https://en.wikipedia.org/wiki/Specials_(Unicode_block)#Replacement_character), etc
- Check for "suspicious" characters that indicate encoding or copy/paste issues, for example "foreˆt" should be "forêt"
- Remove duplicate metadata values

## Installation
The easiest way to install CSV Metadata Quality is with [pipenv](https://github.com/pypa/pipenv):

```
$ git clone https://github.com/ilri/csv-metadata-quality.git
$ cd csv-metadata-quality
$ pipenv install
$ pipenv shell
```

Otherwise, if you don't have pipenv, you can use a vanilla Python virtual environment:

```
$ git clone https://github.com/ilri/csv-metadata-quality.git
$ cd csv-metadata-quality
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Usage
Run CSV Metadata Quality with the `--help` flag to see available options:

```
$ csv-metadata-quality --help
```

To validate and clean a CSV file you must specify input and output files using the `-i` and `-o` options. For example, using the included test file:

```
$ csv-metadata-quality -i data/test.csv -o /tmp/test.csv
```

## Unsafe Fixes
You can enable several "unsafe" fixes with the `--unsafe-fixes` option. Currently this will attempt to fix invalid multi-value separators and remove newlines.

### Invalid Multi-Value Separators
This is considered "unsafe" because it is *theoretically* possible for a single `|` character to be used legitimately in a metadata value, though in my experience it is always a typo. For example, if a user mistakenly writes `Kenya|Tanzania` when attempting to indicate two countries, the result will be one metadata value with the literal text `Kenya|Tanzania`. The `--unsafe-fixes` option will correct the invalid multi-value separator so that there are two metadata values, ie `Kenya||Tanzania`.

### Newlines
This is considered "unsafe" because some systems give special importance to vertical space and render it properly. DSpace does not support rendering newlines in its XMLUI and has, at times, suffered from parsing errors that cause the import process to fail if an input file had newlines. The `--unsafe-fixes` option strips Unix line feeds (U+000A).

## AGROVOC Validation
You can enable validation of metadata values in certain fields against the AGROVOC REST API with the `--agrovoc-fields` option. For example, in addition to agricultural subjects, many countries and regions are also present AGROVOC. Enable this validation by specifying a comma-separated list of fields:

```
$ csv-metadata-quality -i data/test.csv -o /tmp/test.csv -u --agrovoc-fields dc.subject,cg.coverage.country
...
Invalid AGROVOC (dc.subject): FOREST
Invalid AGROVOC (cg.coverage.country): KENYAA
```

*Note: Requests to the AGROVOC REST API are cached using [requests_cache](https://pypi.org/project/requests-cache/) to speed up subsequent runs with the same data and to be kind to the system's administrators.*

## Experimental Checks
You can enable experimental support for validating whether the value of an item's `dc.language.iso` or `dcterms.language` field matches the actual language used in its title, abstract, and citation.

```
$ csv-metadata-quality -i data/test.csv -o /tmp/test.csv -e
...
Possibly incorrect language es (detected en): Incorrect ISO 639-1 language
Possibly incorrect language spa (detected eng): Incorrect ISO 639-3 language
```

This currently uses the [Python langid](https://github.com/saffsd/langid.py) library. In the future I would like to move to the fastText library, but there is currently an [issue with their Python bindings](https://github.com/facebookresearch/fastText/issues/909) that makes this unfeasible.

## Todo

- Reporting / summary
- Better logging, for example with INFO, WARN, and ERR levels
- Verbose, debug, or quiet options
- Warn if an author is shorter than 3 characters?
- Validate dc.rights field against SPDX? Perhaps with an option like `-m spdx` to enable the spdx module?
- Validate DOIs? Normalize to https://doi.org format? Or use just the DOI part: 10.1016/j.worlddev.2010.06.006
- Warn if two items use the same file in `filename` column
- Add an option to drop invalid AGROVOC subjects?
- Add check for author names with incorrect spacing after commas, ie "Orth,Alan S."
- Add tests for application invocation, ie `tests/test_app.py`?

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

The license allows you to use and modify the work for personal and commercial purposes, but if you distribute the work you must provide users with a means to access the source code for the version you are distributing. Read more about the [GPLv3 at TL;DR Legal](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)).
