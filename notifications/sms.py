# N.B. COMMENTED CODE IS PYTHON3

import notification
import urllib
import urllib2
#import urllib.request
#import urllib.parse

class SMS(notification.Notification):
    requiredParams = ["user", "hash", "to"]
    optionalParams = ["sender"]
    # Common params are defined in the parent "notification" Class
    commonParams = notification.Notification.commonParams

    def __init__(self, params):

	hostname = self.getHostname()

        # Set messages
        if "msgalert" in params:
            self.msgalert = params["msgalert"].replace("<hostname>", hostname)
        else:
            self.msgalert = "AirPi " + hostname + " has experienced an error! Nobody panic."

        if "msgdata" in params:
            self.msgdata = params["msgdata"].replace("<hostname>", hostname)
        else:
            self.msgdata  = "AirPi " + hostname + " has just had something interesting happen with its data."

        # Set recipient and sender info
        self.to = (params["to"])
        if "sender" in params:
            self.sender = params["sender"]
        else:
            self.sender= "AirPi"

        # Set TextLocal authorisation info
        self.auth = {}
        self.auth['user'] = params["user"]
        self.auth['hash'] = params["hash"]

        # Warn user this will cost money!
        print("Info: SMS notifications enabled. Data costs will be incurred.")

    def sendNotification(self, event):
        if event == "alert":
            params =  {'username': self.auth["user"], 'hash': self.auth["hash"], 'numbers': self.to, 'message' : self.msgalert[:160], 'sender': self.sender}
        else:
            params =  {'username': self.auth["user"], 'hash': self.auth["hash"], 'numbers': self.to, 'message' : self.msgdata[:160], 'sender': self.sender}
        #data = urllib.parse.urlencode(params)
        data = urllib.urlencode(params)
        data = data.encode('utf-8')
        #request = urllib.request.Request("https://api.txtlocal.com/send/?")
        #f = urllib.request.urlopen(request, data)
        request = urllib2.Request("https://api.txtlocal.com/send/?")
        f = urllib2.urlopen(request, data)
        fr = f.read()
