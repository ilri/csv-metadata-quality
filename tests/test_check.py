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

    assert result == value


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

    assert result == value


def test_check_invalid_separators(capsys):
    """Test checking invalid multi-value separators."""

    value = "Alan|Orth"

    field_name = "dc.contributor.author"

    check.separators(value, field_name)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.RED}Invalid multi-value separator ({field_name}): {Fore.RESET}{value}\n"
    )


def test_check_unnecessary_separators(capsys):
    """Test checking unnecessary multi-value separators."""

    field = "Alan||Orth||"

    field_name = "dc.contributor.author"

    check.separators(field, field_name)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.RED}Unnecessary multi-value separator ({field_name}): {Fore.RESET}{field}\n"
    )


def test_check_valid_separators():
    """Test checking valid multi-value separators."""

    value = "Alan||Orth"

    field_name = "dc.contributor.author"

    result = check.separators(value, field_name)

    assert result == value


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

    assert result == value


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

    assert result == value


def test_check_valid_iso639_3_language():
    """Test valid ISO 639-3 (alpha 3) language."""

    value = "eng"

    result = check.language(value)

    assert result == value


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
    """Test invalid AGROVOC subject."""

    value = "FOREST"
    field_name = "dcterms.subject"

    check.agrovoc(value, field_name)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.RED}Invalid AGROVOC ({field_name}): {Fore.RESET}{value}\n"
    )


def test_check_valid_agrovoc():
    """Test valid AGROVOC subject."""

    value = "FORESTS"
    field_name = "dcterms.subject"

    result = check.agrovoc(value, field_name)

    assert result == value


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

    assert result == value


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

    assert result == language


def test_check_correct_iso_639_3_language():
    """Test correct ISO 639-3 language, as determined by comparing the item's language field with the actual language predicted in the item's title."""

    title = "A randomised vaccine field trial in Kenya demonstrates protection against wildebeest-associated malignant catarrhal fever in cattle"
    language = "eng"

    # Create a dictionary to mimic Pandas series
    row = {"dc.title": title, "dc.language.iso": language}
    series = pd.Series(row)

    result = experimental.correct_language(series)

    assert result == language


def test_check_valid_spdx_license_identifier():
    """Test valid SPDX license identifier."""

    license = "CC-BY-SA-4.0"

    result = check.spdx_license_identifier(license)

    assert result == license


def test_check_invalid_spdx_license_identifier(capsys):
    """Test invalid SPDX license identifier."""

    license = "CC-BY-SA"

    result = check.spdx_license_identifier(license)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"{Fore.YELLOW}Non-SPDX license identifier: {Fore.RESET}{license}\n"
    )
