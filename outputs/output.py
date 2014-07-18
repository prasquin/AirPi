class Output():
    def __init__(self, params):
        raise NotImplementedError

    def checkCal(self, params):
	doCal = 0;
        if "calibration" in params:
            if params["calibration"].lower() in ["on", "yes", "true", "1"]:
                docal = 1
        return doCal
