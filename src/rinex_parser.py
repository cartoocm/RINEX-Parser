import datetime
import os
from rinex_header import *

class RINEXFile():
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

        self.header = RINEXHeader(''.join([header, eoh]))
