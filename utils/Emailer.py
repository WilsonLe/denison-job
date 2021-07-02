import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Emailer():
    def __init__(self, email, pw):
        self.port = 465  # For SSL
        self.smtp_server = "smtp.gmail.com"
        self.sender_email = email
        self.password = pw

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
                {html_message}
            </body>
        </html>
        """
        email = MIMEMultipart("alternative")
        email["Subject"] = subject
        email["From"] = self.sender_email
        email["To"] = receiver_email
        email.attach(MIMEText(message, "html"))

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, receiver_email,
                            email.as_string())
