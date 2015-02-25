"""A module to output data to Ubidots.

A module which is used to output data from an AirPi to the 'Ubidots'
service at http://ubidots.com This does not include metadata, because
Ubidots has no way of representing those data. Note that this plugin
does NOT require you to have the Ubidots Python API installed.

"""

import output
import calibration
import requests
import json

class Ubidot(output.Output):
    """A module to output data to Ubidots.

    A module which is used to output data from an AirPi to the 'Ubidots'
    service at http://ubidots.com  This does not include metadata, because
    Ubidots has no way of representing those data.

    """

    requiredParams = ["token", "needsinternet"]
    optionalParams = ["calibration",
                      "showcost",
                      "ID-BMP085-temp",
                      "ID-BMP085-pres",
                      "ID-DHT22-hum",
                      "ID-DHT22-temp",
                      "ID-LDR ",
                      "ID-TGS2600",
                      "ID-MiCS-2710",
                      "ID-MiCS-5525",
                      "ID-Microphone"
                      ]

    def __init__(self, params):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(params)
        self.token = params["token"]
        if "showcost" in params:
            self.showcost = params["showcost"]
        else:
            self.showcost = False
        self.ubivariables = {}
        for key, value in params.iteritems():
            if key[:3] == "ID-":
                self.ubivariables[key[3:]] = value

    def output_data(self, datapoints, sampletime):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration
        is carried out first if required.

        Args:
            self: self.
            datapoints: A dict containing the data to be output.
            sampletime: datetime representing the time the sample was taken.

        Returns:
            boolean True if data successfully output to Ubidots; False if
                not

        """
        if self.docal == 1:
            datapoints = self.cal.calibrate(datapoints)
        payload= []
        for point in datapoints:
            for ubivariablename, ubivariableid in self.ubivariables.iteritems():
                if point["sensor"] == ubivariablename:
                    if point["value"] is not None:
                        thisvalue = {}
                        thisvalue["variable"] = ubivariableid
                        thisvalue["value"] = point["value"]
                        payload.append(thisvalue)
                        break
        headers = {'Accept': 'application/json; indent=4', 'Content-Type': 'application/json', 'X-Auth-Token': self.token}
        url = "http://things.ubidots.com/api/v1.6/collections/values"
        req = None
        cost = 0
        try:
            req = requests.post(url, data=json.dumps(payload), headers=headers)
        except Exception, e:
            print("ERROR: Failed to POST any values to Ubidots")
            print("ERROR: " + str(e))
            return False
        for response in req.json():
            if response["status_code"] is not 201:
                print("ERROR: Failed to POST this value to Ubidots.")
                return False
            else:
                cost += 1
        if self.showcost:
            print("Ubidots upload cost " + str(cost) + " dots.")
        return True

    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. Metadata is set in airpi.py and then passed as a dict to
        each plugin which wants to output it. Even if it is not
        appropriate for the output plugin to output metadata, this
        method is required because airpi.py looks for it in its own
        output_metadata() method. In such cases, this method will simply
        return boolean True.

        Args:
            self: self.
            metadata: dict The metadata for the run.

        Returns:
            boolean True in all cases.

        """
        return True
