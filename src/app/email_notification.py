from mailjet_rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ['MAIL_API_KEY']
api_secret = os.environ['MAIL_API_SECRET_KEY']
sender_mail = os.environ['SENDER_EMAIL']

mailjet = Client(auth=(api_key, api_secret), version='v3.1')


async def build_student_enroll_request(receiver_mail: str, student_email: str, course_title: str, course_id: int, sender_mail: str=sender_mail):
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
                "TextPart": f"Student {student_email} has requested access to your {course_title} course with ID {course_id}. Please click here to login and then here for approval",
                "HTMLPart": f"<h3>Student {student_email} has requested access to your course. Please click <a href=\"http://127.0.0.1:8000/docs#/\">here</a>, then click on the Authorize button to login and navigate to Approve Enrollment to input the student's email and the course ID for approval</h3><br />"
            }
        ]
    }


async def send_email(data):
    mailjet.send.create(data)
