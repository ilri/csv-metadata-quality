# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
### Changed
- Fixing invalid multi-value separators like `|` and `|||` is no longer class-
ified as "unsafe" as I have yet to see a case where this was intentional
- Not user visible, but now checks only print a warning to the screen instead
of returning a value and re-writing the DataFrame, which should be faster and
use less memory

### Added
- Configurable directory for AGROVOC requests cache (to allow running the web
version from Google App Engine where we can only write to /tmp)
- Ability to check for duplicate items in the data set (uses a combination of
the title, type, and date issued to determine uniqueness)

### Removed
- Checks for invalid and unnecessary multi-value separators because now I fix
them whenever I see them, so there is no need to have checks for them

### Updated
- Run `poetry update` to update project dependencies

## [0.4.6] - 2021-03-11
### Added
- Validation of dcterms.license field against SPDX license identifiers 

### Changed
- Use DCTERMS fields where possible in `data/test.csv`

### Updated
- Run `poetry update` to update project dependencies

### Fixed
- Output for all fixes should be green, because it is good

## [0.4.5] - 2021-03-04
### Added
- Check dates in dcterms.issued field as well, not just fields that have the
word "date" in them

### Updated
- Run `poetry update` to update project dependencies

## [0.4.4] - 2021-02-21
### Added
- Accept dates formatted in ISO 8601 extended with combined date and time, for
example: 2020-08-31T11:04:56Z
- Colorized output: red for errors, yellow for warnings and information, green
for changes

### Updated
- Run `poetry update` to update project dependencies

## [0.4.3] - 2021-01-26
### Changed
- Reformat with black
- Requires Python 3.7+ for pandas 1.2.0

### Updated
- Run `poetry update`
- Expand check/fix for multi-value separators to include metadata with invalid
separators at the end, for example "Kenya||Tanzania||"

## [0.4.2] - 2020-07-06
### Changed
- Add field name to the output for more fixes and checks to help identify where
the error is
- Minor optimizations to AGROVOC subject lookup
- Use Poetry instead of Pipenv

### Updated
- Update python dependencies to latest versions

## [0.4.1] - 2020-01-15
### Changed
- Reduce minimum Python version to 3.6 by working around the `is_normalized()`
that only works in Python >= 3.8

## [0.4.0] - 2020-01-15
### Added
- Unicode normalization (enable with `--unsafe-fixes`, see README.md)

### Updated
- Update python dependencies to latest versions, including numpy 1.18.1, pandas
1.0.0rc0, flake8 3.7.9, pytest 5.3.2, and black 19.10b0
- Regenerate requirements.txt and requirements-dev.txt

### Changed
- Use Python 3.8.0 for pipenv
- Use Ubuntu 18.04 "Bionic" for TravisCI builds
- Test Python 3.8 in TravisCI builds

## [0.3.1] - 2019-10-01
## Changed
- Replace non-breaking spaces (U+00A0) with space instead of removing them
- Harmonize language of script output when fixing various issues

## [0.3.0] - 2019-09-26
### Updated
- Update python dependencies to latest versions, including numpy 1.17.2, pandas
0.25.1, pytest 5.1.3, and requests-cache 0.5.2

### Added
- csvkit to dev requirements (csvcut etc are useful during development)
- Experimental language validation using the Python `langid` library (enable with `-e`, see README.md)

### Changed
- Re-formatted code with black and isort

## [0.2.2] - 2019-08-27
### Changed
- Output of date checks to include column names (helps debugging in case there are multiple date fields)

### Added
- Ability to exclude certain fields using `--exclude-fields`
- Fix for missing space after a comma, ie "Orth,Alan S."

### Improved
- AGROVOC lookup code

## [0.2.1] - 2019-08-11
### Added
- Check for uncommon filename extensions
- Replacement of unneccessary Unicode characters like soft hyphens (U+00AD)

## [0.2.0] - 2019-08-09
### Added
- Handle Ctrl-C interrupt gracefully
- Make output in suspicious character check more user friendly
- Add pytest-clarity to dev packages for more user friendly pytest output

## [0.1.0] - 2019-08-01
### Changed
- AGROVOC validation is now turned off by default

### Added
- Ability to enable AGROVOC validation on a field-by-field basis using the `--agrovoc-fields` option
- Option to print the version (`--version` or `-V`)
