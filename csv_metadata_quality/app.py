from csv_metadata_quality.version import VERSION
import argparse
import csv_metadata_quality.check as check
import csv_metadata_quality.fix as fix
import pandas as pd
import re
import signal
import sys


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Metadata quality checker and fixer.')
    parser.add_argument('--agrovoc-fields', '-a', help='Comma-separated list of fields to validate against AGROVOC, for example: dc.subject,cg.coverage.country')
    parser.add_argument('--input-file', '-i', help='Path to input file. Can be UTF-8 CSV or Excel XLSX.', required=True, type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument('--output-file', '-o', help='Path to output file (always CSV).', required=True, type=argparse.FileType('w', encoding='UTF-8'))
    parser.add_argument('--unsafe-fixes', '-u', help='Perform unsafe fixes.', action='store_true')
    parser.add_argument('--version', '-V', action='version', version=f'CSV Metadata Quality v{VERSION}')
    args = parser.parse_args()

    return args


def signal_handler(signal, frame):
    sys.exit(1)


def run(argv):
    args = parse_args(argv)

    # set the signal handler for SIGINT (^C)
    signal.signal(signal.SIGINT, signal_handler)

    # Read all fields as strings so dates don't get converted from 1998 to 1998.0
    df = pd.read_csv(args.input_file, dtype=str)

    for column in df.columns.values.tolist():
        # Fix: whitespace
        df[column] = df[column].apply(fix.whitespace)

        # Fix: newlines
        if args.unsafe_fixes:
            df[column] = df[column].apply(fix.newlines)

        # Fix: unnecessary Unicode
        df[column] = df[column].apply(fix.unnecessary_unicode)

        # Check: invalid multi-value separator
        df[column] = df[column].apply(check.separators)

        # Check: suspicious characters
        df[column] = df[column].apply(check.suspicious_characters, field_name=column)

        # Fix: invalid multi-value separator
        if args.unsafe_fixes:
            df[column] = df[column].apply(fix.separators)
            # Run whitespace fix again after fixing invalid separators
            df[column] = df[column].apply(fix.whitespace)

        # Fix: duplicate metadata values
        df[column] = df[column].apply(fix.duplicates)

        # Check: invalid AGROVOC subject
        if args.agrovoc_fields:
            # Identify fields the user wants to validate against AGROVOC
            for field in args.agrovoc_fields.split(','):
                if column == field:
                    df[column] = df[column].apply(check.agrovoc, field_name=column)

        # Check: invalid language
        match = re.match(r'^.*?language.*$', column)
        if match is not None:
            df[column] = df[column].apply(check.language)

        # Check: invalid ISSN
        match = re.match(r'^.*?issn.*$', column)
        if match is not None:
            df[column] = df[column].apply(check.issn)

        # Check: invalid ISBN
        match = re.match(r'^.*?isbn.*$', column)
        if match is not None:
            df[column] = df[column].apply(check.isbn)

        # Check: invalid date
        match = re.match(r'^.*?date.*$', column)
        if match is not None:
            df[column] = df[column].apply(check.date)

    # Write
    df.to_csv(args.output_file, index=False)

    # Close the input and output files before exiting
    args.input_file.close()
    args.output_file.close()

    sys.exit(0)
