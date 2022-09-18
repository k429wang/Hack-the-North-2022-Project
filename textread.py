from google.cloud import vision, translate, texttospeech
from google.cloud import translate
import io, os, re

import cv2
import numpy as np

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("hackthenorth-1663435360245-76d2e298297d.json")

def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient(credentials=credentials)

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    try: 
        text = texts[0]
    except:
        return('No text found, try again')
    return(text.description)

print(detect_text('output/20220918_045805.jpg'))