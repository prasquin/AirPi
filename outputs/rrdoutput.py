"""Output AirPi data to an RRD file.

Output AirPi data to a Round-Robin Database (RRD) file
(http://oss.oetiker.ch/rrdtool/). RRD does require some setup by the
user beforehand; this is outside the remit of this module - only basic
RRD support is provided, with minimal error checking. This module
assumes that 'rrdtool' and 'python-rrdtool' are both installed on your
system.

The RRD database should be created in the shell first: an example would
be something along the lines of:

rrdtool create /home/pi/`hostname`.rrd --step 5 \
DS:Temperature-BMP:GAUGE:10:U:U \
DS:Pressure:GAUGE:10:U:U \
DS:Relative_Humidity:GAUGE:10:U:U \
DS:Temperature-DHT:GAUGE:10:U:U \
DS:Light_Level:GAUGE:10:U:U \
DS:Nitrogen_Dioxide:GAUGE:10:U:U \
DS:Carbon_Monoxide:GAUGE:10:U:U \
DS:Air_Quality:GAUGE:10:U:U \
DS:Volume:GAUGE:10:U:U \
RRA:AVERAGE:0.9:1:34560 \
RRA:AVERAGE:0.9:1:105120

Note the last two lines, indicating that two sets of records will be
maintained:
* for a record every  5 seconds during 2 days = 2*24*60*12 =  34560
* for an average over 5 minutes during 1 year =  365*24*12 = 105120

Remember that the Round-Robin nature of RRD means that when the max.
counter is reached for each record set, older values will be
over-written.

To output a graph of results, you may want to use something like the
following in your shell:

rrdtool graph 'graph.png' \
    --imgformat 'PNG' \
    --title "AirPi Output" \
    --watermark "N.B. Some values may be too small to show on graph." \
    --vertical-label "Value" \
    --width '1000' \
    --height '800' \
    --start now-6000s \
    --end now-5920s \
    'DEF:Temp-BMP=file.rrd:Temp-BMP:AVERAGE' \
    'DEF:Pressure=file.rrd:Pressure:AVERAGE' \
    'DEF:Hum=file.rrd:Relative_Humidity:AVERAGE' \
    'DEF:Temp-DHT=file.rrd:Temp-DHT:AVERAGE' \
    'DEF:Light=file.rrd:Light_Level:AVERAGE' \
    'DEF:NO2=file.rrd:Nitrogen_Dioxide:AVERAGE' \
    'DEF:CO=file.rrd:Carbon_Monoxide:AVERAGE' \
    'DEF:AQ=file.rrd:Air_Quality:AVERAGE' \
    'DEF:Vol=file.rrd:Volume:AVERAGE' \
    'LINE1:Temp-BMP#0099CC:Temperature-BMP (C))' \
    'LINE1:Pressure#0099CC:Pressure (hPa)' \
    'LINE1:Hum#993399:Relative Humidity (%)' \
    'LINE1:Temp-DHT#0099CC:Temperature-DHT (C))' \
    'LINE1:Light#66FF33:Light (Ohms)' \
    'LINE1:NO2#3366CC:Nitrogen Dioxide (Ohms)' \
    'LINE1:CO#FF9966:Carbon Monoxide (Ohms)' \
    'LINE1:AQ#CC33FF:Air Quality / VOCs (Ohms)' \
    'LINE1:Vol#999966:Volume (Ohms)'

This module is based on code by Francois Guillier, with permission
(http://www.guillier.org/blog/2014/08/airpi/).

"""


import output
import datetime
import time
import calibration
import rrdtool

class RRDOutput(output.Output):
    """A module to output AirPi data to an RRD file.

    A module which is used to output data from an AirPi into a
    RRD file. This can include GPS data if
    present, along with metadata (again, if present).

    """

    requiredParams = ["target", "outputDir", "outputFile"]
    optionalParams = ["calibration", "metadatareqd"]

    def __init__(self, params):
        if "<date>" in params["outputFile"]:
            filenamedate = time.strftime("%Y%m%d-%H%M")
            params["outputFile"] = \
                params["outputFile"].replace("<date>", filenamedate)
        if "<hostname>" in params["outputFile"]:
            params["outputFile"] = \
                params["outputFile"].replace("<hostname>", self.gethostname())
        # open the file persistently for append
        self.filename = params["outputDir"] + "/" + params["outputFile"]
        #self.file = open(self.filename, "a")
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkcal(params)
        self.target = params["target"]
        self.metadatareqd = params["metadatareqd"]

    def output_metadata(self):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. This particular plugin cannot output metadata, so this
        method will always return True. This is an abstract method of
        the Output class, which this class inherits from; this means you
        shouldn't (and can't) remove this method. See docs in the Output
        class for more info.

        Args:
            self: self.

        Returns:
            boolean True in all cases.
        """
        return True

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

        Args:
            self: self.
            datapoints: A dict containing the data to be output.
            sampletime: datetime representing the time the sample was taken.

        Returns:
            boolean True if data successfully written to file.

        """
        if self.docal == 1:
            datapoints = self.cal.calibrate(datapoints)
        print("writing file")
        names = []
        data = [str(int(time.time()))]
        for point in datapoints:
            if point["name"] != "Location":
                names.append(point["name"].replace(' ', '_'))
                data.append(str(point["value"]))
        print(':'.join(names), ":".join(data))
        try:
            print("writing file")
            print(rrdtool.update(self.filename, '-t', ':'.join(names), ":".join(data)))
            print("file written")
        except Exception as theexception:
            print(str(theexception))
        return True

    def output_coda(self):
        rrdtool graph self.filename + '.png' \
            --imgformat 'PNG' \
            --title "AirPi Output" \
            --watermark "N.B. Some values may be too small to display accurately on the graph." \
            --vertical-label "Value" \
            --width '1000' \
            --height '800' \
            --start now-6000s \
            --end now-5920s \
            'DEF:Temp-BMP=' + self.filename + '.rrd:Temp-BMP:AVERAGE' \
            'DEF:Pressure=' + self.filename + '.rrd:Pressure:AVERAGE' \
            'DEF:Hum=' + self.filename + '.rrd:Relative_Humidity:AVERAGE' \
            'DEF:Temp-DHT=' + self.filename + '.rrd:Temp-DHT:AVERAGE' \
            'DEF:Light=' + self.filename + '.rrd:Light_Level:AVERAGE' \
            'DEF:NO2=' + self.filename + '.rrd:Nitrogen_Dioxide:AVERAGE' \
            'DEF:CO=' + self.filename + '.rrd:Carbon_Monoxide:AVERAGE' \
            'DEF:AQ=' + self.filename + '.rrd:Air_Quality:AVERAGE' \
            'DEF:Vol=' + self.filename + '.rrd:Volume:AVERAGE' \
            'LINE1:Temp-BMP#0099CC:Temperature-BMP (C))' \
            'LINE1:Pressure#0099CC:Pressure (hPa)' \
            'LINE1:Hum#993399:Relative Humidity (%)' \
            'LINE1:Temp-DHT#0099CC:Temperature-DHT (C))' \
            'LINE1:Light#66FF33:Light (Ohms)' \
            'LINE1:NO2#3366CC:Nitrogen Dioxide (Ohms)' \
            'LINE1:CO#FF9966:Carbon Monoxide (Ohms)' \
            'LINE1:AQ#CC33FF:Air Quality / VOCs (Ohms)' \
            'LINE1:Vol#999966:Volume (Ohms)'
