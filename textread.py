from google.cloud import vision, translate, texttospeech
from google.cloud import translate
import io, os, re

import cv2
import numpy as np

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("hackthenorth-1663435360245-76d2e298297d.json")

# MAKE COORDINATES THE INPUT ONES
# coordinates = [[0.2,0.3],[0.7,0.8]]
# MAKE FILE_NAME THE INPUT IMAGE LOCATION
# file_name = os.path.abspath('gcloud/images/unknown.png')

# native_language = "en-US"

# file path
# output_path = 'gcloud/output'

# note: portugues(portugal), english(british) have the same language codes and do not need to be converted
# language_map = {"zh-CN":"zh-Hans", "zh-TW":"zh-Hant", "pt-BR":"pt"}

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
    
    # for text in texts:
    #     print(text.description)
    #     vertices = (['({},{})'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
    #     print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

print(detect_text('output/20220918_045805.jpg'))