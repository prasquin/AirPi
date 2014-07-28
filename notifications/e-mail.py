import notification
import smtplib
import email.utils
from email.mime.text import MIMEText

class Email(notification.Notification):
    requiredParams = ["toaddress", "fromname", "fromaddress", "smtpserver", "smtpuser", "smtppass"]
    optionalParams = ["alertsubject", "alertbody", "databody", "datasubject", "smtpport", "smtptls"]

    def __init__(self, params):

        self.message = {}
        self.smtp = {}
        self.address = {}

        #TODO: Put hostname in here

        # Set text for 'alert' email
        if "alertsubject" in params:
            self.message["alertsubject"] = params["alertsubject"]
        else:
            self.message["alertsubject"] = "AirPi alert"
        if "alertbody" in params:
            self.message["alertbody"] = params["alertbody"]
        else:
            self.message["alertbody"] = "AirPi has reported an error. It apologises profusely."

        # Set text for 'data notification' email
        if "datasubject" in params:
            self.message["datasubject"] = params["datasubject"]
        else:
            self.message["datasubject"] = "AirPi data notification"
        if "databody" in params:
            self.message["databody"] = params["databody"]
        else:
            self.message["databody"] = "AirPi data has done something interesting."

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

        msg  = "From: " + self.address["fromname"] + " <" + self.address["fromaddress"] + ">\n"
        msg += "To: " + self.address["toaddress"] + "\n"
        if event == "alert":
            msg += "Subject: " + self.message["alertsubject"] + "\n"
            msg += self.message["alertbody"]

        else:
            msg += "Subject: " + self.message["datasubject"] + "\n"
            msg += self.message["databody"]

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
