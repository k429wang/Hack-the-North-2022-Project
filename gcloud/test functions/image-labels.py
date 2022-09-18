import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("gcloud\hackthenorth-1663435360245-76d2e298297d.json")

# Instantiates a client
client = vision.ImageAnnotatorClient(credentials=credentials)

# The name of the image file to annotate
file_name = os.path.abspath('gcloud/images/readme.jpeg')

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Performs label detection on the image file
response = client.label_detection(image=image)
labels = response.label_annotations

print('Labels:')
for label in labels:
    print(label.description)