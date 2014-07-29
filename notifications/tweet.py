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

        hostname = self.getHostname()

        # Set messages 
        hostname = self.getHostname()
        
        if "msgalert" in params:
            self.msgalert = params["msgalert"].replace("<hostname>", hostname)
        else:
            self.msgalert = hostname + " has experienced an error! Nobody panic."

        if "msgdata" in params:
            self.msgdata = params["msgdata"].replace("<hostname>", hostname)
        else:
            self.msgdata  = hostname + " has just had something interesting happen with its data."

    def sendNotification(self, event):
        # We must include a timestamp as insurance:
        # Twitter won't let you repeat the same Tweet twice in a row
        stamp = time.strftime("%H:%M: ")
        if event == "alert":
                msg = (stamp + self.msgalert)[:140]
                self.twitter.statuses.update(status=msg)
        if event == "data" and self.data == True:
                msg = (stamp + self.msgalert)[:140]
                self.twitter.statuses.update(status=msg)
