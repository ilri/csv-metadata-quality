import argparse
import csv_metadata_quality.check as check
import csv_metadata_quality.fix as fix
import pandas as pd
import re


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Metadata quality checker and fixer.')
    parser.add_argument('--input-file', '-i', help='Path to input file. Can be UTF-8 CSV or Excel XLSX.', required=True, type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument('--output-file', '-o', help='Path to output file (always CSV).', required=True, type=argparse.FileType('w', encoding='UTF-8'))
    parser.add_argument('--unsafe-fixes', '-u', help='Perform unsafe fixes.', action='store_true')
    args = parser.parse_args()

    return args


def main(argv):
    args = parse_args(argv)

    # Read all fields as strings so dates don't get converted from 1998 to 1998.0
    df = pd.read_csv(args.input_file, dtype=str)

    for column in df.columns.values.tolist():
        # Run whitespace fix on all columns
        df[column] = df[column].apply(fix.whitespace)

        # Run invalid multi-value separator check on all columns
        df[column] = df[column].apply(check.separators)

        # Run invalid multi-value separator fix on all columns
        if args.unsafe_fixes:
            df[column] = df[column].apply(fix.separators)
            # Run whitespace fix again after fixing invalid separators
            df[column] = df[column].apply(fix.whitespace)

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
    df.to_csv(args.output_file, index=False)
