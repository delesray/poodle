from mailjet_rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ['MAIL_API_KEY']
api_secret = os.environ['MAIL_API_SECRET_KEY']
sender_mail = os.environ['SENDER_EMAIL']

mailjet = Client(auth=(api_key, api_secret), version='v3.1')


async def build_student_enroll_request(receiver_mail, student_email, sender_mail=sender_mail):
    return {
        'Messages': [
            {
                "From": {
                    "Email": sender_mail,
                    "Name": "Poodle e-learning platform"
                },
                "To": [
                    {
                        "Email": receiver_mail
                    }
                ],
                "Subject": "Student enroll request",
                "TextPart": f"Student {student_email} has requested access to your course. Please click here for approval",
                "HTMLPart": f"<h3>Student {student_email} has requested access to your course. Please click <a href=\"https://www.mailjet.com/\">here</a> for approval</h3><br />"
            }
        ]
    }


async def send_email(data):
    mailjet.send.create(data)
