import smtplib
import logging.config
from settings import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('notifier')
__version__ = "1.0"


class Email(object):
    """"
    Send a email using this class.

    Suppported methods:
        __init__():   constructor that initializes sender email account, password, mail server and mail server port
        send_email(): send a email to a list of receivers
    """

    def __init__(self, sender, password, email_host, port):
        """ Constructor """
        self.sender = sender
        self.password = password

        # email server settings
        self.email_host = email_host
        self.port = port

    def send_email(self, receiver_list, text):
        """ Send email """

        gmail_user = self.sender
        gmail_pwd = self.password
        FROM = self.sender
        TO = receiver_list  # list

        SUBJECT = "5G-MEDIA SVP Recommendations"
        TEXT = text

        # Prepare actual message
        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

        try:
            server = smtplib.SMTP(self.email_host, self.port)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            server.quit()

        except:
            import traceback
            # traceback.print_stack()
            traceback.print_exc()

    def send_html_email(self, receiver_list, text, html):
        """
        Send email included HTML table
        """

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart('alternative')

        msg['Subject'] = "[ANGEL] Angel platform notification"
        msg['From'] = self.sender
        msg['To'] = receiver_list

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        msg.attach(part1)
        msg.attach(part2)

        try:
            server = smtplib.SMTP(self.email_host, self.port)
            server.ehlo()
            server.starttls()
            server.login(self.sender, self.password)
            server.sendmail(self.sender, receiver_list, msg.as_string())
            server.quit()
        except:
            import traceback
            # traceback.print_stack()
            traceback.print_exc()
