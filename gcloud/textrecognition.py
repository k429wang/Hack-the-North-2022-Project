from google.cloud import vision, translate, texttospeech
from google.cloud import translate
import io, os, re

import cv2
import numpy as np

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("gcloud/hackthenorth-1663435360245-76d2e298297d.json")

# MAKE COORDINATES THE INPUT ONES
coordinates = [[0.2,0.3],[0.7,0.8]]
# MAKE FILE_NAME THE INPUT IMAGE LOCATION
file_name = os.path.abspath('gcloud/images/unknown.png')

native_language = "en-US"

# file path
output_path = 'gcloud/output'

# note: portugues(portugal), english(british) have the same language codes and do not need to be converted
language_map = {"zh-CN":"zh-Hans", "zh-TW":"zh-Hant", "pt-BR":"pt"}

def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient(credentials=credentials)

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    text = texts[0]
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

def detect_language(text):
    """Detects the text's language."""
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client(credentials=credentials)

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.detect_language(text)
    return(result["language"])

def translate_text(text, language, native):
    credentials = service_account.Credentials.from_service_account_file("gcloud\hackthenorth-1663435360245-76d2e298297d.json")

    client = translate.TranslationServiceClient(credentials=credentials)
    location = "global"
    parent = f"projects/hackthenorth-1663435360245/locations/{location}"

    if language == "en":
        return(text)

    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": language,
            "target_language_code": native,
        }
    )

    for translation in response.translations:
        return(translation.translated_text)

def tts(text, output_path): 
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    path = os.path.join(output_path , 'output.mp3')
    # The response's audio_content is binary.
    with open(path, "wb") as out:
        # Write the response to the output file.
        
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')

def crop(img, x1, y1, x2, y2, output_path):
    img = cv2.imread(img)
    cropped = img[x1:x2, y1:y2]
    cv2.imwrite(os.path.join(output_path , 'croppedimage.jpg'), cropped)

# crop(file_name, int(coordinates[0][0]*1280-50), int(coordinates[0][1]*720)-50, int(coordinates[1][0]*1280+50), int(coordinates[1][1]*720)+50, output_path)

# read_image = detect_text("gcloud/output/croppedimage.jpg")
# read_language = detect_language(read_image)

# # check if language is consistent and needs to be remapped
# if read_language in language_map.keys():
#     read_language = language_map[read_language]

# translated = translate_text(read_image, read_language, native_language)

# print(f"Read text: \n{read_image}")
# print(f"Language: {read_language}")
# print(f"Translated text:\n{translated}")
# tts(translated, output_path)