from flask_mail import Message
from . import mail
from flask import render_template, current_app

def send_email(to, subject, template, **kwargs):
    msg = Message(subject,
                  recipients=[to],
                  sender=current_app.config['MAIL_DEFAULT_SENDER'])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_token()
    send_email(to=user.email,
               subject='Reset Your Password',
               template='email/reset_password',
               user=user,
               token=token)

def send_email_confirmation(user):
    token = user.get_reset_token()
    send_email(to=user.email,
               subject='Confirm Your Email',
               template='email/confirm_email',
               user=user,
               token=token)