from google.cloud import vision, translate
import io, os

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("gcloud\hackthenorth-1663435360245-76d2e298297d.json")

# file path
file_name = os.path.abspath('gcloud/images/chinese.jpg')

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

    # vertices = (['({},{})'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
    # print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))


def translate_text(text="Hello, world!", project_id="hackthenorth-1663435360245"):

    client = translate.TranslationServiceClient(credentials=credentials)
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"

    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": "zh-Hans",
            "target_language_code": "en-US",
        }
    )

    for translation in response.translations:
        print("Translated text: {}".format(translation.translated_text))

print(detect_text(file_name))
translate_text(detect_text(file_name))