#!/usr/bin/env python3

import pandas as pd

def fix_whitespace(field):
    """Fix whitespace issues.

    Return string with leading, trailing, and consecutive whitespace trimmed.
    """

    import re

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

        if len(match) > 0:
            print('DEBUG: Excessive whitespace')
            value = re.sub(pattern, ' ', value)

        # Save cleaned value
        values.append(value)

    # Create a new field consisting of all values joined with "||"
    new_field = '||'.join(values)

    return new_field


# Read all fields as strings so dates don't get converted from 1998 to 1998.0
#df = pd.read_csv('/home/aorth/Downloads/2019-07-26-Bioversity-Migration.csv', dtype=str)
#df = pd.read_csv('/tmp/quality.csv', dtype=str)
df = pd.read_csv('/tmp/omg.csv', dtype=str)

# Fix whitespace in all columns
for column in df.columns.values.tolist():
    print(f'DEBUG: {column}')

    df[column] = df[column].apply(fix_whitespace)

# Write
df.to_csv('/tmp/omg.fixed.csv', index=False)
