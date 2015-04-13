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

    #TODO: Delete these
    requiredParams = ["target", "token"]
    optionalParams = ["calibration",
                      "showcost",
                      "ID-BMP085-temp",
                      "ID-BMP085-pres",
                      "ID-DHT22-hum",
                      "ID-DHT22-temp",
                      "ID-LDR",
                      "ID-TGS2600",
                      "ID-MiCS-2710",
                      "ID-MiCS-5525",
                      "ID-Microphone"
                      ]

    requiredSpecificParams = ["token"]
    optionalSpecificParams = ["showcost",
                      "ID-BMP085-temp",
                      "ID-BMP085-pres",
                      "ID-DHT22-hum",
                      "ID-DHT22-temp",
                      "ID-LDR",
                      "ID-TGS2600",
                      "ID-MiCS-2710",
                      "ID-MiCS-5525",
                      "ID-Microphone"
                      ]

    def __init__(self, params):
        super(Ubidot, self).__init__(params)        
        self.token = params["token"]
        if "showcost" in params:
            self.showcost = params["showcost"]
        else:
            self.showcost = False
        self.ubivariables = {}
        for key, value in params.iteritems():
            if key[:3] == "ID-":
                self.ubivariables[key[3:]] = value

    def output_data(self, datapoints, dummy):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration
        is carried out first if required.
        Because this particular plugin (ubidots) does not show time, the
        third argument (normally called 'sampletime') is called 'dummy'
        to facilitate compliance with pylint.

        Args:
            self: self.
            datapoints: A dict containing the data to be output.
            dummy: datetime representing the time the sample was taken.

        Returns:
            boolean True if data successfully output to Ubidots; False if
                not

        """
        if self.cal:
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
            print("ERROR: Failed to contact the Ubidots service.")
            print("ERROR: " + str(e))
            return False
        for response in req.json():
            if response["status_code"] is not 201:
                print("ERROR: Ubidots responded with an error for this value.")
                return False
            else:
                cost += 1
        if self.showcost:
            print("Ubidots upload cost " + str(cost) + " dots.")
        return True
