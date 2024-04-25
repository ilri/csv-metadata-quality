<h1 align="center">DSpace CSV Metadata Quality Checker</h1>

<p align="center">
  <a href="https://ci.mjanja.ch/alanorth/csv-metadata-quality"><img alt="Build Status" src="https://ci.mjanja.ch/api/badges/alanorth/csv-metadata-quality/status.svg"></a>
  <a href="https://github.com/ilri/csv-metadata-quality/actions"><img alt="Build and Test" src="https://github.com/ilri/csv-metadata-quality/workflows/Build%20and%20Test/badge.svg"></a>
  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

A simple, but opinionated metadata quality checker and fixer designed to work with CSVs in the DSpace ecosystem (though it could theoretically work on any CSV that uses Dublin Core fields as columns). The implementation is essentially a pipeline of checks and fixes that begins with splitting multi-value fields on the standard DSpace "||" separator, trimming leading/trailing whitespace, and then proceeding to more specialized cases like ISSNs, ISBNs, languages, unnecessary Unicode, AGROVOC terms, etc.

Requires Python 3.9 or greater. CSV support comes from the [Pandas](https://pandas.pydata.org/) library.

If you use the DSpace CSV metadata quality checker please cite:

*Orth, A. 2019. DSpace CSV metadata quality checker. Nairobi, Kenya: ILRI. https://hdl.handle.net/10568/110997.*

## Functionality

- Validate dates, ISSNs, ISBNs, and multi-value separators ("||")
- Validate languages against ISO 639-1 (alpha2) and ISO 639-3 (alpha3)
- Experimental validation of titles and abstracts against item's Dublin Core language field
- Validate subjects against the AGROVOC REST API (see the `--agrovoc-fields` option)
- Validation of licenses against the list of [SPDX license identifiers](https://spdx.org/licenses)
- Fix leading, trailing, and excessive (ie, more than one) whitespace
- Fix invalid and unnecessary multi-value separators (`|`)
- Fix problematic newlines (line feeds) using `--unsafe-fixes`
- Perform [Unicode normalization](https://withblue.ink/2019/03/11/why-you-need-to-normalize-unicode-strings.html) on strings using `--unsafe-fixes`
- Remove unnecessary Unicode like [non-breaking spaces](https://en.wikipedia.org/wiki/Non-breaking_space), [replacement characters](https://en.wikipedia.org/wiki/Specials_(Unicode_block)#Replacement_character), etc
- Check for "suspicious" characters that indicate encoding or copy/paste issues, for example "foreˆt" should be "forêt"
- Check for "mojibake" characters (and attempt to fix with `--unsafe-fixes`)
- Check for countries with missing regions (and attempt to fix with `--unsafe-fixes`)
- Remove duplicate metadata values
- Check for duplicate items, using the title, type, and date issued as an indicator
- [Normalize DOIs](https://www.crossref.org/documentation/member-setup/constructing-your-dois/) to https://doi.org URI format

## Installation
The easiest way to install CSV Metadata Quality is with [poetry](https://python-poetry.org):

```
$ git clone https://github.com/ilri/csv-metadata-quality.git
$ cd csv-metadata-quality
$ poetry install
$ poetry shell
```

Otherwise, if you don't have poetry, you can use a vanilla Python virtual environment:

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

## Invalid Multi-Value Separators
While it is *theoretically* possible for a single `|` character to be used legitimately in a metadata value, in my experience it is always a typo. For example, if a user mistakenly writes `Kenya|Tanzania` when attempting to indicate two countries, the result will be one metadata value with the literal text `Kenya|Tanzania`. This utility will correct the invalid multi-value separator so that there are two metadata values, ie `Kenya||Tanzania`.

This will also remove unnecessary trailing multi-value separators, for example `Kenya||Tanzania||`.

## Unsafe Fixes
You can enable several "unsafe" fixes with the `--unsafe-fixes` option. Currently this will remove newlines, perform Unicode normalization, attempt to fix "mojibake" characters, and add missing UN M.49 regions.

### Newlines
This is considered "unsafe" because some systems give special importance to vertical space and render it properly. DSpace does not support rendering newlines in its XMLUI and has, at times, suffered from parsing errors that cause the import process to fail if an input file had newlines. The `--unsafe-fixes` option strips Unix line feeds (U+000A).

### Unicode Normalization
[Unicode](https://en.wikipedia.org/wiki/Unicode) is a standard for encoding text. As the standard aims to support most of the world's languages, characters can often be represented in different ways and still be valid Unicode. This leads to interesting problems that can be confusing unless you know what's going on behind the scenes. For example, the characters `é` and `é` *look* the same, but are not — technically they refer to different code points in the Unicode standard:

- `é` is the Unicode code point `U+00E9`
- `é` is the Unicode code points `U+0065` + `U+0301`

Read more about [Unicode normalization](https://withblue.ink/2019/03/11/why-you-need-to-normalize-unicode-strings.html).

### Encoding Issues aka "Mojibake"
[Mojibake](https://en.wikipedia.org/wiki/Mojibake) is a phenomenon that occurs when text is decoded using an unintended character encoding. This usually presents itself in the form of strange, garbled characters in the text. Enabling "unsafe" fixes will attempt to correct these, for example:

- CIAT PublicaÃ§ao → CIAT Publicaçao
- CIAT PublicaciÃ³n → CIAT Publicación

Pay special attention to the output of the script as well as the resulting file to make sure no new issues have been introduced. The ideal way to solve these issues is to avoid it in the first place. See [this guide about opening CSVs in UTF-8 format in Excel](https://www.itg.ias.edu/content/how-import-csv-file-uses-utf-8-character-encoding-0).

### Countries With Missing Regions
When an input file has both country and region columns we can check to see if the ISO 3166 country names have matching UN M.49 regions and add them when they are missing.

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
- Warn if two items use the same file in `filename` column
- Add tests for application invocation, ie `tests/test_app.py`?
- Validate ISSNs or journal titles against CrossRef API?
- Add configurable field validation, like specify a field name and a validation file?
  - Perhaps like --validate=field.name,filename
- Add some row-based item sanity checks and fixes:
  - Warn if item is Open Access, but missing a filename or URL
  - Warn if item is Open Access, but missing a license
  - Warn if item has an ISSN but no journal title
  - Update journal titles from ISSN
- Migrate from Pandas to Polars

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

The license allows you to use and modify the work for personal and commercial purposes, but if you distribute the work you must provide users with a means to access the source code for the version you are distributing. Read more about the [GPLv3 at TL;DR Legal](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)).
