import notification
import os
import time
import socket
from twitter import *

class Tweet(notification.Notification):
    requiredParams = ["consumerkey", "consumersecret"]
    optionalParams = ["msgalert", "msgdata"]

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

        # Set up standard messages
        if socket.gethostname().find('.')>=0:
            host = socket.gethostname()
        else:
            host = socket.gethostbyaddr(socket.gethostname())[0]

        # Set default messages 
        self.msgalert = host + " has experienced an error! Nobody panic."
        self.msgdata  = host + " has just had something interesting happen with its data."

        # Set custom messages if present
        if "msgalert" in params:
            if "hostname" in params["msgalert"]:
                self.msgalert = params["msgalert"].replace("<hostname>", host)
            else:
                self.msgalert = params["msgalert"]

        if "msgdata" in params:
            if "hostname" in params["msgdata"]:
                self.msgdata = params["msgdata"].replace("<hostname>", host)
            else:
                self.msgdata = params["msgdata"]

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
