# SPDX-License-Identifier: GPL-3.0-only

import pandas as pd

import csv_metadata_quality.fix as fix


def test_fix_leading_whitespace():
    """Test fixing leading whitespace."""

    value = " Alan"

    field_name = "dc.contributor.author"

    assert fix.whitespace(value, field_name) == "Alan"


def test_fix_trailing_whitespace():
    """Test fixing trailing whitespace."""

    value = "Alan "

    field_name = "dc.contributor.author"

    assert fix.whitespace(value, field_name) == "Alan"


def test_fix_excessive_whitespace():
    """Test fixing excessive whitespace."""

    value = "Alan  Orth"

    field_name = "dc.contributor.author"

    assert fix.whitespace(value, field_name) == "Alan Orth"


def test_fix_invalid_separators():
    """Test fixing invalid multi-value separators."""

    value = "Alan|Orth"

    field_name = "dc.contributor.author"

    assert fix.separators(value, field_name) == "Alan||Orth"


def test_fix_unnecessary_separators():
    """Test fixing unnecessary multi-value separators."""

    field = "Alan||Orth||"

    field_name = "dc.contributor.author"

    assert fix.separators(field, field_name) == "Alan||Orth"


def test_fix_unnecessary_unicode():
    """Test fixing unnecessary Unicode."""

    value = "Alan​ Orth"

    assert fix.unnecessary_unicode(value) == "Alan Orth"


def test_fix_duplicates():
    """Test fixing duplicate metadata values."""

    value = "Kenya||Kenya"

    field_name = "dc.contributor.author"

    assert fix.duplicates(value, field_name) == "Kenya"


def test_fix_newlines():
    """Test fixing newlines."""

    value = """Ken
ya"""
    field_name = "dcterms.subject"

    assert fix.newlines(value, field_name) == "Kenya"


def test_fix_comma_space():
    """Test adding space after comma."""

    value = "Orth,Alan S."

    field_name = "dc.contributor.author"

    assert fix.comma_space(value, field_name) == "Orth, Alan S."


def test_fix_normalized_unicode():
    """Test fixing a string that is already in its normalized (NFC) Unicode form."""

    # string using the normalized canonical form of é
    value = "Ouédraogo, Mathieu"

    field_name = "dc.contributor.author"

    assert fix.normalize_unicode(value, field_name) == "Ouédraogo, Mathieu"


def test_fix_decomposed_unicode():
    """Test fixing a string that contains Unicode string."""

    # string using the decomposed form of é
    value = "Ouédraogo, Mathieu"

    field_name = "dc.contributor.author"

    assert fix.normalize_unicode(value, field_name) == "Ouédraogo, Mathieu"


def test_fix_mojibake():
    """Test string with no mojibake."""

    field = "CIAT PublicaÃ§ao"
    field_name = "dcterms.isPartOf"

    assert fix.mojibake(field, field_name) == "CIAT Publicaçao"


def test_fix_country_not_matching_region():
    """Test an item with regions not matching its country list."""

    title = "Testing an item with no matching region."
    country = "Kenya"
    region = ""
    missing_region = "Eastern Africa"
    exclude = list()

    # Emulate a column in a transposed dataframe (which is just a series)
    d = {
        "dc.title": title,
        "cg.coverage.country": country,
        "cg.coverage.region": region,
    }
    series = pd.Series(data=d)

    result = fix.countries_match_regions(series, exclude)

    # Emulate the correct series we are expecting
    d_correct = {
        "dc.title": title,
        "cg.coverage.country": country,
        "cg.coverage.region": missing_region,
    }
    series_correct = pd.Series(data=d_correct)

    pd.testing.assert_series_equal(result, series_correct)
