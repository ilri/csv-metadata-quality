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
