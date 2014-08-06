import notification
import smtplib
import email.utils
from email.mime.text import MIMEText

class Email(notification.Notification):
    # Note the filename for this Class cannot be email.py, as that is reserved by Python.
    requiredParams = ["toaddress", "fromname", "fromaddress", "smtpserver", "smtpuser", "smtppass"]
    optionalParams = ["alertsubject", "datasubject", "smtpport", "smtptls"]
    # Common params are defined in the parent "notification Class
    commonParams = notification.Notification.commonParams

    def __init__(self, params):

        self.message = {}
        self.smtp = {}
        self.address = {}

        hostname = self.getHostname()

        # Set subject text
        if "alertsubject" in params:
            self.message["alertsubject"] = params["alertsubject"].replace("<hostname>", hostname)
        else:
            self.message["alertsubject"] = "AirPi alert - " + hostname
        if "datasubject" in params:
            self.message["datasubject"] = params["datasubject"].replace("<hostname>", hostname)
        else:
            self.message["datasubject"] = "AirPi data notification - " + hostname

        # Set body text
        if "msgalertsensor" in params:
            self.message["msgalertsensor"] = params["msgalertsensor"].replace("<hostname>", hostname)
        else:
            self.message["msgalertsensor"] = "AirPi " + hostname + " has experienced a sensor error. It apologises profusely."
        if "msgalertoutput" in params:
            self.message["msgalertoutput"] = params["msgalertoutput"].replace("<hostname>", hostname) 
        else:
            self.message["msgalertoutput"] = "AirPi " + hostname + " has experienced an output error. It apologises profusely."
        if "msgdata" in params:
            self.message["msgdata"] = params["msgdata"].replace("<hostname>", hostname)
        else:
            self.message["msgdata"] = "Something interesting has happened with AirPi " + hostname + ". You'd better come see this..."



        # Set SMTP settings
        self.smtp['server'] = params["smtpserver"]
        if "smtpport" in params and params["smtpport"] != "False":
            self.smtp['port'] = int(params["smtpport"])
        if "smtptls" in params:
            self.smtp['tls'] = params["smtptls"]
        if "smtpuser" in params:
            self.smtp['user'] = params["smtpuser"]
        if "smtppass" in params:
            self.smtp['pass'] = params["smtppass"]

        self.address['toaddress'] = params["toaddress"]

        if "fromaddress" in params:
            self.address['fromaddress'] = params["fromaddress"]
        else:
            self.address['fromaddress'] = "airpi@yourpi.com"

        if "fromname" in params:
            self.address['fromname'] = params["fromname"]
        else:
            self.address['fromname'] = "AirPi"

    def sendNotification(self, event):

        msg  = "X-Priority: 1\n"
        msg += "From: " + self.address["fromname"] + " <" + self.address["fromaddress"] + ">\n"
        msg += "To: " + self.address["toaddress"] + "\n"
        
        if "alert" in event:
            msg += "Subject: " + self.message["alertsubject"] + "\n"
            if event == "alertsensor":
                msg += self.message["msgalertsensor"]
            else:
                msg += self.message["msgalertoutput"]
        else:
            msg += "Subject: " + self.message["datasubject"] + "\n"
            msg += self.message["msgdata"]

        if "port" in self.smtp:
            s = smtplib.SMTP(self.smtp['server'], self.smtp['port'])
        else:
            s = smtplib.SMTP(self.smtp['server'])
       
        if self.smtp['tls']:
            s.starttls()
 
        if "user" in self.smtp:
            try:
                s.login(self.smtp['user'], self.smtp['pass'])
            except (SMTPHeloError, SMTPAuthenticationError, SMTPExecption) as e:
                print e
        
        try:
            s.sendmail(self.address["fromaddress"], [self.address["toaddress"]], msg)
        except Exception as e:
            print e
        s.quit()
