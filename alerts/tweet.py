import alert
import os
import time
import socket
from twitter import *

class Tweet(alert.Alert):
    requiredParams = ["consumerkey", "consumersecret"]
    optionalParams = ["tweet"]

    def __init__(self, params):
        CONSUMER_KEY = params["consumerkey"]
        CONSUMER_SECRET = params["consumersecret"]

        oauth_filename = os.path.join(os.path.expanduser("~"),".twitterairpi_oauth")
        if not os.path.exists(oauth_filename):
           oauth_dance("UoL AirPis", CONSUMER_KEY, CONSUMER_SECRET, oauth_filename)
        (oauth_token, oauth_token_secret) = read_token_file(oauth_filename)

         # log in
        auth = OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET)
        self.twitter = Twitter(auth=auth)

        if "tweet" in params:
            if "<hostname>" in params["tweet"]:
                if socket.gethostname().find('.')>=0:
                    filenamehost = socket.gethostname()
                else:
                    filenamehost = socket.gethostbyaddr(socket.gethostname())[0]
                params["tweet"] = params["tweet"].replace("<hostname>", filenamehost)
	    self.tweet = params["tweet"]
        else:
            self.tweet = "Uh oh, AirPi has experienced an error! This is an automated message left at " + time.strftime("%H:%M") + " . Nobody panic."

    def sendAlert(self):
        try:
            self.twitter.statuses.update(status=self.tweet[:140])
        except Exception as err:
            print(type(err))
            print(err.args)
            print(err)
