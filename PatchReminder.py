import smtplib
import configparser
import codecs
from datetime import datetime
import calendar
import sched
import time

# get ini config file
config = configparser.ConfigParser()
config.read('PatchReminder.ini')

# get todays current date and time
today = datetime.now()

# replace parts of the text passed 
def replace_text(text):
    temp_text = text
    for each_section in config.sections():
        if each_section == 'message_template_file':
            for (each_key, each_val) in config.items(each_section):
                if each_key.startswith('$'):
                    temp_text = temp_text.replace(each_key, each_val)
                if each_key.startswith('@'):
                    temp_text = temp_text.replace(each_key, today.strftime(each_val))
    return temp_text

# settings
use_message_template_file = config.getboolean('settings', 'use_message_template_file')

# mail server
smtp_Server = config.get('mail_server', 'smtp_Server')
port = config.getint('mail_server', 'port')

# login credentials
username = config.get('email', 'username')
password = config.get('email', 'password')

# sender 
sender_name = config.get('email', 'sender_name')
sender_email = config.get('email', 'sender_email')
sender = sender_name + " <" + sender_email + ">"

# receiver 
receiver_name = config.get('email', 'receiver_name')
receiver_email = config.get('email', 'receiver_email')
receiver = receiver_name + " <" + receiver_email + ">"

# message
subject = config.get('message_details', 'subject')

if not use_message_template_file:
    subject = config.get('message_details', 'subject')
    subject = replace_text(subject)
    message_text = config.get('message_details', 'message_text')
    message_text = replace_text(message_text)
else:
    subject = config.get('message_template_file', 'subject')
    subject = replace_text(subject)
    file_path = config.get('message_template_file', 'file_path')
    file_data = codecs.open(file_path, 'r')
    message_text = replace_text(file_data.read())
    file_data.close()

message = f"""\
MIME-Version: 1.0
Content-type: text/html
Subject: {subject}
To: {receiver}
From: {sender}

{message_text}"""

with smtplib.SMTP(smtp_Server, port) as server:
    server.login(username, password)
    server.sendmail(sender, receiver, message)
    server.quit()