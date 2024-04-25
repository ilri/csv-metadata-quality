# SPDX-License-Identifier: GPL-3.0-only

import argparse
import os
import re
import signal
import sys
from datetime import timedelta

import pandas as pd
import requests_cache
from colorama import Fore

import csv_metadata_quality.check as check
import csv_metadata_quality.experimental as experimental
import csv_metadata_quality.fix as fix
from csv_metadata_quality.version import VERSION


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Metadata quality checker and fixer.")
    parser.add_argument(
        "--agrovoc-fields",
        "-a",
        help="Comma-separated list of fields to validate against AGROVOC, for example: dcterms.subject,cg.coverage.country",
    )
    parser.add_argument(
        "--drop-invalid-agrovoc",
        "-d",
        help="After validating metadata values against AGROVOC, drop invalid values.",
        action="store_true",
    )
    parser.add_argument(
        "--experimental-checks",
        "-e",
        help="Enable experimental checks like language detection",
        action="store_true",
    )
    parser.add_argument(
        "--input-file",
        "-i",
        help="Path to input file. Must be a UTF-8 CSV.",
        required=True,
        type=argparse.FileType("r", encoding="UTF-8"),
    )
    parser.add_argument(
        "--output-file",
        "-o",
        help="Path to output file (always CSV).",
        required=True,
        type=argparse.FileType("w", encoding="UTF-8"),
    )
    parser.add_argument(
        "--unsafe-fixes", "-u", help="Perform unsafe fixes.", action="store_true"
    )
    parser.add_argument(
        "--version", "-V", action="version", version=f"CSV Metadata Quality v{VERSION}"
    )
    parser.add_argument(
        "--exclude-fields",
        "-x",
        help="Comma-separated list of fields to skip, for example: dc.contributor.author,dcterms.bibliographicCitation",
    )
    args = parser.parse_args()

    return args


def signal_handler(signal, frame):
    sys.exit(1)


def run(argv):
    args = parse_args(argv)

    # set the signal handler for SIGINT (^C)
    signal.signal(signal.SIGINT, signal_handler)

    # Read all fields as strings so dates don't get converted from 1998 to 1998.0
    df = pd.read_csv(args.input_file, dtype_backend="pyarrow", dtype="str")

    # Check if the user requested to skip any fields
    if args.exclude_fields:
        # Split the list of excluded fields on ',' into a list. Note that the
        # user should be careful to no include spaces here.
        exclude = args.exclude_fields.split(",")
    else:
        exclude = []

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
    requests_cache.delete()

    for column in df.columns:
        if column in exclude:
            print(f"{Fore.YELLOW}Skipping {Fore.RESET}{column}")

            continue

        if args.unsafe_fixes:
            # Skip whitespace and newline fixes on abstracts and descriptions
            # because there are too many with legitimate multi-line metadata.
            match = re.match(r"^.*?(abstract|description).*$", column)
            if match is None:
                # Fix: whitespace
                df[column] = df[column].apply(fix.whitespace, field_name=column)

                # Fix: newlines
                df[column] = df[column].apply(fix.newlines, field_name=column)

        # Fix: missing space after comma. Only run on author and citation
        # fields for now, as this problem is mostly an issue in names.
        if args.unsafe_fixes:
            match = re.match(r"^.*?(author|[Cc]itation).*$", column)
            if match is not None:
                df[column] = df[column].apply(fix.comma_space, field_name=column)

        # Fix: perform Unicode normalization (NFC) to convert decomposed
        # characters into their canonical forms.
        if args.unsafe_fixes:
            df[column] = df[column].apply(fix.normalize_unicode, field_name=column)

        # Check: suspicious characters
        df[column].apply(check.suspicious_characters, field_name=column)

        # Fix: mojibake. If unsafe fixes are not enabled then we only check.
        if args.unsafe_fixes:
            df[column] = df[column].apply(fix.mojibake, field_name=column)
        else:
            df[column].apply(check.mojibake, field_name=column)

        # Fix: unnecessary Unicode
        df[column] = df[column].apply(fix.unnecessary_unicode)

        # Fix: normalize DOIs
        match = re.match(r"^.*?identifier\.doi.*$", column)
        if match is not None:
            df[column] = df[column].apply(fix.normalize_dois)

        # Fix: invalid and unnecessary multi-value separators. Skip the title
        # and abstract fields because "|" is used to indicate something like
        # a subtitle.
        match = re.match(r"^.*?(abstract|[Cc]itation|title).*$", column)
        if match is None:
            df[column] = df[column].apply(fix.separators, field_name=column)
            # Run whitespace fix again after fixing invalid separators
            df[column] = df[column].apply(fix.whitespace, field_name=column)

        # Fix: duplicate metadata values
        df[column] = df[column].apply(fix.duplicates, field_name=column)

        # Check: invalid AGROVOC subject and optionally drop them
        if args.agrovoc_fields:
            # Identify fields the user wants to validate against AGROVOC
            for field in args.agrovoc_fields.split(","):
                if column == field:
                    df[column] = df[column].apply(
                        check.agrovoc, field_name=column, drop=args.drop_invalid_agrovoc
                    )

        # Check: invalid language
        match = re.match(r"^.*?language.*$", column)
        if match is not None:
            df[column].apply(check.language)

        # Check: invalid ISSN
        match = re.match(r"^.*?issn.*$", column)
        if match is not None:
            df[column].apply(check.issn)

        # Check: invalid ISBN
        match = re.match(r"^.*?isbn.*$", column)
        if match is not None:
            df[column].apply(check.isbn)

        # Check: invalid date
        match = re.match(r"^.*?(date|dcterms\.issued).*$", column)
        if match is not None:
            df[column].apply(check.date, field_name=column)

        # Check: filename extension
        if column == "filename":
            df[column].apply(check.filename_extension)

        # Check: SPDX license identifier
        match = re.match(r"dcterms\.license.*$", column)
        if match is not None:
            df[column].apply(check.spdx_license_identifier)

    ### End individual column checks ###

    # Check: duplicate items
    # We extract just the title, type, and date issued columns to analyze
    try:
        duplicates_df = df.filter(
            regex=r"dcterms\.title|dc\.title|dcterms\.type|dc\.type|dcterms\.issued|dc\.date\.issued"
        )
        check.duplicate_items(duplicates_df)

        # Delete the temporary duplicates DataFrame
        del duplicates_df
    except IndexError:
        pass

    ##
    # Perform some checks on rows so we can consider items as a whole rather
    # than simple on a field-by-field basis. This allows us to check whether
    # the language used in the title and abstract matches the language indi-
    # cated in the language field, for example.
    #
    # This is slower and apparently frowned upon in the Pandas community be-
    # cause it requires iterating over rows rather than using apply over a
    # column. For now it will have to do.
    ##

    # Transpose the DataFrame so we can consider each row as a column
    df_transposed = df.T

    # Remember, here a "column" is an item (previously row). Perhaps I
    # should rename column in this for loop...
    for column in df_transposed.columns:
        # Check: citation DOI
        check.citation_doi(df_transposed[column], exclude)

        # Check: title in citation
        check.title_in_citation(df_transposed[column], exclude)

        if args.unsafe_fixes:
            # Fix: countries match regions
            df_transposed[column] = fix.countries_match_regions(
                df_transposed[column], exclude
            )
        else:
            # Check: countries match regions
            check.countries_match_regions(df_transposed[column], exclude)

        if args.experimental_checks:
            experimental.correct_language(df_transposed[column], exclude)

    # Transpose the DataFrame back before writing. This is probably wasteful to
    # do every time since we technically only need to do it if we've done the
    # countries/regions fix above, but I can't think of another way for now.
    df_transposed_back = df_transposed.T

    # Write
    df_transposed_back.to_csv(args.output_file, index=False)

    # Close the input and output files before exiting
    args.input_file.close()
    args.output_file.close()

    sys.exit(0)
