from google.cloud import translate

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("hackthenorth-1663435360245-76d2e298297d.json")

def translate_text(text, language):

    client = translate.TranslationServiceClient(credentials=credentials)
    location = "global"
    parent = f"projects/hackthenorth-1663435360245/locations/{location}"

    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": language,
            "target_language_code": "en-US",
        }
    )

    for translation in response.translations:
        return(translation.translated_text)
language = "th"
print(translate_text("หัวรับนําดับเพลิง", language))
