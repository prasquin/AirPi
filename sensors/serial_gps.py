import sensor
import GpsController

gpsc = None # define gps data structure

class serial_gps(sensor.Sensor):
    requiredData = []
    optionalData = []

    def __init__(self, data):
        """Initialise GPS sensor class.

        Initialise the serial_gps sensor class using parameters passed in
        'data'.

        Args:
            self: self.
            data: A dict containing the parameters to be used during setup.

        """
        self.sensorName = "MTK3339"
        self.valName = "Location"
        global gpsc
        try:
            gpsc = GpsController.GpsController()
            gpsc.start()
        except Exception as e:
            print "Exception:", e
            raise

    def getVal(self):
        """Get the current sensor values.

        Get the current sensor values. Actually returns five different values,
        because GPS data are multi-dimensional (i.e. x,y,z are represented by
        latitude, longitude and altitude), plus there is disposition and
        exposure too.

        Args:
            self: self.

        Return:
            float, float, float, string, string
                All of the current values for the sensor.

        """
        global gpsc
        # Assume we're mobile and outside if speed is above 1.0 m/s
        if gpsc.fix.speed > 1.0:
            return (gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude, "mobile", "outdoor")
        else:
            return (gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude, "fixed", "indoor")

    def stopController(self):
        """Stop the GPS controller.

        Stop the GPS controller we created for this sensor. Informing the user
        what's going on at the same time.

        Args:
            self: self.

        """
        global gpsc
        print("[AirPi] GPS controller stopping...")
        gpsc.stopController()
        # wait for the thread to finish
        gpsc.join()
        print("[AirPi] GPS controller stopped.")
