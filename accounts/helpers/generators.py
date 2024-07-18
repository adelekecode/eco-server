import string
import random
from rest_framework.exceptions import ValidationError
import cloudinary
import cloudinary.uploader
from django.db.models import Q
import base64
import requests
import os
def generate_password():
    a = []
    for _ in range(3):
        a.append(random.choice(string.ascii_lowercase))
        a.append(random.choice(string.ascii_uppercase))
        a.append(random.choice(string.digits))
        a.append(random.choice(["@","!","$","#","="]))
    random.shuffle(a)
    return "".join(a)


def generate_code(n):
    
    alphabet = string.ascii_letters + string.digits
    code = ''.join(random.choice(alphabet) for i in range(n))
    return code



def upload_file(raw: str) -> str:
    
    try:
        cloudinary.config(

            cloud_name=os.environ.get("CLOUD_NAME"),
            api_key=os.environ.get("API_KEY"),
            api_secret=os.environ.get("API_SECRET")
        )

        response = cloudinary.uploader.upload(raw, resource_type="auto")

        return response.get("secure_url")
    
    except Exception as e:
        raise ValidationError({"message": "Error uploading file"})