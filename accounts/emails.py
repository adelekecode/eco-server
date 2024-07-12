import os
import requests



key = 'sk_26de7a9edc831dabcb28b17ae9615f21ed518d5938e3a966'


def auth_otp(email, otp):
 
    requests.post(
        "https://api.useplunk.com/v1/track",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}" 
        },
        json={
            "event": 'otp_auth',
            "email": email,
            "data": {
                "code": otp,
                }
            }
    )



