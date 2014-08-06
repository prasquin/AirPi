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
        if "msgalertsensor" in params:
            self.msgalertsensor = params["msgalertsensor"].replace("<hostname>", hostname)
        else:
            self.msgalertsensor = "AirPi " + hostname + " has experienced a sensor error! It apologises profusely."
        if "msgalertoutput" in params:
            self.msgalertoutput = params["msgalertoutput"].replace("<hostname>", hostname)
        else:
            self.msgalertoutput = "AirPi " + hostname + " has experienced an output error! It apologises profusely."
        if "msgdata" in params:
            self.msgdata = params["msgdata"].replace("<hostname>", hostname)
        else:
            self.msgdata  = "Something interesting has happened with AirPi " + hostname + ". You'd better come see this..."

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
        if event == "alertsensor":
            params =  {'username': self.auth["user"], 'hash': self.auth["hash"], 'numbers': self.to, 'message' : self.msgalertsensor[:160], 'sender': self.sender}
        elif event == "alertoutput":
            params =  {'username': self.auth["user"], 'hash': self.auth["hash"], 'numbers': self.to, 'message' : self.msgalertoutput[:160], 'sender': self.sender}
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
