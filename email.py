from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from menu import get_daily_menu


def send_email():
    sender_email = ""
    password = ""

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Obědy {datetime.strftime(datetime.today(), '%d. %m. %Y')}"
    message["From"] = sender_email

    html = get_daily_menu()
    message.attach(MIMEText(html, "html"))
    recievers = ["", ""]

    for reciever in recievers:
        message["To"] = reciever
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.forpsi.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, reciever, message.as_string()
            )


if __name__ == "__main__":
    send_email()
