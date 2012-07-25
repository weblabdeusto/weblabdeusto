import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


EMAIL_HOST = 'mail.deusto.es'


def send_email(body_text, subject, from_email, to_email, body_html=None):

    msg = MIMEMultipart('alternative')

    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    part1 = MIMEText(body_text, 'text')
    msg.attach(part1)
    
    if body_text is not None:
        part2 = MIMEText(body_html, 'html')
        msg.attach(part2)

    
    s = smtplib.SMTP(EMAIL_HOST)
    s.sendmail(from_email, to_email, msg.as_string())