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

        if match:
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

        return field


def suspicious_characters(field):
    """Warn about suspicious characters.

    Look for standalone characters that could indicate encoding or copy/paste
    errors for languages with accents. For example: foreˆt should be forêt.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # List of suspicious characters, for example:  ́ˆ~`
    suspicious_characters = ['\u00B4', '\u02C6', '\u007E', '\u0060']

    for character in suspicious_characters:
        character_set = set(character)

        if character_set.issubset(field):
            print(f'Suspicious character: {field}')

    return field


def language(field):
    """Check if a language is valid ISO 639-2 or ISO 639-3.

    Prints the value if it is invalid.
    """

    from iso639 import languages

    # Skip fields with missing values
    if pd.isna(field):
        return

    # need to handle "Other" values here...

    # Try to split multi-value field on "||" separator
    for value in field.split('||'):

        # After splitting, check if language value is 2 or 3 characters so we
        # can check it against ISO 639-2 or ISO 639-3 accordingly. In iso-639
        # library ISO 639-2 is "part1" and ISO 639-3 is "part3".
        if len(value) == 2:
            try:
                languages.get(part1=value)
            except KeyError:
                print(f'Invalid ISO 639-2 language: {value}')

                pass
        elif len(value) == 3:
            try:
                languages.get(part3=value)
            except KeyError:
                print(f'Invalid ISO 639-3 language: {value}')

                pass
        else:
            print(f'Invalid language: {value}')

    return field


def agrovoc(field):
    """Check subject terms against AGROVOC REST API.

    Logic copied from agrovoc-lookup.py.

    See: https://github.com/ilri/DSpace/blob/5_x-prod/agrovoc-lookup.py

    Prints a warning if the value is invalid.
    """

    from datetime import timedelta
    import re
    import requests
    import requests_cache

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    for value in field.split('||'):
        # match lines beginning with words, paying attention to subjects with
        # special characters like spaces, quotes, dashes, parentheses, etc:
        # SUBJECT
        # ANOTHER SUBJECT
        # XANTHOMONAS CAMPESTRIS PV. MANIHOTIS
        # WOMEN'S PARTICIPATION
        # COMMUNITY-BASED FOREST MANAGEMENT
        # INTERACCIÓN GENOTIPO AMBIENTE
        # COCOA (PLANT)
        pattern = re.compile(r'^[\w\-\.\'\(\)]+?[\w\s\-\.\'\(\)]+$')

        if pattern.match(value):
            request_url = f'http://agrovoc.uniroma2.it/agrovoc/rest/v1/agrovoc/search?query={value}'

            # enable transparent request cache with thirty days expiry
            expire_after = timedelta(days=30)
            requests_cache.install_cache('agrovoc-response-cache', expire_after=expire_after)

            request = requests.get(request_url)

            # prune old cache entries
            requests_cache.core.remove_expired_responses()

            if request.status_code == requests.codes.ok:
                data = request.json()

                # check if there is 1 result, ie an exact subject term match
                if len(data['results']) != 1:
                    print(f'Invalid AGROVOC subject: {value}')

    return field
