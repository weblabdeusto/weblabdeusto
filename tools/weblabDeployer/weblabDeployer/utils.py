import smtplib
from email.mime.text import MIMEText


EMAIL_HOST = 'mail.deusto.es'


def send_email(body, subject, from_email, to_email):

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    s = smtplib.SMTP(EMAIL_HOST)
    s.sendmail(from_email, to_email, msg.as_string())