import output
import requests
import json
import calibration

class Xively(output.Output):
    """
    Proxy code courtesy of www.raynerd.co.uk:
    http://airpi.freeforums.net/thread/98/proxy-airpi-py-helpful-schools
    """

    #TODO: Is "needsinternet" really required here? Don't we just use it
    #      in airpi.py? Applies to other output plugins too.
    #TODO: Expand proxy info to a single setting in settings.cfg and
    #      make available to all plugins which require internet access.
    requiredParams = ["APIKey", "FeedID", "needsinternet"]
    optionalParams = ["calibration", "proxyhttp", "proxyhttps"]
    proxies = None

    def __init__(self, params):
        self.APIKey = params["APIKey"]
        self.FeedID = params["FeedID"]
        if "proxyhttp" in params and "proxyhttps" in params:
            self.proxies = {
                          http: params["proxyhttp"],
                          https: params["proxyhttps"]
            }
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(params)

    def output_data(self, dataPoints):
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
            dataPoints: A dict containing the data to be output.

        """
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)
        arr = []
        for i in dataPoints:
            # handle GPS data
            if i["name"] == "Location":
                arr.append({"location": {"disposition": i["Disposition"], "ele": i["Altitude"], "exposure": i["Exposure"], "domain": "physical", "lat": i["Latitude"], "lon": i["Longitude"]}})
            if i["value"] != None: #this means it has no data to upload.
                arr.append({"id":i["name"],"current_value":round(i["value"],2)})
        a = json.dumps({"version":"1.0.0","datastreams":arr})
        try:
            if self.proxies is None:
                z = requests.put("https://api.xively.com/v2/feeds/"+self.FeedID+".json", headers = {"X-ApiKey":self.APIKey}, data = a)
            else:
                z = requests.put("https://api.xively.com/v2/feeds/"+self.FeedID+".json", headers = {"X-ApiKey":self.APIKey}, data = a, proxies = self.proxies)
            if z.text != "": 
                print "Error: Xively message - " + z.text
                print "Error: Xively URL - " + z.url
                return False
        except Exception:
            return False
        return True

    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this plugin.
        Metadata is set in airpi.py and then passed as a dict to each plugin
        which wants to output it. Even if it is not appropriate for the output
        plugin to output metadata, this method is required because airpi.py
        looks for it in its own output_metadata() method. In such cases, this
        method will simply return boolean True.

        Args:
            self: self.
            metadata: dict The metadata for the run.

        """
        return True