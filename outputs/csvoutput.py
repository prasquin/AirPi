import output
import datetime
import time
import calibration

class CSVOutput(output.Output):
    requiredParams = ["outputDir", "outputFile"]
    optionalParams = ["calibration", "metadatareqd"]

    def __init__(self, params):
        if "<date>" in params["outputFile"]:
            filenamedate = time.strftime("%Y%m%d-%H%M")
            params["outputFile"] = params["outputFile"].replace("<date>", filenamedate)
        if "<hostname>" in params["outputFile"]:
            params["outputFile"] = params["outputFile"].replace("<hostname>", self.getHostname())
        # open the file persistently for append
        filename = params["outputDir"] + "/" + params["outputFile"]
        self.file = open(filename, "a")
        # write a header line so we know which sensor is which?
        self.header = False;
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(params)
        self.metadatareqd = params["metadatareqd"]

    def output_metadata(self, metadata):
        if self.metadatareqd:
            towrite = "\"Run started\",\"" + metadata['STARTTIME'] + "\"\n"
            towrite += "\"Operator\",\"" + metadata['OPERATOR'] + "\"\n"
            towrite += "\"Raspberry Pi name\",\"" + metadata['PINAME'] + "\"\n"
            towrite += "\"Raspberry Pi ID\",\"" +  metadata['PIID'] + "\"\n"
            towrite += "\"Sampling frequency\",\"" + metadata['SAMPLEFREQ'] + "\""
            if "AVERAGEFREQ" in metadata:
                towrite += "\n\"Averaging frequency\",\"" + metadata['AVERAGEFREQ'] + "\"\n"
            self.file.write(towrite + "\n")

    def output_data(self,dataPoints):
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)

        line = "\"" + str(datetime.datetime.now()) + "\"," + str(time.time())
        if self.header == False:
            header = "\"Date and time\",\"Unix time\"";
        for point in dataPoints:
            if point["name"] != "Location":
                if self.header == False:
                    header = "%s,\"%s %s (%s) (%s)\"" % (header, point["sensor"], point["name"], point["symbol"], point["readingType"])
                line += "," + str(point["value"])
            else:
                if self.header == False:
                    header = "%s,\"Latitude (deg)\",\"Longitude (deg)\",\"Altitude (m)\",\"Exposure\",\"Disposition\"" % (header)
                props=["latitude", "longitude", "altitude", "exposure", "disposition"]
                for prop in props:
                    line += "," + str(point[prop])
        line = line[:-1]
        # if it's the first write of this instance do a header so we know what's what
        if self.header == False:
            self.file.write(header + "\n")
            self.header = True
        # write the data line to the file
        self.file.write(line + "\n")
        # don't forget to flush the file in case of power failure
        self.file.flush()
        return True

    #need an exit hook to close the file nicely
    def __del__(self):
        self.file.flush()
        self.file.close()
