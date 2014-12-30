"""A module to output AirPi data to a json file.

A module which is used to output data from an AirPi into a
JavaScript Object Notation (JSON) file. This can include GPS data if
present, along with metadata (again, if present).
Note that one JSON object is created *per datapoint*, so the resultant
file contains hundreds of JSON objects. This means that while each
individual object is valid JSON, the entire file is not. If you're
reading it into something else then you'll need to take account of this,
e.g. http://www.benweaver.com/blog/decode-multiple-json-objects-in-
python.html

The idea and some code for this module came from:
http://airpi.freeforums.net/post/396/thread
https://github.com/river-io/AirPi/blob/master/outputs/log.py

"""

import output
import datetime
import time
import calibration

class JSONOutput(output.Output):
    """A module to output AirPi data to a json file.

    A module which is used to output data from an AirPi into a
    JavaScript Object Notation (json) file. This can include GPS data if
    present, along with metadata (again, if present).

    """

    requiredParams = ["outputDir", "outputFile"]
    optionalParams = ["calibration", "metadatareqd"]

    def __init__(self, params):
        if "<date>" in params["outputFile"]:
            filenamedate = time.strftime("%Y%m%d-%H%M")
            params["outputFile"] = \
                params["outputFile"].replace("<date>", filenamedate)
        if "<hostname>" in params["outputFile"]:
            params["outputFile"] = \
                params["outputFile"].replace("<hostname>", self.getHostname())
        # open the file persistently for append
        filename = params["outputDir"] + "/" + params["outputFile"]
        self.file = open(filename, "a")
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(params)
        self.metadatareqd = params["metadatareqd"]

    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. Metadata is set in airpi.py and then passed as a dict to
        each plugin which wants to output it.

        Args:
            self: self.
            metadata: dict The metadata for the run.

        """
        if self.metadatareqd:
            towrite = "{\"Run started\":\"" + metadata['STARTTIME'] + "\""
            towrite += "\n,\"Operator\":\"" + metadata['OPERATOR'] + "\""
            towrite += "\n,\"Raspberry Pi name\":\"" + metadata['PINAME'] + "\""
            towrite += "\n,\"Raspberry Pi ID\":\"" +  metadata['PIID'] + "\""
            towrite += "\n,\"Sampling frequency\":\"" \
                + metadata['SAMPLEFREQ'] + "\""
            if 'AVERAGEFREQ' in metadata:
                towrite += "\n,\"Averaging frequency\":\""
                towrite += metadata['AVERAGEFREQ'] + "\""
            if 'DUMMYDURATION' in metadata:
                towrite += "\n,\"Initialising runs\":\""
                towrite += metadata['DUMMYDURATION'] + "\""
            if 'STOPAFTER' in metadata:
                towrite += "\n,\"Stopping after\":\""
                towrite += metadata['STOPAFTER'] + "\""
            self.file.write(towrite + "}\n")

    def output_data(self, datapoints, sampletime):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration
        is carried out first if required.
        Note this method takes account of the different data formats for
        'standard' sensors as distinct from the GPS. The former present
        a dict containing one value and associated properties such as
        units and symbols, while the latter presents a dict containing
        several readings such as latitude, longitude and altitude, but
        no units or symbols.
        Remember, one JSON object is output per datapoint, so the file
        will contain lots of them (which isn't valid JSON).

        Args:
            self: self.
            datapoints: A dict containing the data to be output.
            sampletime: datetime representing the time the sample was taken.

        Returns:
            boolean True if data successfully written to file.

        """
        if self.docal == 1:
            datapoints = self.cal.calibrate(datapoints)

        line = '{"Date and time":"' + sampletime.strftime("%Y-%m-%d %H:%M:%S.%f") + '",'
        line += '"Unix time":"' + str(time.time()) + '",'
        for point in datapoints:
            if point["name"] != "Location":
                line += '"' + point["name"] + '"' + ":" + '"' + str(point["value"]) + '",'
            else:
                props = ["latitude",
                            "longitude",
                            "altitude",
                            "exposure",
                            "disposition"]
                for prop in props:
                    line += "\"" + prop + "\":" + str(point[prop]) + "\","
        line = line[:-1] + "}"
        self.file.write(line + "\n")
        # Flush the file in case of power failure:
        self.file.flush()
        return True

    def __del__(self):
        """ An exit hook to close the file nicely. """
        self.file.flush()
        self.file.close()