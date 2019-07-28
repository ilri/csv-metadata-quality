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

    return field


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

    return field


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

    return field


def date(field):
    """Check if a date is valid.

    In DSpace the issue date is usually 1990, 1990-01, or 1990-01-01, but it
    could technically even include time as long as it is ISO8601.

    Also checks for other invalid cases like missing and multiple dates.

    Prints the date if invalid.
    """
    from datetime import datetime

    if pd.isna(field):
        print(f'Missing date.')

        return

    # Try to split multi-value field on "||" separator
    multiple_dates = field.split('||')

    # We don't allow multi-value date fields
    if len(multiple_dates) > 1:
        print(f'Multiple dates not allowed: {field}')

        return field

    try:
        # Check if date is valid YYYY format
        datetime.strptime(field, '%Y')

        return field
    except ValueError:
        pass

    try:
        # Check if date is valid YYYY-MM format
        datetime.strptime(field, '%Y-%m')

        return field
    except ValueError:
        pass

    try:
        # Check if date is valid YYYY-MM-DD format
        datetime.strptime(field, '%Y-%m-%d')

        return field
    except ValueError:
        print(f'Invalid date: {field}')
