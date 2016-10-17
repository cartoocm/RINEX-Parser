"""Exceptions for the RINEXer module"""

class InvalidFilename(Exception):
    """Indicates that a filename does not meet RINEX naming format standards
    """

class InvalidHeader(Exception):
    """Indicates that the RINEX header is syntactically incorrect in some way
    """

class RINEXHeaderFieldError(ValueError):
    """Used to indicate that a RINEX header field was of the wrong data type

    Example:
        If a string is found where a float was expected
    """
