import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from creds import *
import requests
from pprint import pprint
import json
from datetime import date, timedelta
import time

def getJSON(link, parameters=None):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"}
    req = requests.get(link, headers=headers, params=parameters)
    return req.json()


def make_id():
    link = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    states = getJSON(link)['states']
    data = {}
    for state in states:
        link = f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state['state_id']}"
        districts = getJSON(link)['districts']
        data[state['state_name']] = {}
        for district in districts:
            data[state['state_name']][district['district_name']
                                      ] = district['district_id']

    pprint(data)
    # with open("districts.json", "w") as f:
    #     json.dump(data, f)


def send_mail(receiver_address, mail_content, subject):
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    # login with mail_id and password
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')


def find_vac(district_id):
    link = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    today = date.today()
    centers = []
    for i in range(4):
        day = (today+timedelta(days=7*i)).strftime("%d-%m-%Y")
        print(day)
        parameters = {"district_id": district_id, "date": day}
        data = getJSON(link, parameters)
        for center in data['centers']:
            for session in center['sessions']:
                if session['available_capacity'] > 0 and session['min_age_limit'] == 18:
                    centers.append(center)
    pprint(centers)
    return centers


def driver():
    for receiver in receivers:
        centers = []
        for dist in receiver['dist_ids']:
            center = find_vac(dist)
            if len(center) == 0:
                continue
            centers.extend(center)
        if len(centers) == 0:
            continue
        subject = "VACCINE SLOTS FOUND NEAR YOU"
        msg = "VACCINE SLOTS FOUND\n\n\n\n"
        for center in centers:
            msg += f"ADDRESS: \n{center['name']},\n{center['address']}, {center['district_name']},\n{center['state_name']}, \n{center['pincode']}\nFEES: {center['fee_type']}\n\n"
            for session in center['sessions']:
                if session['available_capacity'] > 0:
                    msg += f"DATE: {session['date']} \nAVAILABILITY: {session['available_capacity']} \nVACCINE: {session['vaccine']}\n"
            msg += "************************************************\n\n"
        print(msg)
        send_mail(receiver['email'], mail_content=msg, subject=subject)


if __name__ == "__main__":
    while True:
        driver()
        time.sleep(900)