import csv_metadata_quality.fix as fix


def test_fix_leading_whitespace():
    """Test fixing leading whitespace."""

    value = " Alan"

    assert fix.whitespace(value) == "Alan"


def test_fix_trailing_whitespace():
    """Test fixing trailing whitespace."""

    value = "Alan "

    assert fix.whitespace(value) == "Alan"


def test_fix_excessive_whitespace():
    """Test fixing excessive whitespace."""

    value = "Alan  Orth"

    assert fix.whitespace(value) == "Alan Orth"


def test_fix_invalid_separators():
    """Test fixing invalid multi-value separators."""

    value = "Alan|Orth"

    assert fix.separators(value) == "Alan||Orth"


def test_fix_unnecessary_unicode():
    """Test fixing unnecessary Unicode."""

    value = "Alan​ Orth"

    assert fix.unnecessary_unicode(value) == "Alan Orth"


def test_fix_duplicates():
    """Test fixing duplicate metadata values."""

    value = "Kenya||Kenya"

    assert fix.duplicates(value) == "Kenya"


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
