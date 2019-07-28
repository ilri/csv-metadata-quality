# CSV Metadata Quality [![builds.sr.ht status](https://builds.sr.ht/~alanorth/csv-metadata-quality.svg)](https://builds.sr.ht/~alanorth/csv-metadata-quality?)
A simple but opinionated metadata quality checker and fixer designed to work with CSVs in the DSpace ecosystem. Supports multi-value fields using the standard DSpace value separator ("||").

Written and tested using Python 3.7.

## Checks
Supports checking the validity of the following metadata elements:

- ISSN
- ISBN
- Multi-value separators
- Dates

## Fixes
Supports fixing the following metadata issues:

- Leading, trailing, and excessive whitespace

## Todo

- Reporting / summary
- Real logging
- Fix invalid multi-value separators? Check if there are any valid cases of "|" in the database

## License
This work is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).

The license allows you to use and modify the work for personal and commercial purposes, but if you distribute the work you must provide users with a means to access the source code for the version you are distributing. Read more about the [GPLv3 at TL;DR Legal](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)).
