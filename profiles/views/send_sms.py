import os
from twilio.rest import Client
import environ





def send_sms(phone_number, name):
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    print("o numero do telefone do casaninha que vai receber o sms é ", phone_number)
    env = environ.Env()

    environ.Env.read_env()
    
    

    account_sid = env('ACCOUNT_SID')
    auth_token = env('AUTH_TOKEN')
    print('account_sid', account_sid)
    print('AUTH_TOKEN', auth_token)
    client = Client(account_sid, auth_token)
    
    message = client.messages \
                    .create(
                         body="Welcome " + name + " to Nanny Kid Playdate APP. Join us in this exciting journey of fun-filled playdates and meaningful interactions.",
                         from_='+18669525815',
                         to=phone_number
                     )
    
    print(message.sid)