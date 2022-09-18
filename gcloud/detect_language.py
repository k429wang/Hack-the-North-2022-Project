from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("gcloud\hackthenorth-1663435360245-76d2e298297d.json")

def detect_language(text):
    """Detects the text's language."""
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client(credentials=credentials)

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.detect_language(text)
    print("Language: {}".format(result["language"]))

detect_language("Hello world")