import datetime
import os
from parsec import *
from collections import defaultdict

class RINEX():

    def __init__(self, data, filename=None):
        """Initialize RINEXData object

        Creates RINEXData object when passed a string containing RINEX file
        contents, along with a filename - or just a local filename - then parses
        the RINEX header and filename to extract variables.

        If data is not parsable, then an exception is raised on initialization

        Input:
            data        Local path to RINEX file, or string containing RINEX file data
            filename    RINEX formatted name of file, this is assumed to be the name of
                        the file, if a file is given. It must be provided if input is
                        string containing file data.

        Attributes generated:
            data            String containing inputted data
            filename        String containing RINEX filename
            header          String containing header portion of RINEX data
            observations    String containing all file data after header

        Additional attributes generated depend on header fields in file
        """
        if os.path.isfile(data):
            filename = os.path.basename(data)
            with open(data, 'rb') as file:
                data = file.read()

        elif not filename:
            raise ValueError('must supply filename with file data')

        self.data = data
        self.filename = filename

        header, eoh, self.observations = self.data.partition('END OF HEADER')

        if not eoh:
            raise InvalidHeader('Missing END OF HEADER field')

        self.header = header + eoh

        self._parseHeader()


    def _parseHeader(self):
        header_fields = defaultdict(str)
        for line in self.header.splitlines():
            field, label = line[:60], trim_whitespace(line[60:])
            header_fields[label] += field

        header_fields = dict(header_fields)

	self.version, self.type, satellite = Parser(joint(
            n_ANY(9).parsecmap(float),
            compose(n_ANY(11), one_of('MON')),
            compose(n_ANY(19), n_ANY(1)))).parse(
                header_fields['RINEX VERSION / TYPE'])


class Meteorological(RINEX):
    def __init__(self, file):
        super(Meteorological, self).__init__()

class Navigational(RINEX):
    def __init__(self, file):
        super(Navigational, self).__init__()

class Observational(RINEX):
    def __init__(self, file):
        super(Observational, self).__init__()


def parseRINEX(data, filename=None):
    pass


# Custom parser generators
def n_A(n):
    """Given n, return Parser for string of length n, containing only alphanumeric
    characters
    """
    return regex('([A-Za-z0-9]){{{0}}}'.format(n))

def n_I(n):
    """ Given n, return parser for an integer between one and n digits long
    """
    return regex('([0-9]){{1,{0}}}'.format(n)).parsecmap(int)

def n_ANY(n):
    """Given n, return Parser for string of n length containing any characters

    Useful for ignoring n characters with the compose >> or skip << operations
    or for capturing fixed length fields
    """
    return regex('(.){{{0}}}'.format(n))

def n_A3(n):
    """Given n, return parser for space seperated list of n A3's

    A3 is a token for three successive alphanumeric characters
    """
    return count(compose(spaces(), n_A(3)), n)

# Lambda funcion to remove excess whitespace from a string
trim_whitespace = lambda a: ' '.join(a.split())


class InvalidHeader(Exception):
    """Indicates that the RINEX header is syntactically incorrect in some way
    """

class RINEXHeaderFieldError(ValueError):
    """Used to indicate that a RINEX header field was of the wrong data type

    Example:
        If a string is found where a float was expected
    """
