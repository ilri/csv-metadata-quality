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

    check.date(value)

    captured = capsys.readouterr()
    assert captured.out == f'Missing date.\n'


def test_check_multiple_dates(capsys):
    '''Test checking multiple dates.'''

    value = '1990||1991'

    check.date(value)

    captured = capsys.readouterr()
    assert captured.out == f'Multiple dates not allowed: {value}\n'


def test_check_invalid_date(capsys):
    '''Test checking invalid ISO8601 date.'''

    value = '1990-0'

    check.date(value)

    captured = capsys.readouterr()
    assert captured.out == f'Invalid date: {value}\n'


def test_check_valid_date():
    '''Test checking valid ISO8601 date.'''

    value = '1990'

    result = check.date(value)

    assert result == value
