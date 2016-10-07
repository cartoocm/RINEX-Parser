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
        self.local_file = None
        if os.path.isfile(data):
            filename = os.path.basename(data)
            self.local_file = data
            with open(data, 'rb') as file:
                data = file.read()

        elif not filename:
            raise ValueError('must supply filename with file data')

        self.filename = filename

        self._parseFilename()

        header, eoh, observations = data.partition('END OF HEADER')

        if not eoh:
            raise InvalidHeader('Missing END OF HEADER field')

        parser = {'N': Navigational, 'M': Meteorological, 'O': Observational}
        self.header = parser[self.data_type](header + eoh)


    def _parseFilename(self):
        """Extract variables from filename and assert syntax

        This should only fail if the regex does not match, so the only
        exception which this can raise is an InvalidFilename

        Variables generated:
            data_type   Type of data, string containing 'N', 'O', or 'M' for
                        Navigation, Observation, or Meteorological respectively

            file_type   String containing 'daily', 'hourly', or 'highrate'
                        representing the duration of the file

            start_time  Starting UTC date and time of file data: YYYYDDDHHMM,
                        datetime object

            marker_name Four character site identifier

        Example filenames:
            Long name
                ALIC00AUS_R_20161280000_01D_30S_MO.rnx
                EDSV00AUS_R_20161280000_01D_EN.rnx
                    Note: sample rate ('30S' above) is variably included

            Short name
                bula1280.16d        Daily specifies hours field as integer
                alby028g.16n        Hourly specifies hours as alpha (a-z=0-23)
                ALBY124V00.16d      Highrate has alpha hours and specifies
                                    minutes
        """
        assert self.filename
        filename = self.filename.upper()

        # Define RINEX long and short name regex patterns
        rinex_longname_pattern = re.compile(
            '^[a-z\d]{9}_r_\d{11}_\d\d[dhm]_'
            '(\d\d[a-z]_)?[megjr][mon]\.[cr][rn]x$',
            re.IGNORECASE)

        rinex_shortname_pattern = re.compile(
            '^[a-z\d]{4}\d{3}[a-x\d](\d\d)?\.\d\d[gndmo]$',
            re.IGNORECASE)

        # If the regex matches, we can safely extract variables from filename
        if re.match(rinex_longname_pattern, filename):
            # RINEX longname
            # Remove crx/rnx extension and split name on underscore delimeter
            filename, extension = os.path.splitext(filename)
            split_name = filename.split('_')

            # First four characters of filename contain marker name
            self.marker_name = filename[0:4].upper()

            # Last character of name defines data type (o, m, or n)
            self.data_type = str(split_name[-1][-1]).upper()

            # filetype is assumed based on the unit of time given for range
            # Days = daily, Hours = hourly, Minutes = highrate
            file_types = {'D': 'daily', 'H': 'hourly', 'M': 'highrate'}
            self.file_type = file_types[split_name[3][-1]]

            # Date and time can be given directly to datetime in longname
            date_time = split_name[2]
            self.start_time = datetime.datetime.strptime(date_time, '%Y%j%H%M')

        elif re.match(rinex_shortname_pattern, filename):
            # RINEX shortname
            # First four characters of filename contain marker name
            self.marker_name = filename[0:4].upper()
            # Last character of filename defines data type
            data_type = filename[-1]
            # GLONASS Navigation File
            if data_type == 'G': data_type = 'N'
            # Hatanaka compressed observation file
            if data_type == 'D': data_type = 'O'

            self.data_type = str(data_type)

            # Hour and minute are 0 by default
            hour, minute = 0, 0

            # Filetype is assumed based on hours and whether or not minutes are
            # present: Daily if hours is 0-9, hourly if minutes are not given,
            # otherwise highrate
            check_hour = filename[7:9].lower()
            if re.match('^\d$', check_hour[0]):
                file_type = 'daily'
            else:
                # Get hour for highrate and hourly data
                # Convert alpha-hour to integer, a - x = 0 - 23
                hour = int(ord(check_hour[0]) - 97)
                if check_hour[1] == '.':
                    file_type = 'hourly'
                else:
                    file_type = 'highrate'
                    # Get minutes for highrate data
                    minute = int(filename[8:10])

            self.file_type = file_type

            # Year and day are given uniformly for all file types in shortname
            # Day is 3 digit day of year
            day = int(filename[4:7])
            # Year is given as 2 digits
            year = int(filename.split('.')[-1][0:2])

            self.start_time = datetime.datetime.strptime(
                '{}-{}-{}-{}'.format(year, day, hour, minute), '%y-%j-%H-%M')

        else:
            # Invalid filename did not match regex for RINEX long or short name
            err = 'Filename does not match RINEX formatting: {}'.format(
                filename)
            raise InvalidFilename(err)

        return
    

class RINEXHeader():
    def __init__(self, header):
        header_fields = defaultdict(str)
        for line in header.splitlines():
            field, label = line[:60], trim_whitespace(line[60:])
            header_fields[label] += field

        self.header_fields = dict(header_fields)

        self.version, self.type, satellite = Parser(joint(
            n_ANY(9).parsecmap(float),
            compose(n_ANY(11), one_of('MON')),
            compose(n_ANY(19), n_ANY(1)))).parse(
                self.header_fields['RINEX VERSION / TYPE'])

class Meteorological(RINEXHeader):
    def __init__(self, header):
        RINEXHeader.__init__(self, header)

class Navigational(RINEXHeader):
    def __init__(self, header):
        RINEXHeader.__init__(self, header)

class Observational(RINEXHeader):
    def __init__(self, header):
        RINEXHeader.__init__(self, header)


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
