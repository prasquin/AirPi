class Output():
    def __init__(self, data):
        raise NotImplementedError

    def checkCal(self, options):
	doCal = 0;
        if "calibration" in options:
            if options["calibration"].lower() in ["on", "yes", "true", "1"]:
                docal = 1
        return doCal
