import csv_metadata_quality.check as check
import csv_metadata_quality.fix as fix
import pandas as pd

def run():
    # Read all fields as strings so dates don't get converted from 1998 to 1998.0
    #df = pd.read_csv('/home/aorth/Downloads/2019-07-26-Bioversity-Migration.csv', dtype=str)
    #df = pd.read_csv('/tmp/quality.csv', dtype=str)
    df = pd.read_csv('tests/test.csv', dtype=str)

    # Fix whitespace in all columns
    for column in df.columns.values.tolist():
        print(f'DEBUG: {column}')

        df[column] = df[column].apply(fix.whitespace)

        # Run invalid multi-value separator check on all columns
        df[column] = df[column].apply(check.separators)

        if column == 'dc.identifier.issn':
            df[column] = df[column].apply(check.issn)

        if column == 'dc.identifier.isbn':
            df[column] = df[column].apply(check.isbn)

    # Write
    df.to_csv('/tmp/test.fixed.csv', index=False)
