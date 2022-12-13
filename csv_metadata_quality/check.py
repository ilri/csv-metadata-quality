# SPDX-License-Identifier: GPL-3.0-only

import logging
import os
import re
from datetime import datetime, timedelta

import country_converter as coco
import pandas as pd
import requests
import requests_cache
from colorama import Fore
from pycountry import languages
from stdnum import isbn as stdnum_isbn
from stdnum import issn as stdnum_issn

from csv_metadata_quality.util import is_mojibake, load_spdx_licenses


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

    return


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

    return


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

        return

    try:
        # Check if date is valid YYYY format
        datetime.strptime(field, "%Y")

        return
    except ValueError:
        pass

    try:
        # Check if date is valid YYYY-MM format
        datetime.strptime(field, "%Y-%m")

        return
    except ValueError:
        pass

    try:
        # Check if date is valid YYYY-MM-DD format
        datetime.strptime(field, "%Y-%m-%d")

        return
    except ValueError:
        pass

    try:
        # Check if date is valid YYYY-MM-DDTHH:MM:SSZ format
        datetime.strptime(field, "%Y-%m-%dT%H:%M:%SZ")

        return
    except ValueError:
        print(f"{Fore.RED}Invalid date ({field_name}): {Fore.RESET}{field}")

        return


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

    return


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
        elif len(value) == 3:
            if not languages.get(alpha_3=value):
                print(f"{Fore.RED}Invalid ISO 639-3 language: {Fore.RESET}{value}")
        else:
            print(f"{Fore.RED}Invalid language: {Fore.RESET}{value}")

    return


def agrovoc(field, field_name, drop):
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
    requests_cache.install_cache(
        f"{REQUESTS_CACHE_DIR}/agrovoc-response-cache", expire_after=expire_after
    )

    # prune old cache entries
    # requests_cache.remove_expired_responses()

    # Initialize an empty list to hold the validated AGROVOC values
    values = list()

    # Try to split multi-value field on "||" separator
    for value in field.split("||"):
        request_url = "http://agrovoc.uniroma2.it/agrovoc/rest/v1/agrovoc/search"
        request_params = {"query": value}

        request = requests.get(request_url, params=request_params)

        if request.status_code == requests.codes.ok:
            data = request.json()

            # check if there are any results
            if len(data["results"]) == 0:
                if drop:
                    print(
                        f"{Fore.GREEN}Dropping invalid AGROVOC ({field_name}): {Fore.RESET}{value}"
                    )
                else:
                    print(
                        f"{Fore.RED}Invalid AGROVOC ({field_name}): {Fore.RESET}{value}"
                    )

                    # value is invalid AGROVOC, but we are not dropping
                    values.append(value)
            else:
                # value is valid AGROVOC so save it
                values.append(value)

    # Create a new field consisting of all values joined with "||"
    new_field = "||".join(values)

    return new_field


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

    return


def spdx_license_identifier(field):
    """Check if a license is a valid SPDX identifier.

    Prints the value if it is invalid.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    spdx_licenses = load_spdx_licenses()

    # Try to split multi-value field on "||" separator
    for value in field.split("||"):
        if value not in spdx_licenses:
            print(f"{Fore.YELLOW}Non-SPDX license identifier: {Fore.RESET}{value}")

    return


def duplicate_items(df):
    """Attempt to identify duplicate items.

    First we check the total number of titles and compare it with the number of
    unique titles. If there are less unique titles than total titles we expand
    the search by creating a key (of sorts) for each item that includes their
    title, type, and date issued, and compare it with all the others. If there
    are multiple occurrences of the same title, type, date string then it's a
    very good indicator that the items are duplicates.
    """

    # Extract the names of the title, type, and date issued columns so we can
    # reference them later. First we filter columns by likely patterns, then
    # we extract the name from the first item of the resulting object, ie:
    #
    #   Index(['dcterms.title[en_US]'], dtype='object')
    #
    # But, we need to consider that dc.title.alternative might come before the
    # main title in the CSV, so use a negative lookahead to eliminate that.
    #
    # See: https://regex101.com/r/elyXkW/1
    title_column_name = df.filter(
        regex=r"^(dc|dcterms)\.title(?!\.alternative).*$"
    ).columns[0]
    type_column_name = df.filter(regex=r"^(dcterms\.type|dc\.type).*$").columns[0]
    date_column_name = df.filter(
        regex=r"^(dcterms\.issued|dc\.date\.accessioned).*$"
    ).columns[0]

    items_count_total = df[title_column_name].count()
    items_count_unique = df[title_column_name].nunique()

    if items_count_unique < items_count_total:
        # Create a list to hold our items while we check for duplicates
        items = list()

        for index, row in df.iterrows():
            item_title_type_date = f"{row[title_column_name]}{row[type_column_name]}{row[date_column_name]}"

            if item_title_type_date in items:
                print(
                    f"{Fore.YELLOW}Possible duplicate ({title_column_name}): {Fore.RESET}{row[title_column_name]}"
                )
            else:
                items.append(item_title_type_date)


def mojibake(field, field_name):
    """Check for mojibake (text that was encoded in one encoding and decoded in
    in another, perhaps multiple times). See util.py.

    Prints the string if it contains suspected mojibake.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    if is_mojibake(field):
        print(
            f"{Fore.YELLOW}Possible encoding issue ({field_name}): {Fore.RESET}{field}"
        )

    return


def citation_doi(row, exclude):
    """Check for the scenario where an item has a DOI listed in its citation,
    but does not have a cg.identifier.doi field.

    Function prints a warning if the DOI field is missing, but there is a DOI
    in the citation.
    """
    # Check if the user requested us to skip any DOI fields so we can
    # just return before going any further.
    for field in exclude:
        match = re.match(r"^.*?doi.*$", field)
        if match is not None:
            return

    # Initialize some variables at global scope so that we can set them in the
    # loop scope below and still be able to access them afterwards.
    citation = ""

    # Iterate over the labels of the current row's values to check if a DOI
    # exists. If not, then we extract the citation to see if there is a DOI
    # listed there.
    for label in row.axes[0]:
        # Skip fields with missing values
        if pd.isna(row[label]):
            continue

        # If a DOI field exists we don't need to check the citation
        match = re.match(r"^.*?doi.*$", label)
        if match is not None:
            return

        # Check if the current label is a citation field and make sure the user
        # hasn't asked to skip it. If not, then set the citation.
        match = re.match(r"^.*?[cC]itation.*$", label)
        if match is not None and label not in exclude:
            citation = row[label]

    if citation != "":
        # Check the citation for "doi: 10.1186/1743-422X-9-218"
        doi_match1 = re.match(r"^.*?doi:\s.*$", citation)
        # Check the citation for a DOI URL (doi.org, dx.doi.org, etc)
        doi_match2 = re.match(r"^.*?doi\.org.*$", citation)
        if doi_match1 is not None or doi_match2 is not None:
            print(
                f"{Fore.YELLOW}DOI in citation, but missing a DOI field: {Fore.RESET}{citation}"
            )

    return


def title_in_citation(row, exclude):
    """Check for the scenario where an item's title is missing from its cita-
    tion. This could mean that it is missing entirely, or perhaps just exists
    in a different format (whitespace, accents, etc).

    Function prints a warning if the title does not appear in the citation.
    """
    # Initialize some variables at global scope so that we can set them in the
    # loop scope below and still be able to access them afterwards.
    title = ""
    citation = ""

    # Iterate over the labels of the current row's values to get the names of
    # the title and citation columns. Then we check if the title is present in
    # the citation.
    for label in row.axes[0]:
        # Skip fields with missing values
        if pd.isna(row[label]):
            continue

        # Find the name of the title column
        match = re.match(r"^(dc|dcterms)\.title.*$", label)
        if match is not None and label not in exclude:
            title = row[label]

        # Find the name of the citation column
        match = re.match(r"^.*?[cC]itation.*$", label)
        if match is not None and label not in exclude:
            citation = row[label]

    if citation != "":
        if title not in citation:
            print(f"{Fore.YELLOW}Title is not present in citation: {Fore.RESET}{title}")

    return


def countries_match_regions(row, exclude):
    """Check for the scenario where an item has country coverage metadata, but
    does not have the corresponding region metadata. For example, an item that
    has country coverage "Kenya" should also have region "Eastern Africa" acc-
    ording to the UN M.49 classification scheme.

    See: https://unstats.un.org/unsd/methodology/m49/

    Function prints a warning if the appropriate region is not present.
    """
    # Initialize some variables at global scope so that we can set them in the
    # loop scope below and still be able to access them afterwards.
    country_column_name = ""
    region_column_name = ""
    title_column_name = ""

    # Instantiate a CountryConverter() object here. According to the docs it is
    # more performant to do that as opposed to calling coco.convert() directly
    # because we don't need to re-load the country data with each iteration.
    cc = coco.CountryConverter()

    # Set logging to ERROR so country_converter's convert() doesn't print the
    # "not found in regex" warning message to the screen.
    logging.basicConfig(level=logging.ERROR)

    # Iterate over the labels of the current row's values to get the names of
    # the title and citation columns. Then we check if the title is present in
    # the citation.
    for label in row.axes[0]:
        # Find the name of the country column
        match = re.match(r"^.*?country.*$", label)
        if match is not None:
            country_column_name = label

        # Find the name of the region column, but make sure it's not subregion!
        match = re.match(r"^.*?region.*$", label)
        if match is not None and "sub" not in label:
            region_column_name = label

        # Find the name of the title column
        match = re.match(r"^(dc|dcterms)\.title.*$", label)
        if match is not None:
            title_column_name = label

    # Make sure the user has not asked to exclude any metadata fields. If so, we
    # should return immediately.
    column_names = [country_column_name, region_column_name, title_column_name]
    if any(field in column_names for field in exclude):
        return

    # Make sure we found the country and region columns
    if country_column_name != "" and region_column_name != "":
        # If we don't have any countries then we should return early before
        # suggesting regions.
        if row[country_column_name] is not None:
            countries = row[country_column_name].split("||")
        else:
            return

        if row[region_column_name] is not None:
            regions = row[region_column_name].split("||")
        else:
            regions = list()

        for country in countries:
            # Look up the UN M.49 regions for this country code. CoCo seems to
            # only list the direct region, ie Western Africa, rather than all
            # the parent regions ("Sub-Saharan Africa", "Africa", "World")
            un_region = cc.convert(names=country, to="UNRegion")

            if un_region != "not found" and un_region not in regions:
                print(
                    f"{Fore.YELLOW}Missing region ({country} → {un_region}): {Fore.RESET}{row[title_column_name]}"
                )

    return
