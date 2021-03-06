import twilio
from twilio.rest import TwilioRestClient
import os


def send_message(phone, info):
    ''' Accepts message and phone number, sends text through twilio'''

    try:
        #retrieves appropriate secret keys
        consumer_key = os.environ.get("ACCOUNT_SID")
        consumer_token = os.environ.get("AUTH_TOKEN")

        account_sid = consumer_key
        auth_token = consumer_token
        client = TwilioRestClient(account_sid, auth_token)

        message = client.messages.create(to=phone, from_="+14159916333",
                                         body=info)

    except twilio.TwilioRestException as e:
        print e
        return False

    return True
