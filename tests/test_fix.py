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
