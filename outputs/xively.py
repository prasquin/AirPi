import output
import requests
import json
import calibration

class Xively(output.Output):
    """
    Proxy code courtesy of www.raynerd.co.uk:
    http://airpi.freeforums.net/thread/98/proxy-airpi-py-helpful-schools
    """

    #TODO: Is "target" really required here? Don't we just use it
    #      in airpi.py? Applies to other output plugins too.
    #TODO: Expand proxy info to a single setting in settings.cfg and
    #      make available to all plugins which require internet access.
    requiredParams = ["target", "apikey", "feedid"]
    optionalParams = ["calibration", "proxyhttp", "proxyhttps"]
    proxies = None

    def __init__(self, params):
        self.apikey = params["apikey"]
        self.feedid = params["feedid"]
        if "proxyhttp" in params and "proxyhttps" in params:
            self.proxies = {
                          http: params["proxyhttp"],
                          https: params["proxyhttps"]
            }
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkcal(params)
        self.target = params["target"]

    def output_data(self, dataPoints, dummy):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration is
        carried out first if required.
        Note this method takes account of the different data formats for
        'standard' sensors as distinct from the GPS. The former present a dict
        containing one value and associated properties such as units and
        symbols, while the latter presents a dict containing several readings
        such as latitude, longitude and altitude, but no units or symbols.
        Because this particular plugin (xively) does not show time, the
        third argument (normally called 'sampletime') is called 'dummy'
        to facilitate compliance with pylint.

        Args:
            self: self.
            dataPoints: A dict containing the data to be output.
            dummy: datetime representing the time the sample was taken.

        Returns:
            boolean True if output successfully. False if not.

        """
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)
        arr = []
        for i in dataPoints:
            # handle GPS data
            if i["name"] == "Location":
                arr.append({"location": {"disposition": i["Disposition"], "ele": i["Altitude"], "exposure": i["Exposure"], "domain": "physical", "lat": i["Latitude"], "lon": i["Longitude"]}})
            if i["value"] != None: #this means it has no data to upload.
                arr.append({"id":i["name"], "current_value":round(i["value"], 2)})
        a = json.dumps({"version":"1.0.0", "datastreams":arr})
        try:
            if self.proxies is None:
                z = requests.put("https://api.xively.com/v2/feeds/"+self.feedid+".json", headers={"X-apikey":self.apikey}, data=a)
            else:
                z = requests.put("https://api.xively.com/v2/feeds/"+self.feedid+".json", headers={"X-apikey":self.apikey}, data=a, proxies=self.proxies)
            if z.text != "":
                print("Error: Xively message - " + z.text)
                print("Error: Xively URL - " + z.url)
                return False
        except Exception:
            return False
        return True

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

    def get_help(self):
        """Get help for this plugin.

        Where help is available for this plugin, get it.

        Returns:
            string The help.

        """
        return "Xively: Make sure the channels in your stream are named as per the sensor names above."
