import csv_metadata_quality.fix as fix


def test_fix_leading_whitespace():
    '''Test fixing leading whitespace.'''

    value = ' Alan'

    assert fix.whitespace(value) == 'Alan'


def test_fix_trailing_whitespace():
    '''Test fixing trailing whitespace.'''

    value = 'Alan '

    assert fix.whitespace(value) == 'Alan'


def test_fix_excessive_whitespace():
    '''Test fixing excessive whitespace.'''

    value = 'Alan  Orth'

    assert fix.whitespace(value) == 'Alan Orth'


def test_fix_invalid_separators():
    '''Test fixing invalid multi-value separators.'''

    value = 'Alan|Orth'

    assert fix.separators(value) == 'Alan||Orth'


def test_fix_unnecessary_unicode():
    '''Test fixing unnecessary Unicode.'''

    value = 'Alan​ Orth'

    assert fix.unnecessary_unicode(value) == 'Alan Orth'
