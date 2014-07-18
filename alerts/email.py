import smtplib
from email.mime.text import MIMEText

class Email(alert.Alert):
    requiredParams = ["to", "smtp"]
    optionalParams = ["from", "subject"]

    def sendAlert():
        msg = MIMEText("There has been an error! Panicking will not help, however.")
        msg["Subject"] = "AirPi error!"
        msg["From"] = "pi@yourpi"
        msg["To"] = "contact@haydnwilliams.com"

        s = smtplib.SMTP("localhost")
        s.send_message(msg)
        s.quit()
