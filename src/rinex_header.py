import datetime
import os
import re
from parsec import *
from collections import defaultdict

class RINEXHeader():
    def __init__(self, data):
        if not re.match('^(.{61,80}\n)+.{60}END OF HEADER$', data):
            raise InvalidHeader('header does not match RINEX formatting standards')

        self.header = data
        self._parseHeader()

        return

    def _parseHeader(self):
        header_fields = defaultdict(str)
        for line in self.header.splitlines():
            field, label = line[:60], line[60:]
            header_fields[label] += field

        parsed_fields = {}
        for label, field in header_fields.iteritems():
            try:
                print label
                parsed_fields[label] = RINEX_HEADER_FIELD_PARSERS[label].parse(field)

            except KeyError:
                print('field not in schema: {}'.format(label))
                pass

        self.pf = parsed_fields # FOR TESTING


# Custom parser generators
def n_A(n):
    """Given n, return Parser for string of length n, containing only alphanumeric
    characters 
    """ 
    return regex('([A-Za-z0-9]){{{}}}'.format(n))

def n_I(n):
    """ Given n, return parser for an integer between one and n digits long
    """
    return regex('([0-9]){{1,{}}}'.format(n)).parsecmap(int)

def n_ANY(n):
    """Given n, return Parser for string of n length containing any characters

    Useful for ignoring n characters with the compose >> or skip << operations
    or for capturing fixed length fields
    """
    return regex('(.){{{}}}'.format(n))

def n_A3(n):
    """Given n, return parser for space seperated list of n A3's
    
    A3 is a token for three successive alphanumeric characters
    """
    return count(compose(spaces(), n_A(3)), n)

# Lambda funcion to remove excess whitespace from a string
trim_whitespace = lambda a: ' '.join(a.split())

# Define Parsec parser for each RINEX header field 
RINEX_HEADER_FIELD_PARSERS = {

    'RINEX VERSION / TYPE': Parser(joint(
        n_ANY(9).parsecmap(float),
        compose(n_ANY(11), one_of('MON')), 
        compose(n_ANY(19), n_ANY(1)))),

    'PGM / RUN BY / DATE': Parser(
        count(n_ANY(20).parsecmap(trim_whitespace), 3)),

    'COMMENT': Parser(many1(n_ANY(60))),

    'MARKER NAME': Parser(n_ANY(60)).parsecmap(trim_whitespace),

    'MARKER NUMBER': Parser(n_ANY(20)).parsecmap(trim_whitespace),

    'REC # / TYPE / VERS': Parser(count(
        n_ANY(20).parsecmap(trim_whitespace), 3)),

    'ANT # / TYPE': Parser(count(n_ANY(20).parsecmap(trim_whitespace), 2)),

    'ANTENNA: DELTA H/E/N': Parser(count(n_ANY(14).parsecmap(float), 3)),

    'SENSOR MOD/TYPE/ACC': Parser(many1(joint(
        n_ANY(20).parsecmap(trim_whitespace), 
        skip(n_ANY(20).parsecmap(trim_whitespace), n_ANY(6)),
        skip(n_ANY(7).parsecmap(float), n_ANY(4)),
        skip(n_ANY(2), n_ANY(1))))),

    'SYS / # / OBS TYPES': Parser(many1(compose(spaces(), joint(
        one_of('GREJCIS'), compose(spaces(), bind(n_I(3), n_A3))))))

}


class InvalidHeader(Exception):
    """Indicates that the RINEX header is syntactically incorrect in some way
    """

class RINEXHeaderFieldError(ValueError):
    """Used to indicate that a RINEX header field was of the wrong data type
    
    Example:
        If a string is found where a float was expected
    """
