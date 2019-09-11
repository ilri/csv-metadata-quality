import csv_metadata_quality.check as check


def test_check_invalid_issn(capsys):
    '''Test checking invalid ISSN.'''

    value = '2321-2302'

    check.issn(value)

    captured = capsys.readouterr()
    assert captured.out == f'Invalid ISSN: {value}\n'


def test_check_valid_issn():
    '''Test checking valid ISSN.'''

    value = '0024-9319'

    result = check.issn(value)

    assert result == value


def test_check_invalid_isbn(capsys):
    '''Test checking invalid ISBN.'''

    value = '99921-58-10-6'

    check.isbn(value)

    captured = capsys.readouterr()
    assert captured.out == f'Invalid ISBN: {value}\n'


def test_check_valid_isbn():
    '''Test checking valid ISBN.'''

    value = '99921-58-10-7'

    result = check.isbn(value)

    assert result == value


def test_check_invalid_separators(capsys):
    '''Test checking invalid multi-value separators.'''

    value = 'Alan|Orth'

    check.separators(value)

    captured = capsys.readouterr()
    assert captured.out == f'Invalid multi-value separator: {value}\n'


def test_check_valid_separators():
    '''Test checking valid multi-value separators.'''

    value = 'Alan||Orth'

    result = check.separators(value)

    assert result == value


def test_check_missing_date(capsys):
    '''Test checking missing date.'''

    value = None

    field_name = 'dc.date.issued'

    check.date(value, field_name)

    captured = capsys.readouterr()
    assert captured.out == f'Missing date ({field_name}).\n'


def test_check_multiple_dates(capsys):
    '''Test checking multiple dates.'''

    value = '1990||1991'

    field_name = 'dc.date.issued'

    check.date(value, field_name)

    captured = capsys.readouterr()
    assert captured.out == f'Multiple dates not allowed ({field_name}): {value}\n'


def test_check_invalid_date(capsys):
    '''Test checking invalid ISO8601 date.'''

    value = '1990-0'

    field_name = 'dc.date.issued'

    check.date(value, field_name)

    captured = capsys.readouterr()
    assert captured.out == f'Invalid date ({field_name}): {value}\n'


def test_check_valid_date():
    '''Test checking valid ISO8601 date.'''

    value = '1990'

    field_name = 'dc.date.issued'

    result = check.date(value, field_name)

    assert result == value


def test_check_suspicious_characters(capsys):
    '''Test checking for suspicious characters.'''

    value = 'foreˆt'

    field_name = 'dc.contributor.author'

    check.suspicious_characters(value, field_name)

    captured = capsys.readouterr()
    assert captured.out == f'Suspicious character ({field_name}): ˆt\n'


def test_check_valid_iso639_1_language():
    '''Test valid ISO 639-1 language.'''

    value = 'ja'

    result = check.language(value)

    assert result == value


def test_check_valid_iso639_2_language():
    '''Test invalid ISO 639-2 language.'''

    value = 'eng'

    result = check.language(value)

    assert result == value


def test_check_invalid_iso639_1_language(capsys):
    '''Test invalid ISO 639-1 language.'''

    value = 'jp'

    check.language(value)

    captured = capsys.readouterr()
    assert captured.out == f'Invalid ISO 639-1 language: {value}\n'


def test_check_invalid_iso639_2_language(capsys):
    '''Test invalid ISO 639-2 language.'''

    value = 'chi'

    check.language(value)

    captured = capsys.readouterr()
    assert captured.out == f'Invalid ISO 639-2 language: {value}\n'


def test_check_invalid_language(capsys):
    '''Test invalid language.'''

    value = 'Span'

    check.language(value)

    captured = capsys.readouterr()
    assert captured.out == f'Invalid language: {value}\n'


def test_check_invalid_agrovoc(capsys):
    '''Test invalid AGROVOC subject.'''

    value = 'FOREST'
    field_name = 'dc.subject'

    check.agrovoc(value, field_name)

    captured = capsys.readouterr()
    assert captured.out == f'Invalid AGROVOC ({field_name}): {value}\n'


def test_check_valid_agrovoc():
    '''Test valid AGROVOC subject.'''

    value = 'FORESTS'
    field_name = 'dc.subject'

    result = check.agrovoc(value, field_name)

    assert result == value


def test_check_uncommon_filename_extension(capsys):
    '''Test uncommon filename extension.'''

    value = 'file.pdf.lck'

    check.filename_extension(value)

    captured = capsys.readouterr()
    assert captured.out == f'Filename with uncommon extension: {value}\n'


def test_check_common_filename_extension():
    '''Test common filename extension.'''

    value = 'file.pdf'

    result = check.filename_extension(value)

    assert result == value
