#!/usr/bin/env python3

import pandas as pd

def fix_whitespace(value):
    """Fix whitespace issues.

    Return string with leading, trailing, and consecutive whitespace trimmed.
    """

    import re

    # Skip cells with missing values
    if pd.isna(value):
        return

    # Try to split multi-value cells on "||" separator
    #for value in cell.split('||'):

    # Check for leading whitespace
    pattern = re.compile(r'^\s+')
    match = re.findall(pattern, value)

    if len(match) > 0:
        print('DEBUG: Leading whitespace')
        value = re.sub(pattern, '', value)

    # Check for leading whitespace in multi-value cells
    # SOME VALUE|| ANOTHER VALUE
    pattern = re.compile(r'\|\|\s+')
    match = re.findall(pattern, value)

    if len(match) > 0:
        print('DEBUG: Leading whitespace in multi-value cell')
        value = re.sub(pattern, '||', value)

    # Check for trailing whitespace
    pattern = re.compile(r'\s+$')
    match = re.findall(pattern, value)

    if len(match) > 0:
        print('DEBUG: Trailing whitespace')
        value = re.sub(pattern, '', value)

    # Check for trailing whitespace in multi-value cells
    # SOME VALUE ||ANOTHER VALUE
    pattern = re.compile(r'\s+\|\|')
    match = re.findall(pattern, value)

    if len(match) > 0:
        print('DEBUG: Trailing whitespace in multi-value cell')
        value = re.sub(pattern, '||', value)

    return value


# Read all fields as strings so dates don't get converted from 1998 to 1998.0
df = pd.read_csv('/home/aorth/Downloads/2019-07-26-Bioversity-Migration.csv', dtype=str)
#df = pd.read_csv('/tmp/quality.csv')
#df = pd.read_csv('/tmp/omg.csv')

# Fix whitespace in all columns
for column in df.columns.values.tolist():
    print(column)

    # Skip the id column
    #if column == 'id':
    #    continue

    df[column] = df[column].apply(fix_whitespace)

# Write
df.to_csv('/tmp/omg.fixed.csv', index=False)
