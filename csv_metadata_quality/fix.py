import pandas as pd
import re


def whitespace(field):
    """Fix whitespace issues.

    Return string with leading, trailing, and consecutive whitespace trimmed.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Initialize an empty list to hold the cleaned values
    values = list()

    # Try to split multi-value field on "||" separator
    for value in field.split('||'):
        # Strip leading and trailing whitespace
        value = value.strip()

        # Replace excessive whitespace (>2) with one space
        pattern = re.compile(r'\s{2,}')
        match = re.findall(pattern, value)

        if match:
            print(f'Excessive whitespace: {value}')
            value = re.sub(pattern, ' ', value)

        # Save cleaned value
        values.append(value)

    # Create a new field consisting of all values joined with "||"
    new_field = '||'.join(values)

    return new_field


def separators(field):
    """Fix for invalid multi-value separators (ie "|")."""

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Initialize an empty list to hold the cleaned values
    values = list()

    # Try to split multi-value field on "||" separator
    for value in field.split('||'):
        # After splitting, see if there are any remaining "|" characters
        pattern = re.compile(r'\|')
        match = re.findall(pattern, value)

        if match:
            print(f'Fixing invalid multi-value separator: {value}')

            value = re.sub(pattern, '||', value)

        # Save cleaned value
        values.append(value)

    # Create a new field consisting of all values joined with "||"
    new_field = '||'.join(values)

    return new_field


def unnecessary_unicode(field):
    """Remove unnecessary Unicode characters.

    Removes unnecessary Unicode characters like:
        - Zero-width space (U+200B)
        - Replacement character (U+FFFD)
        - No-break space (U+00A0)

    Return string with characters removed.
    """

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Check for zero-width space characters (U+200B)
    pattern = re.compile(r'\u200B')
    match = re.findall(pattern, field)

    if match:
        print(f'Removing unnecessary Unicode (U+200B): {field}')
        field = re.sub(pattern, '', field)

    # Check for replacement characters (U+FFFD)
    pattern = re.compile(r'\uFFFD')
    match = re.findall(pattern, field)

    if match:
        print(f'Removing unnecessary Unicode (U+FFFD): {field}')
        field = re.sub(pattern, '', field)

    # Check for no-break spaces (U+00A0)
    pattern = re.compile(r'\u00A0')
    match = re.findall(pattern, field)

    if match:
        print(f'Removing unnecessary Unicode (U+00A0): {field}')
        field = re.sub(pattern, '', field)

    return field


def duplicates(field):
    """Remove duplicate metadata values."""

    # Skip fields with missing values
    if pd.isna(field):
        return

    # Try to split multi-value field on "||" separator
    values = field.split('||')

    # Initialize an empty list to hold the de-duplicated values
    new_values = list()

    # Iterate over all values
    for value in values:
        # Check if each value exists in our list of values already
        if value not in new_values:
            new_values.append(value)
        else:
            print(f'Dropping duplicate value: {value}')

    # Create a new field consisting of all values joined with "||"
    new_field = '||'.join(new_values)

    return new_field
