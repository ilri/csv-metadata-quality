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

    assert fix.newlines(value) == "Kenya"


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
