import notification
import os
import time
from twitter import *

class Tweet(notification.Notification):
    requiredParams = ["consumerkey", "consumersecret"]
    optionalParams = []
    # Common params are defined in the parent "notification" Class
    commonParams = notification.Notification.commonParams

    def __init__(self, params):

        # Set up Twitter authentication
        CONSUMER_KEY = params["consumerkey"]
        CONSUMER_SECRET = params["consumersecret"]

        oauth_filename = os.path.join(os.path.expanduser("~"),".twitterairpi_oauth")
        if not os.path.exists(oauth_filename):
           oauth_dance("UoL AirPis", CONSUMER_KEY, CONSUMER_SECRET, oauth_filename)
        (oauth_token, oauth_token_secret) = read_token_file(oauth_filename)

        # Log in to Twitter
        auth = OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET)
        self.twitter = Twitter(auth=auth)

        # Set messages 
        hostname = self.getHostname()
        
        if "msgalertsensor" in params:
            self.msgalertsensor = params["msgalertsensor"].replace("<hostname>", hostname)
        else:
            self.msgalertsensor = "AirPi " + hostname + " has experienced a sensor error. It apologies profusely."
        if "msgalertoutput" in params:
            self.msgalertoutput = params["msgalertoutput"].replace("<hostname>", hostname)
        else:
            self.msgalertoutput = "AirPi" + hostname + " has experienced an output error! It apologises profusely."

        if "msgdata" in params:
            self.msgdata = params["msgdata"].replace("<hostname>", hostname)
        else:
            self.msgdata = "Something interesting has happened with AirPi " + hostname + ". You'd better come see this..."

    def sendNotification(self, event):
        # We must include a timestamp as insurance:
        # Twitter won't let you repeat the same Tweet twice in a row
        stamp = time.strftime("%H:%M: ")
        if event == "alertsensor":
                msg = (stamp + self.msgalertsensor)[:140]
        elif event == "alertoutput":
                msg = (stamp + self.msgalertoutput)[:140]
        elif event == "data":
                msg = (stamp + self.msgdata)[:140]
        self.twitter.statuses.update(status=msg)
