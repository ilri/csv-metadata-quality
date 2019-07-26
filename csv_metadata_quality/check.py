import pandas as pd

def issn(field):
    """Check if an ISSN is valid.

    Prints the ISSN if invalid.

    stdnum's is_valid() function never raises an exception.

    See: https://arthurdejong.org/python-stdnum/doc/1.11/index.html#stdnum.module.is_valid
    """

    from stdnum import issn

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    for value in field.split('||'):

        if not issn.is_valid(value):
            print(f'Invalid ISSN: {value}')


def isbn(field):
    """Check if an ISBN is valid.

    Prints the ISBN if invalid.

    stdnum's is_valid() function never raises an exception.

    See: https://arthurdejong.org/python-stdnum/doc/1.11/index.html#stdnum.module.is_valid
    """

    from stdnum import isbn

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    for value in field.split('||'):

        if not isbn.is_valid(value):
            print(f'Invalid ISBN: {value}')


def separators(field):
    """Check for invalid multi-value separators (ie "|" or "|||").

    Prints the field with the invalid multi-value separator.
    """

    import re

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    for value in field.split('||'):

        # After splitting, see if there are any remaining "|" characters
        match = re.findall(r'^.*?\|.*$', value)

        if len(match) > 0:
            print(f'Invalid multi-value separator: {field}')