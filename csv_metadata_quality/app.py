import csv_metadata_quality.check as check
import csv_metadata_quality.fix as fix
import pandas as pd
import re

def main():
    # Read all fields as strings so dates don't get converted from 1998 to 1998.0
    #df = pd.read_csv('/home/aorth/Downloads/2019-07-26-Bioversity-Migration.csv', dtype=str)
    #df = pd.read_csv('/tmp/quality.csv', dtype=str)
    df = pd.read_csv('data/test.csv', dtype=str)

    # Fix whitespace in all columns
    for column in df.columns.values.tolist():
        # Run whitespace fix on all columns
        df[column] = df[column].apply(fix.whitespace)

        # Run invalid multi-value separator check on all columns
        df[column] = df[column].apply(check.separators)

        # check if column is an issn column like dc.identifier.issn
        match = re.match(r'^.*?issn.*$', column)
        if match is not None:
            df[column] = df[column].apply(check.issn)

        # check if column is an isbn column like dc.identifier.isbn
        match = re.match(r'^.*?isbn.*$', column)
        if match is not None:
            df[column] = df[column].apply(check.isbn)

        # check if column is a date column like dc.date.issued
        match = re.match(r'^.*?date.*$', column)
        if match is not None:
            df[column] = df[column].apply(check.date)

    # Write
    df.to_csv('/tmp/test.fixed.csv', index=False)
