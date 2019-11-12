import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail

def save_picture(form_picture):
    r_hex = secrets.token_hex(8)
    _, ext_name = os.path.splitext(form_picture.filename)
    filename = r_hex + ext_name
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', filename)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return filename

def send_reset_email(user):
    token = user.get_reset_token(expires_sec=600)
    message = Message(subject='Password Reset Request',
                        sender='noreply@demo.com',
                        recipients=[user.email])
    message.body = f'''To reset your password, visit the following link:
{url_for('users.reset_password', token=token, _external=True)}

If you did not make this request then simply ignory this email and no changes will be made.
'''
    mail.send(message)