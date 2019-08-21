# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
### Changed
- Output of date checks to include column names (helps debugging in case there are multiple date fields)

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
