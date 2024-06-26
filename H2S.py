import requests
from bs4 import BeautifulSoup
import re
import smtplib
import schedule
import time
from twilio.rest import Client

# your rent budget, the highest price you can afford
BUDGET = 900

# the target url needed for search, for example, I want to find a fully-furnished apartment in Eindhoven which is available to book directly, I would change the url into this:
url = 'https://holland2stay.com/residences.html?&available_to_book=179&city=29&finishing=70'

# the price div we need to search for
price_class = 'regi-price'

# alert through email
def email_alert(message):
    sender_email = "your-email@google.com"
    receiver_email = "can-also-be-your-email@google.com"
    password = "email-password"
    smtp_server = "smtp.google.com"
    port = 587

    server = smtplib.SMTP(smtp_server, port)
    server.connect(smtp_server, port)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
    server.quit()

# alert through text
def text_alert(message):
    # through twilio
    account_sid = 'your-account-sid'
    auth_token = 'your-auth-token'
    from_number = 'your-twilio-number'
    to_number = 'your-own-number'

    client = Client(account_sid, auth_token)
    message = client.messages \
            .create(
                    body=message,
                    from_=from_number,
                    to=to_number
                )

# to make sure when to stop
found = False

def job():
    # make a new one for multiple websites.
    # that runs in paralel and sends the message
    # bonus if the message can tell which website it founds.
    # More Bonuses if the message will send the found property
    # Saving 40euro!
    
    # get the information of website
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # search for the price div
    price_elements = soup.find_all('div', {'class': price_class})

    price_list = []

    for price_element in price_elements:
        price = price_element.text.strip()
        if price:
            price = int(re.sub(',', '', re.findall('[\d,]+', price)[0]))
            if price < BUDGET:
                price_list.append(price)
                print('Find a new price:', price, '!')

    if price_list == [] : pass
    else:
        # state that 'found' is global, or else there's gonna be a local new one
        global found 
        # terminate the script
        found = True

        subject = 'New House Alert!'
        body = ''
        for p in price_list:
            body += 'The price is' + str(p) + "\n"
            
        body += 'Click the url:' + url + "\n"
        message = f"Subject: {subject}\n\n{body}"
        message = message.encode('utf-8')  

        email_alert(message)
        # text_alert(message)

# Run every 10 seconds
schedule.every(10).seconds.do(job)

while not found:
    schedule.run_pending()
    time.sleep(1)
