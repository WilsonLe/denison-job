import smtplib
import ssl
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
load_dotenv()


class Emailer():
    def __init__(self):
        self.port = 465  # For SSL
        self.smtp_server = "smtp.gmail.com"
        self.sender_email = os.getenv('MAIL_ADDRESS')
        self.password = os.getenv('MAIL_PASS')

    def send(
            self,
            receiver_email,
            subject,
            html_message
    ):
        """send email

        Args:
            receiver_email (string): email address of receiver
            subject (string): subject of email
            html_message (string): content of email
        """
        message = f"""
        <html>
            <body>
                <p>{html_message}</p>
            </body>
        </html>
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = receiver_email
        message.attach(MIMEText(message, "html"))

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, receiver_email,
                            message.as_string())
