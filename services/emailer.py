import smtplib
from email.mime.text import MIMEText

SMTP_HOST = "smtp.example.com"  # ВСТАВЬ СВОЙ SMTP
SMTP_PORT = 465
SMTP_USER = "your_email@example.com"
SMTP_PASS = "your_password"

def send_email(recipient, subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = recipient
    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail(SMTP_USER, [recipient], msg.as_string())
    server.quit()