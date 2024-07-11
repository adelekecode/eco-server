import os
import requests



key = 'sk_5ba9a3ae97708617c4ee42f25d72320d4cc5f67ccc8bec6a'


def auth_otp(email, otp):
 
    requests.post(
        "https://api.useplunk.com/v1/track",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}" 
        },
        json={
            "event": 'auth',
            "email": email,
            "data": {
                "otp": otp,
                }
            }
    )



