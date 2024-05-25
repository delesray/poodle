from mailjet_rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ['MAIL_API_KEY']
api_secret = os.environ['MAIL_API_SECRET_KEY']
sender_mail = os.environ['SENDER_EMAIL']
receiver_mail = os.environ['RECIPIENT_EMAIL']

mailjet = Client(auth=(api_key, api_secret), version='v3.1')

data = {
  'Messages': [
				{
						"From": {
								"Email": sender_mail,
								"Name": "Mailjet Pilot"
						},
						"To": [
								{
										"Email": receiver_mail,
										"Name": "passenger 1"
								}
						],
						"Subject": "Hello",
						"TextPart": "Dear passenger 1, welcome to Mailjet! May the delivery force be with you!",
						"HTMLPart": "<h3>Dear passenger 1, welcome to <a href=\"https://www.mailjet.com/\">Mailjet</a>!</h3><br />May the delivery force be with you!"
				}
		]
}
result = mailjet.send.create(data=data)
print(result.status_code)
print(result.json())
