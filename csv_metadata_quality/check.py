import os
import re
from datetime import datetime, timedelta

import pandas as pd
import requests
import requests_cache
import spdx_license_list
from colorama import Fore
from pycountry import languages
from stdnum import isbn as stdnum_isbn
from stdnum import issn as stdnum_issn


def issn(field):
    """Check if an ISSN is valid.

    Prints the ISSN if invalid.

    stdnum's is_valid() function never raises an exception.

    See: https://arthurdejong.org/python-stdnum/doc/1.11/index.html#stdnum.module.is_valid
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    for value in field.split("||"):

        if not stdnum_issn.is_valid(value):
            print(f"{Fore.RED}Invalid ISSN: {Fore.RESET}{value}")

    return field


def isbn(field):
    """Check if an ISBN is valid.

    Prints the ISBN if invalid.

    stdnum's is_valid() function never raises an exception.

    See: https://arthurdejong.org/python-stdnum/doc/1.11/index.html#stdnum.module.is_valid
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    for value in field.split("||"):

        if not stdnum_isbn.is_valid(value):
            print(f"{Fore.RED}Invalid ISBN: {Fore.RESET}{value}")

    return field


def date(field, field_name):
    """Check if a date is valid.

    In DSpace the issue date is usually 1990, 1990-01, or 1990-01-01, but it
    could technically even include time as long as it is ISO8601.

    Also checks for other invalid cases like missing and multiple dates.

    Prints the date if invalid.
    """

    if pd.isna(field):
        print(f"{Fore.RED}Missing date ({field_name}).{Fore.RESET}")

        return

    # Try to split multi-value field on "||" separator
    multiple_dates = field.split("||")

    # We don't allow multi-value date fields
    if len(multiple_dates) > 1:
        print(
            f"{Fore.RED}Multiple dates not allowed ({field_name}): {Fore.RESET}{field}"
        )

        return field

    try:
        # Check if date is valid YYYY format
        datetime.strptime(field, "%Y")

        return field
    except ValueError:
        pass

    try:
        # Check if date is valid YYYY-MM format
        datetime.strptime(field, "%Y-%m")

        return field
    except ValueError:
        pass

    try:
        # Check if date is valid YYYY-MM-DD format
        datetime.strptime(field, "%Y-%m-%d")

        return field
    except ValueError:
        pass

    try:
        # Check if date is valid YYYY-MM-DDTHH:MM:SSZ format
        datetime.strptime(field, "%Y-%m-%dT%H:%M:%SZ")

        return field
    except ValueError:
        print(f"{Fore.RED}Invalid date ({field_name}): {Fore.RESET}{field}")

        return field


def suspicious_characters(field, field_name):
    """Warn about suspicious characters.

    Look for standalone characters that could indicate encoding or copy/paste
    errors for languages with accents. For example: foreˆt should be forêt.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # List of suspicious characters, for example:  ́ˆ~`
    suspicious_characters = ["\u00B4", "\u02C6", "\u007E", "\u0060"]

    for character in suspicious_characters:
        # Find the position of the suspicious character in the string
        suspicious_character_position = field.find(character)

        # Python returns -1 if there is no match
        if suspicious_character_position != -1:
            # Create a temporary new string starting from the position of the
            # suspicious character
            field_subset = field[suspicious_character_position:]

            # Print part of the metadata value starting from the suspicious
            # character and spanning enough of the rest to give a preview,
            # but not too much to cause the line to break in terminals with
            # a default of 80 characters width.
            suspicious_character_msg = f"{Fore.YELLOW}Suspicious character ({field_name}): {Fore.RESET}{field_subset}"
            print(f"{suspicious_character_msg:1.80}")

    return field


def language(field):
    """Check if a language is valid ISO 639-1 (alpha 2) or ISO 639-3 (alpha 3).

    Prints the value if it is invalid.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # need to handle "Other" values here...

    # Try to split multi-value field on "||" separator
    for value in field.split("||"):

        # After splitting, check if language value is 2 or 3 characters so we
        # can check it against ISO 639-1 or ISO 639-3 accordingly.
        if len(value) == 2:
            if not languages.get(alpha_2=value):
                print(f"{Fore.RED}Invalid ISO 639-1 language: {Fore.RESET}{value}")

                pass
        elif len(value) == 3:
            if not languages.get(alpha_3=value):
                print(f"{Fore.RED}Invalid ISO 639-3 language: {Fore.RESET}{value}")

                pass
        else:
            print(f"{Fore.RED}Invalid language: {Fore.RESET}{value}")

    return field


def agrovoc(field, field_name):
    """Check subject terms against AGROVOC REST API.

    Function constructor expects the field as well as the field name because
    many fields can now be validated against AGROVOC and we want to be able
    to inform the user in which field the invalid term is.

    Logic copied from agrovoc-lookup.py.

    See: https://github.com/ilri/DSpace/blob/5_x-prod/agrovoc-lookup.py

    Prints a warning if the value is invalid.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # enable transparent request cache with thirty days expiry
    expire_after = timedelta(days=30)
    # Allow overriding the location of the requests cache, just in case we are
    # running in an environment where we can't write to the current working di-
    # rectory (for example from csv-metadata-quality-web).
    REQUESTS_CACHE_DIR = os.environ.get("REQUESTS_CACHE_DIR", ".")
    requests_cache.install_cache(f"{REQUESTS_CACHE_DIR}/agrovoc-response-cache", expire_after=expire_after)

    # prune old cache entries
    requests_cache.core.remove_expired_responses()

    # Try to split multi-value field on "||" separator
    for value in field.split("||"):
        request_url = "http://agrovoc.uniroma2.it/agrovoc/rest/v1/agrovoc/search"
        request_params = {"query": value}

        request = requests.get(request_url, params=request_params)

        if request.status_code == requests.codes.ok:
            data = request.json()

            # check if there are any results
            if len(data["results"]) == 0:
                print(f"{Fore.RED}Invalid AGROVOC ({field_name}): {Fore.RESET}{value}")

    return field


def filename_extension(field):
    """Check filename extension.

    CSVs with a 'filename' column are likely meant as input for the SAFBuilder
    tool, which creates a Simple Archive Format bundle for importing metadata
    with accompanying PDFs or other files into DSpace.

    This check warns if a filename has an uncommon extension (that is, other
    than .pdf, .xls(x), .doc(x), ppt(x), case insensitive).
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    values = field.split("||")

    # List of common filename extentions
    common_filename_extensions = [
        ".pdf",
        ".doc",
        ".docx",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
    ]

    # Iterate over all values
    for value in values:
        # Assume filename extension does not match
        filename_extension_match = False

        for filename_extension in common_filename_extensions:
            # Check for extension at the end of the filename
            pattern = re.escape(filename_extension) + r"$"
            match = re.search(pattern, value, re.IGNORECASE)

            if match is not None:
                # Register the match and stop checking for this filename
                filename_extension_match = True

                break

        if filename_extension_match is False:
            print(f"{Fore.YELLOW}Filename with uncommon extension: {Fore.RESET}{value}")

    return field


def spdx_license_identifier(field):
    """Check if a license is a valid SPDX identifier.

    Prints the value if it is invalid.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    for value in field.split("||"):
        if value not in spdx_license_list.LICENSES:
            print(f"{Fore.YELLOW}Non-SPDX license identifier: {Fore.RESET}{value}")

            pass

    return field
