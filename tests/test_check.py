# SPDX-License-Identifier: GPL-3.0-only

import pandas as pd
from colorama import Fore

import csv_metadata_quality.check as check
import csv_metadata_quality.experimental as experimental


def test_check_invalid_issn(capsys):
    """Test checking invalid ISSN."""

    value = "2321-2302"

    check.issn(value)

    captured = capsys.readouterr()
    assert captured.out == f"{Fore.RED}Invalid ISSN: {Fore.RESET}{value}\n"


def test_check_valid_issn():
    """Test checking valid ISSN."""

    value = "0024-9319"

    result = check.issn(value)

    assert result == None


def test_check_invalid_isbn(capsys):
    """Test checking invalid ISBN."""

    value = "99921-58-10-6"

    check.isbn(value)

    captured = capsys.readouterr()
    assert captured.out == f"{Fore.RED}Invalid ISBN: {Fore.RESET}{value}\n"


def test_check_valid_isbn():
    """Test checking valid ISBN."""

    value = "99921-58-10-7"

    result = check.isbn(value)

    assert result == None


def test_check_missing_date(capsys):
    """Test checking missing date."""

    value = None

    field_name = "dc.date.issued"

    check.date(value, field_name)

    captured = capsys.readouterr()
    assert captured.out == f"{Fore.RED}Missing date ({field_name}).{Fore.RESET}\n"


def test_check_multiple_dates(capsys):
    """Test checking multiple dates."""

    value = "1990||1991"

    field_name = "dc.date.issued"

    check.date(value, field_name)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.RED}Multiple dates not allowed ({field_name}): {Fore.RESET}{value}\n"
    )


def test_check_invalid_date(capsys):
    """Test checking invalid ISO8601 date."""

    value = "1990-0"

    field_name = "dc.date.issued"

    check.date(value, field_name)

    captured = capsys.readouterr()
    assert (
        captured.out == f"{Fore.RED}Invalid date ({field_name}): {Fore.RESET}{value}\n"
    )


def test_check_valid_date():
    """Test checking valid ISO8601 date."""

    value = "1990"

    field_name = "dc.date.issued"

    result = check.date(value, field_name)

    assert result == None


def test_check_suspicious_characters(capsys):
    """Test checking for suspicious characters."""

    value = "foreˆt"

    field_name = "dc.contributor.author"

    check.suspicious_characters(value, field_name)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Suspicious character ({field_name}): {Fore.RESET}ˆt\n"
    )


def test_check_valid_iso639_1_language():
    """Test valid ISO 639-1 (alpha 2) language."""

    value = "ja"

    result = check.language(value)

    assert result == None


def test_check_valid_iso639_3_language():
    """Test valid ISO 639-3 (alpha 3) language."""

    value = "eng"

    result = check.language(value)

    assert result == None


def test_check_invalid_iso639_1_language(capsys):
    """Test invalid ISO 639-1 (alpha 2) language."""

    value = "jp"

    check.language(value)

    captured = capsys.readouterr()
    assert (
        captured.out == f"{Fore.RED}Invalid ISO 639-1 language: {Fore.RESET}{value}\n"
    )


def test_check_invalid_iso639_3_language(capsys):
    """Test invalid ISO 639-3 (alpha 3) language."""

    value = "chi"

    check.language(value)

    captured = capsys.readouterr()
    assert (
        captured.out == f"{Fore.RED}Invalid ISO 639-3 language: {Fore.RESET}{value}\n"
    )


def test_check_invalid_language(capsys):
    """Test invalid language."""

    value = "Span"

    check.language(value)

    captured = capsys.readouterr()
    assert captured.out == f"{Fore.RED}Invalid language: {Fore.RESET}{value}\n"


def test_check_invalid_agrovoc(capsys):
    """Test invalid AGROVOC subject. Invalid values *will not* be dropped."""

    valid_agrovoc = "LIVESTOCK"
    invalid_agrovoc = "FOREST"
    value = f"{valid_agrovoc}||{invalid_agrovoc}"
    field_name = "dcterms.subject"
    drop = False

    new_value = check.agrovoc(value, field_name, drop)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.RED}Invalid AGROVOC ({field_name}): {Fore.RESET}{invalid_agrovoc}\n"
    )
    assert new_value == value


def test_check_invalid_agrovoc_dropped(capsys):
    """Test invalid AGROVOC subjects. Invalid values *will* be dropped."""

    valid_agrovoc = "LIVESTOCK"
    invalid_agrovoc = "FOREST"
    value = f"{valid_agrovoc}||{invalid_agrovoc}"
    field_name = "dcterms.subject"
    drop = True

    new_value = check.agrovoc(value, field_name, drop)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.GREEN}Dropping invalid AGROVOC ({field_name}): {Fore.RESET}{invalid_agrovoc}\n"
    )
    assert new_value == valid_agrovoc


def test_check_valid_agrovoc():
    """Test valid AGROVOC subject."""

    value = "FORESTS"
    field_name = "dcterms.subject"
    drop = False

    result = check.agrovoc(value, field_name, drop)

    assert result == "FORESTS"


def test_check_uncommon_filename_extension(capsys):
    """Test uncommon filename extension."""

    value = "file.pdf.lck"

    check.filename_extension(value)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Filename with uncommon extension: {Fore.RESET}{value}\n"
    )


def test_check_common_filename_extension():
    """Test common filename extension."""

    value = "file.pdf"

    result = check.filename_extension(value)

    assert result == None


def test_check_incorrect_iso_639_1_language(capsys):
    """Test incorrect ISO 639-1 language, as determined by comparing the item's language field with the actual language predicted in the item's title."""

    title = "A randomised vaccine field trial in Kenya demonstrates protection against wildebeest-associated malignant catarrhal fever in cattle"
    language = "es"

    # Create a dictionary to mimic Pandas series
    row = {"dc.title": title, "dc.language.iso": language}
    series = pd.Series(row)

    experimental.correct_language(series)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Possibly incorrect language {language} (detected en): {Fore.RESET}{title}\n"
    )


def test_check_incorrect_iso_639_3_language(capsys):
    """Test incorrect ISO 639-3 language, as determined by comparing the item's language field with the actual language predicted in the item's title."""

    title = "A randomised vaccine field trial in Kenya demonstrates protection against wildebeest-associated malignant catarrhal fever in cattle"
    language = "spa"

    # Create a dictionary to mimic Pandas series
    row = {"dc.title": title, "dc.language.iso": language}
    series = pd.Series(row)

    experimental.correct_language(series)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Possibly incorrect language {language} (detected eng): {Fore.RESET}{title}\n"
    )


def test_check_correct_iso_639_1_language():
    """Test correct ISO 639-1 language, as determined by comparing the item's language field with the actual language predicted in the item's title."""

    title = "A randomised vaccine field trial in Kenya demonstrates protection against wildebeest-associated malignant catarrhal fever in cattle"
    language = "en"

    # Create a dictionary to mimic Pandas series
    row = {"dc.title": title, "dc.language.iso": language}
    series = pd.Series(row)

    result = experimental.correct_language(series)

    assert result == None


def test_check_correct_iso_639_3_language():
    """Test correct ISO 639-3 language, as determined by comparing the item's language field with the actual language predicted in the item's title."""

    title = "A randomised vaccine field trial in Kenya demonstrates protection against wildebeest-associated malignant catarrhal fever in cattle"
    language = "eng"

    # Create a dictionary to mimic Pandas series
    row = {"dc.title": title, "dc.language.iso": language}
    series = pd.Series(row)

    result = experimental.correct_language(series)

    assert result == None


def test_check_valid_spdx_license_identifier():
    """Test valid SPDX license identifier."""

    license = "CC-BY-SA-4.0"

    result = check.spdx_license_identifier(license)

    assert result == None


def test_check_invalid_spdx_license_identifier(capsys):
    """Test invalid SPDX license identifier."""

    license = "CC-BY-SA"

    result = check.spdx_license_identifier(license)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Non-SPDX license identifier: {Fore.RESET}{license}\n"
    )


def test_check_duplicate_item(capsys):
    """Test item with duplicate title, type, and date."""

    item_title = "Title"
    item_type = "Report"
    item_date = "2021-03-17"

    d = {
        "dc.title": [item_title, item_title],
        "dcterms.type": [item_type, item_type],
        "dcterms.issued": [item_date, item_date],
    }
    df = pd.DataFrame(data=d)

    result = check.duplicate_items(df)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Possible duplicate (dc.title): {Fore.RESET}{item_title}\n"
    )


def test_check_no_mojibake():
    """Test string with no mojibake."""

    field = "CIAT Publicaçao"
    field_name = "dcterms.isPartOf"

    result = check.mojibake(field, field_name)

    assert result == None


def test_check_mojibake(capsys):
    """Test string with mojibake."""

    field = "CIAT PublicaÃ§ao"
    field_name = "dcterms.isPartOf"

    result = check.mojibake(field, field_name)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Possible encoding issue ({field_name}): {Fore.RESET}{field}\n"
    )


def test_check_doi_field():
    """Test an item with a DOI field."""

    doi = "https://doi.org/10.1186/1743-422X-9-218"
    citation = "Orth, A. 2021. Testing all the things. doi: 10.1186/1743-422X-9-218"

    # Emulate a column in a transposed dataframe (which is just a series), with
    # the citation and a DOI field.
    d = {"cg.identifier.doi": doi, "dcterms.bibliographicCitation": citation}
    series = pd.Series(data=d)

    result = check.citation_doi(series)

    assert result == None


def test_check_doi_only_in_citation(capsys):
    """Test an item with a DOI in its citation, but no DOI field."""

    citation = "Orth, A. 2021. Testing all the things. doi: 10.1186/1743-422X-9-218"

    # Emulate a column in a transposed dataframe (which is just a series), with
    # an empty DOI field and a citation containing a DOI.
    d = {"cg.identifier.doi": None, "dcterms.bibliographicCitation": citation}
    series = pd.Series(data=d)

    check.citation_doi(series)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}DOI in citation, but missing a DOI field: {Fore.RESET}{citation}\n"
    )


def test_title_in_citation():
    """Test an item with its title in the citation."""

    title = "Testing all the things"
    citation = "Orth, A. 2021. Testing all the things."

    # Emulate a column in a transposed dataframe (which is just a series), with
    # the title and citation.
    d = {"dc.title": title, "dcterms.bibliographicCitation": citation}
    series = pd.Series(data=d)

    result = check.title_in_citation(series)

    assert result == None


def test_title_not_in_citation(capsys):
    """Test an item with its title missing from the citation."""

    title = "Testing all the things"
    citation = "Orth, A. 2021. Testing all teh things."

    # Emulate a column in a transposed dataframe (which is just a series), with
    # the title and citation.
    d = {"dc.title": title, "dcterms.bibliographicCitation": citation}
    series = pd.Series(data=d)

    check.title_in_citation(series)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Title is not present in citation: {Fore.RESET}{title}\n"
    )


def test_country_matches_region():
    """Test an item with regions matching its country list."""

    country = "Kenya"
    region = "Eastern Africa"

    # Emulate a column in a transposed dataframe (which is just a series)
    d = {"cg.coverage.country": country, "cg.coverage.region": region}
    series = pd.Series(data=d)

    result = check.countries_match_regions(series)

    assert result == None


def test_country_not_matching_region(capsys):
    """Test an item with regions not matching its country list."""

    title = "Testing an item with no matching region."
    country = "Kenya"
    region = ""
    missing_region = "Eastern Africa"

    # Emulate a column in a transposed dataframe (which is just a series)
    d = {
        "dc.title": title,
        "cg.coverage.country": country,
        "cg.coverage.region": region,
    }
    series = pd.Series(data=d)

    check.countries_match_regions(series)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Missing region ({missing_region}): {Fore.RESET}{title}\n"
    )
