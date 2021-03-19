from ftfy.badness import sequence_weirdness


def is_nfc(field):
    """Utility function to check whether a string is using normalized Unicode.
    Python's built-in unicodedata library has the is_normalized() function, but
    it was only introduced in Python 3.8. By using a simple utility function we
    are able to run on Python >= 3.6 again.

    See: https://docs.python.org/3/library/unicodedata.html

    Return boolean.
    """

    from unicodedata import normalize

    return field == normalize("NFC", field)


def is_mojibake(field):
    """Determines whether a string contains mojibake.

    We commonly deal with CSV files that were *encoded* in UTF-8, but decoded
    as something else like CP-1252 (Windows Latin). This manifests in the form
    of "mojibake", for example:

        - CIAT PublicaÃ§ao
        - CIAT PublicaciÃ³n

    This uses the excellent "fixes text for you" (ftfy) library to determine
    whether a string contains characters that have been encoded in one encoding
    and decoded in another.

    Inspired by this code snippet from Martijn Pieters on StackOverflow:
    https://stackoverflow.com/questions/29071995/identify-garbage-unicode-string-using-python

    Return boolean.
    """
    if not sequence_weirdness(field):
        # Nothing weird, should be okay
        return False
    try:
        field.encode("sloppy-windows-1252")
    except UnicodeEncodeError:
        # Not CP-1252 encodable, probably fine
        return False
    else:
        # Encodable as CP-1252, Mojibake alert level high
        return True
