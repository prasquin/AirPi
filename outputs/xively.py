import output
import requests
import json
import calibration

class Xively(output.Output):
    """
    Proxy code courtesy of www.raynerd.co.uk:
    http://airpi.freeforums.net/thread/98/proxy-airpi-py-helpful-schools
    """

    #TODO: Expand proxy info to a single setting in settings.cfg and
    #      make available to all plugins which require internet access.
    requiredSpecificParams = ["apikey", "feedid"]
    optionalSpecificParams = ["proxyhttp", "proxyhttps"]

    def __init__(self, config):
        super(Xively, self).__init__(config)
        self.apikey = self.params["apikey"]
        self.feedid = self.params["feedid"]
        if "proxyhttp" in self.params and "proxyhttps" in self.params:
            self.proxies = {
                          http: self.params["proxyhttp"],
                          https: self.params["proxyhttps"]
            }

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
        if self.params["calibration"]:
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

    def get_help(self):
        """Get help for this plugin.

        Where help is available for this plugin, get it.

        Returns:
            string The help.

        """
        return "Xively: Make sure the channels in your stream are named as per the sensor names above."
