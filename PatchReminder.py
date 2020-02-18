# created by vioswift.com
import smtplib
import configparser
import codecs
from datetime import datetime
import calendar
import sched
import time

# day and month names
month_name = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# get ini config file
config = configparser.ConfigParser()
config.read('PatchReminder.ini')

calendar = calendar.Calendar()
today = datetime.now() # get todays current date and time

# replace parts of the text passed 
def replace_text(text, section):
    temp_text = text
    for each_section in config.sections():
        if each_section == section:
            for (each_key, each_val) in config.items(each_section):
                if each_key.startswith('$'):
                    temp_text = temp_text.replace(each_key, each_val)
                if each_key.startswith('@'):
                    temp_text = temp_text.replace(each_key, today.strftime(each_val))
    return temp_text

def replace_values_text(text, section, values):
    temp_text = text
    for each_section in config.sections():
        if each_section == section:
            for (each_key, each_val), value in zip(config.items(each_section), values):
                if each_key.startswith('%'):
                    temp_text = temp_text.replace(each_key, value.strftime("%d/%m/%Y"))
    return temp_text

# sends the email
def sendEmail():
    with smtplib.SMTP(smtp_Server, port) as server:
        server.login(username, password)
        server.sendmail(sender, receiver, message)
        server.quit()

def getMonthNumber(month):
    return month_name.index(month) + 1

def findDayName(date): 
    day = datetime.strptime(date, '%d %m %Y').weekday() 
    return (day_name[day])

def getCommaValues(section):
    values = []
    for each_section in config.sections():
        if each_section == section:
            for (each_key, each_val) in config.items(each_section):
                if each_key.startswith('%'):
                    values.append(each_val.split(","))
    return values

def getPatchDates():
    patch_dates_temp = []
    for reminder in getCommaValues('reminders'):
        certain_days_in_month = []
        month_to_email = today.month if reminder[0].lower() == 'every' else getMonthNumber(reminder[0].lower().title())
        day_to_email = reminder[2].lower()

        # gets all day number in the selected month
        for day in calendar.itermonthdays(today.year, month_to_email):
            date = f"""{day} {month_to_email} {today.year}"""
            if day != 0:
                if findDayName(date).lower() == day_to_email:
                    certain_days_in_month.append(day)

        patch_dates_temp.append(datetime(today.year, month_to_email, certain_days_in_month[int(reminder[1]) - 1]))
    return patch_dates_temp

# get patch dates
patch_dates = getPatchDates()

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
    subject = replace_text(subject, 'message_details')
    message_text = config.get('message_details', 'message_text')
    message_text = replace_text(message_text, 'message_details')
else:
    subject = config.get('message_template_file', 'subject')
    subject = replace_text(subject, 'message_template_file')
    file_path = config.get('message_template_file', 'file_path')
    file_data = codecs.open(file_path, 'r')
    message_text = replace_text(file_data.read(), 'message_template_file')
    message_text = replace_values_text(message_text, 'reminders', patch_dates)
    file_data.close()

message = f"""\
MIME-Version: 1.0
Content-type: text/html
Subject: {subject}
To: {receiver}
From: {sender}

{message_text}"""


for patch_date in patch_dates:
    if patch_date.date() == today.date():
        sendEmail()


