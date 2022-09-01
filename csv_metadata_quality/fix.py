# SPDX-License-Identifier: GPL-3.0-only

import re
from unicodedata import normalize

import country_converter as coco
import pandas as pd
from colorama import Fore
from ftfy import TextFixerConfig, fix_text

from csv_metadata_quality.util import is_mojibake, is_nfc


def whitespace(field, field_name):
    """Fix whitespace issues.

    Return string with leading, trailing, and consecutive whitespace trimmed.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Initialize an empty list to hold the cleaned values
    values = list()

    # Try to split multi-value field on "||" separator
    for value in field.split("||"):
        # Strip leading and trailing whitespace
        value = value.strip()

        # Replace excessive whitespace (>2) with one space
        pattern = re.compile(r"\s{2,}")
        match = re.findall(pattern, value)

        if match:
            print(
                f"{Fore.GREEN}Removing excessive whitespace ({field_name}): {Fore.RESET}{value}"
            )
            value = re.sub(pattern, " ", value)

        # Save cleaned value
        values.append(value)

    # Create a new field consisting of all values joined with "||"
    new_field = "||".join(values)

    return new_field


def separators(field, field_name):
    """Fix for invalid and unnecessary multi-value separators, for example:

        value|value
        value|||value
        value||value||

    Prints the field with the invalid multi-value separator.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Initialize an empty list to hold the cleaned values
    values = list()

    # Try to split multi-value field on "||" separator
    for value in field.split("||"):
        # Check if the value is blank and skip it
        if value == "":
            print(
                f"{Fore.GREEN}Fixing unnecessary multi-value separator ({field_name}): {Fore.RESET}{field}"
            )

            continue

        # After splitting, see if there are any remaining "|" characters
        pattern = re.compile(r"\|")
        match = re.findall(pattern, value)

        if match:
            print(
                f"{Fore.GREEN}Fixing invalid multi-value separator ({field_name}): {Fore.RESET}{value}"
            )

            value = re.sub(pattern, "||", value)

        # Save cleaned value
        values.append(value)

    # Create a new field consisting of all values joined with "||"
    new_field = "||".join(values)

    return new_field


def unnecessary_unicode(field):
    """Remove and replace unnecessary Unicode characters.

    Removes unnecessary Unicode characters like:
        - Zero-width space (U+200B)
        - Replacement character (U+FFFD)

    Replaces unnecessary Unicode characters like:
        - Soft hyphen (U+00AD) → hyphen
        - No-break space (U+00A0) → space
        - Thin space (U+2009) → space

    Return string with characters removed or replaced.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Check for zero-width space characters (U+200B)
    pattern = re.compile(r"\u200B")
    match = re.findall(pattern, field)

    if match:
        print(f"{Fore.GREEN}Removing unnecessary Unicode (U+200B): {Fore.RESET}{field}")
        field = re.sub(pattern, "", field)

    # Check for replacement characters (U+FFFD)
    pattern = re.compile(r"\uFFFD")
    match = re.findall(pattern, field)

    if match:
        print(f"{Fore.GREEN}Removing unnecessary Unicode (U+FFFD): {Fore.RESET}{field}")
        field = re.sub(pattern, "", field)

    # Check for no-break spaces (U+00A0)
    pattern = re.compile(r"\u00A0")
    match = re.findall(pattern, field)

    if match:
        print(
            f"{Fore.GREEN}Replacing unnecessary Unicode (U+00A0): {Fore.RESET}{field}"
        )
        field = re.sub(pattern, " ", field)

    # Check for soft hyphens (U+00AD), sometimes preceeded with a normal hyphen
    pattern = re.compile(r"\u002D*?\u00AD")
    match = re.findall(pattern, field)

    if match:
        print(
            f"{Fore.GREEN}Replacing unnecessary Unicode (U+00AD): {Fore.RESET}{field}"
        )
        field = re.sub(pattern, "-", field)

    # Check for thin spaces (U+2009)
    pattern = re.compile(r"\u2009")
    match = re.findall(pattern, field)

    if match:
        print(
            f"{Fore.GREEN}Replacing unnecessary Unicode (U+2009): {Fore.RESET}{field}"
        )
        field = re.sub(pattern, " ", field)

    return field


def duplicates(field, field_name):
    """Remove duplicate metadata values."""

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    values = field.split("||")

    # Initialize an empty list to hold the de-duplicated values
    new_values = list()

    # Iterate over all values
    for value in values:
        # Check if each value exists in our list of values already
        if value not in new_values:
            new_values.append(value)
        else:
            print(
                f"{Fore.GREEN}Removing duplicate value ({field_name}): {Fore.RESET}{value}"
            )

    # Create a new field consisting of all values joined with "||"
    new_field = "||".join(new_values)

    return new_field


def newlines(field, field_name):
    """Fix newlines.

    Single metadata values should not span multiple lines because this is not
    rendered properly in DSpace's XMLUI and even causes issues during import.

    Implementation note: this currently only detects Unix line feeds (0x0a).
    This is essentially when a user presses "Enter" to move to the next line.
    Other newlines like the Windows carriage return are already handled with
    the string stipping performed in the whitespace fixes.

    Confusingly, in Vim '\n' matches a line feed when searching, but you must
    use '\r' to *insert* a line feed, ie in a search and replace expression.

    Return string with newlines removed.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Check for Unix line feed (LF)
    match = re.findall(r"\n", field)

    if match:
        print(f"{Fore.GREEN}Removing newline ({field_name}): {Fore.RESET}{field}")
        field = field.replace("\n", "")

    return field


def comma_space(field, field_name):
    """Fix occurrences of commas missing a trailing space, for example:

    Orth,Alan S.

    This is a very common mistake in author and citation fields.

    Return string with a space added.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Check for comma followed by a word character
    match = re.findall(r",\w", field)

    if match:
        print(
            f"{Fore.GREEN}Adding space after comma ({field_name}): {Fore.RESET}{field}"
        )
        field = re.sub(r",(\w)", r", \1", field)

    return field


def normalize_unicode(field, field_name):
    """Fix occurrences of decomposed Unicode characters by normalizing them
    with NFC to their canonical forms, for example:

    Ouédraogo, Mathieu → Ouédraogo, Mathieu

    Return normalized string.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Check if the current string is using normalized Unicode (NFC)
    if not is_nfc(field):
        print(f"{Fore.GREEN}Normalizing Unicode ({field_name}): {Fore.RESET}{field}")
        field = normalize("NFC", field)

    return field


def mojibake(field, field_name):
    """Attempts to fix mojibake (text that was encoded in one encoding and deco-
    ded in another, perhaps multiple times). See util.py.

    Return fixed string.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return field

    # We don't want ftfy to change “smart quotes” to "ASCII quotes"
    config = TextFixerConfig(uncurl_quotes=False)

    if is_mojibake(field):
        print(f"{Fore.GREEN}Fixing encoding issue ({field_name}): {Fore.RESET}{field}")

        return fix_text(field, config)
    else:
        return field


def countries_match_regions(row):
    """Check for the scenario where an item has country coverage metadata, but
    does not have the corresponding region metadata. For example, an item that
    has country coverage "Kenya" should also have region "Eastern Africa" acc-
    ording to the UN M.49 classification scheme.

    See: https://unstats.un.org/unsd/methodology/m49/

    Return fixed string.
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

    # Iterate over the labels of the current row's values to get the names of
    # the title and citation columns. Then we check if the title is present in
    # the citation.
    for label in row.axes[0]:
        # Find the name of the country column
        match = re.match(r"^.*?country.*$", label)
        if match is not None:
            country_column_name = label

        # Find the name of the region column
        match = re.match(r"^.*?region.*$", label)
        if match is not None:
            region_column_name = label

        # Find the name of the title column
        match = re.match(r"^(dc|dcterms)\.title.*$", label)
        if match is not None:
            title_column_name = label

    # Make sure we found the country and region columns
    if country_column_name != "" and region_column_name != "":
        # If we don't have any countries then we should return early before
        # suggesting regions.
        if row[country_column_name] is not None:
            countries = row[country_column_name].split("||")
        else:
            return row

        if row[region_column_name] is not None:
            regions = row[region_column_name].split("||")
        else:
            regions = list()

        # An empty list for our regions so we can keep track for all countries
        missing_regions = list()

        for country in countries:
            # Look up the UN M.49 regions for this country code. CoCo seems to
            # only list the direct region, ie Western Africa, rather than all
            # the parent regions ("Sub-Saharan Africa", "Africa", "World")
            un_region = cc.convert(names=country, to="UNRegion")

            if un_region not in regions:
                if un_region not in missing_regions:
                    missing_regions.append(un_region)

        if len(missing_regions) > 0:
            for missing_region in missing_regions:
                print(
                    f"{Fore.YELLOW}Adding missing region ({missing_region}): {Fore.RESET}{row[title_column_name]}"
                )

        # Add the missing regions back to the row, paying attention to whether
        # or not the row's region column is None (aka null) or just an empty
        # string (length would be 0).
        if row[region_column_name] is not None and len(row[region_column_name]) > 0:
            row[region_column_name] = (
                row[region_column_name] + "||" + "||".join(missing_regions)
            )
        else:
            row[region_column_name] = "||".join(missing_regions)

    return row
