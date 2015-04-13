"""A module to output AirPi data to a CSV file.

A module which is used to output data from an AirPi into a
comma-separated value (csv) file. This can include GPS data if present,
along with metadata (again, if present).

"""

import output
import time
import calibration

class CSVOutput(output.Output):
    """A module to output data to a CSV file.

    A module which is used to output data from an AirPi into a
    comma-separated value (csv) file. This can include GPS data if present,
    along with metadata (again, if present).

    """

    #TODO: Delete these
    requiredParams = ["target", "outputDir", "outputFile"]
    optionalParams = ["calibration", "metadata"]

    requiredSpecificParams = ["outputDir", "outputFile"]
    
    def __init__(self, params):
        if "<date>" in params["outputFile"]:
            filenamedate = time.strftime("%Y%m%d-%H%M")
            params["outputFile"] = \
                params["outputFile"].replace("<date>", filenamedate)
        if "<hostname>" in params["outputFile"]:
            params["outputFile"] = \
                params["outputFile"].replace("<hostname>", self.gethostname())
        # open the file persistently for append
        filename = params["outputDir"] + "/" + params["outputFile"]
        self.file = open(filename, "a")
        # write a header line so we know which sensor is which?
        self.header = False
        super(CSVOutput, self).__init__(params)

    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. Metadata is set in airpi.py and then passed as a dict to
        each plugin which wants to output it.

        Args:
            self: self.
            metadata: dict The metadata for the run.

        """
        if self.dometadata:
            towrite = "\"Run started\",\"" + metadata['STARTTIME'] + "\""
            towrite += "\n\"Operator\",\"" + metadata['OPERATOR'] + "\""
            towrite += "\n\"Raspberry Pi name\",\"" + metadata['PINAME'] + "\""
            towrite += "\n\"Raspberry Pi ID\",\"" +  metadata['PIID'] + "\""
            towrite += "\n\"Sampling frequency\",\"" \
                + metadata['SAMPLEFREQ'] + "\""
            if 'AVERAGEFREQ' in metadata:
                towrite += "\n\"Averaging frequency\",\""
                towrite += metadata['AVERAGEFREQ'] + "\""
            if 'DUMMYDURATION' in metadata:
                towrite += "\n\"Initialising runs\",\""
                towrite += metadata['DUMMYDURATION'] + "\""
            if 'STOPAFTER' in metadata:
                towrite += "\n\"Stopping after\",\""
                towrite += metadata['STOPAFTER'] + "\""
            self.file.write(towrite + "\n")

    def output_data(self, datapoints, sampletime):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration is
        carried out first if required.
        Note this method takes account of the different data formats for
        'standard' sensors as distinct from the GPS. The former present a dict
        containing one value and associated properties such as units and
        symbols, while the latter presents a dict containing several readings
        such as latitude, longitude and altitude, but no units or symbols.

        Args:
            self: self.
            datapoints: A dict containing the data to be output.
            sampletime: datetime representing the time the sample was taken.

        Returns:
            boolean True if data successfully written to file.

        """
        if self.cal:
            datapoints = self.cal.calibrate(datapoints)

        if self.header == False:
            header = "\"Date and time\",\"Unix time\""

        line = "\"" + sampletime.strftime("%Y-%m-%d %H:%M:%S,%f") + "\"," + str(sampletime)

        for point in datapoints:
            if point["name"] != "Location":
                if self.header == False:
                    header = "%s,\"%s %s (%s) (%s)\"" % (header,
                        point["sensor"],
                        point["name"],
                        point["symbol"],
                        point["readingtype"])
                line += "," + str(point["value"])
            else:
                if self.header == False:
                    header += ",\"Latitude (deg)\",\"Longitude (deg)\","
                    header += "Altitude (m)\",\"Exposure\",\"Disposition\""
                props = ["latitude",
                            "longitude",
                            "altitude",
                            "exposure",
                            "disposition"]
                for prop in props:
                    line += "," + str(point[prop])
        line = line[:-1]
        # If it's the first write of this instance do a header so we
        # know what's what:
        if self.header == False:
            self.file.write(header + "\n")
            self.header = True
        self.file.write(line + "\n")
        # Flush the file in case of power failure:
        self.file.flush()
        return True

    def __del__(self):
        """ An exit hook to close the file nicely. """
        self.file.flush()
        self.file.close()
