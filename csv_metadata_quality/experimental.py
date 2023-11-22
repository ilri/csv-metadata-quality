# SPDX-License-Identifier: GPL-3.0-only

import re

import langid
import pandas as pd
from colorama import Fore
from pycountry import languages


def correct_language(row, exclude):
    """Analyze the text used in the title, abstract, and citation fields to pre-
    dict the language being used and compare it with the item's dc.language.iso
    field.

    Function prints an error if the language field does not match the detected
    language and returns the value in the language field if it does match.
    """

    # Initialize some variables at global scope so that we can set them in the
    # loop scope below and still be able to access them afterwards.
    language = ""
    sample_strings = []
    title = None

    # Iterate over the labels of the current row's values. Before we transposed
    # the DataFrame these were the columns in the CSV, ie dc.title and dc.type.
    for label in row.axes[0]:
        # Skip fields with missing values
        if pd.isna(row[label]):
            continue

        # Check if current row has multiple language values (separated by "||")
        match = re.match(r"^.*?language.*$", label)
        if match is not None:
            # Skip fields with multiple language values
            if "||" in row[label]:
                return

            language = row[label]

        # Extract title if it is present (note that we don't allow excluding
        # the title here because it complicates things).
        match = re.match(r"^.*?title.*$", label)
        if match is not None:
            title = row[label]
            # Append title to sample strings
            sample_strings.append(row[label])

        # Extract abstract if it is present
        match = re.match(r"^.*?abstract.*$", label)
        if match is not None and label not in exclude:
            sample_strings.append(row[label])

        # Extract citation if it is present
        match = re.match(r"^.*?[cC]itation.*$", label)
        if match is not None and label not in exclude:
            sample_strings.append(row[label])

    # Make sure language is not blank and is valid ISO 639-1/639-3 before proceeding with language prediction
    if language != "":
        # Check language value like "es"
        if len(language) == 2:
            if not languages.get(alpha_2=language):
                return
        # Check language value like "spa"
        elif len(language) == 3:
            if not languages.get(alpha_3=language):
                return
        # Language value is something else like "Span", do not proceed
        else:
            return
    # Language is blank, do not proceed
    else:
        return

    # Concatenate all sample strings into one string
    sample_text = " ".join(sample_strings)

    # Restrict the langid detection space to reduce false positives
    langid.set_languages(
        ["ar", "de", "en", "es", "fr", "hi", "it", "ja", "ko", "pt", "ru", "vi", "zh"]
    )
    langid_classification = langid.classify(sample_text)

    # langid returns an ISO 639-1 (alpha 2) representation of the detected language, but the current item's language field might be ISO 639-3 (alpha 3) so we should use a pycountry Language object to compare both represenations and give appropriate error messages that match the format used by in the input file.
    detected_language = languages.get(alpha_2=langid_classification[0])
    if len(language) == 2 and language != detected_language.alpha_2:
        print(
            f"{Fore.YELLOW}Possibly incorrect language {language} (detected {detected_language.alpha_2}): {Fore.RESET}{title}"
        )

    elif len(language) == 3 and language != detected_language.alpha_3:
        print(
            f"{Fore.YELLOW}Possibly incorrect language {language} (detected {detected_language.alpha_3}): {Fore.RESET}{title}"
        )

    else:
        return
