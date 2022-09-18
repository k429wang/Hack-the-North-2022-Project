from google.cloud import translate

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("gcloud\hackthenorth-1663435360245-76d2e298297d.json")

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


translate_text()
