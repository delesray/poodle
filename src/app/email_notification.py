from mailjet_rest import Client
import os


def email_vars_setup():
    api_key = os.getenv('MAIL_API_KEY')
    api_secret = os.getenv('MAIL_API_SECRET_KEY')
    sender_mail = os.getenv('SENDER_EMAIL')

    return api_key, api_secret, sender_mail


api_key, api_secret, send_email = email_vars_setup()
mailjet = Client(auth=(api_key, api_secret), version='v3.1')


async def build_student_enroll_request(receiver_mail: str, 
                                       student_email: str, 
                                       course_title: str, 
                                       course_id: int, 
                                       sender_mail: str=sender_mail):
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
                "TextPart": f"Student {student_email} has requested access to your {course_title} course with ID {course_id}. Click here to be redirected to Poodle, then click on the Authorize button to login, navigate to Approve Enrollment and follow the steps for approval.",
                "HTMLPart": f"<h3>Student {student_email} has requested access to your {course_title} course with ID {course_id}. Click <a href=\"http://127.0.0.1:8000/docs#/\">here</a> to be redirected to Poodle, then click on the Authorize button to login, navigate to Approve Enrollment and follow the steps for approval.</h3><br />"
            }
        ]
    }


async def build_teacher_enroll_request(receiver_mail: str, 
                                       course_title: str, 
                                       response: bool,
                                       sender_mail: str=sender_mail):
    
    response_str = 'granted' if response else 'denied'

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
                "TextPart": f"Your request to enroll in course {course_title} has been {response_str}. Click here to be redirected to Poodle.",
                "HTMLPart": f"<h3>Your request to enroll in course {course_title} has been {response_str}. Click <a href=\"http://127.0.0.1:8000/docs#/\">here</a> to be redirected to Poodle.</h3><br />"
            }
        ]
    }


async def send_email(data):
    mailjet.send.create(data)
