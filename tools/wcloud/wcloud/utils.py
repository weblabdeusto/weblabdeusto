import sys
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


DEFAULT_EMAIL_HOST = 'mail.deusto.es'
EMAILS_SENT = []

def send_email(app, body_text, subject, from_email, to_email, body_html=None):
    email_host = app.config.get('EMAIL_HOST', DEFAULT_EMAIL_HOST)

    if app.config.get('TESTING', False) or app.config.get('DEBUG', False):
        print "Faking request (%s, %s)" %( app.config.get('TESTING', False), app.config.get('DEBUG', False))
        sys.stdout.flush()
        EMAILS_SENT.append(body_html)
    else:
        print "Sending mail using %s" % email_host
        msg = MIMEMultipart('alternative')

        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        part1 = MIMEText(body_text, 'text')
        msg.attach(part1)
        
        if body_text is not None:
            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)

        
        s = smtplib.SMTP(email_host)
        s.sendmail(from_email, (to_email, from_email), msg.as_string())
        print "Mail sent using %s" % email_host
        sys.stdout.flush()
