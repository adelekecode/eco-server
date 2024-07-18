import requests
import os


baseurl = os.getenv("upurl")
token = os.getenv("uptoken")










def get_image_url(image):

    r = requests.post(

    url= f"{baseurl}v1/upload/content/",

    headers = {
        "Authorization": f"Bearer {token}"
        },

    files = {
        "file": image
        }

    )

    return r.json()["url"] if r.status_code == 200 else None


