import base64
import logging
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'


class VisionApi(object):
    def __init__(self):
        self.vision = self._create_client()

    def _create_client(self):
        credentials = GoogleCredentials.get_application_default()
        return discovery.build(
            'vision', 'v1', credentials=credentials,
            discoveryServiceUrl=DISCOVERY_URL)

    def detect_labels(self, images, max_results=10, num_retries=3):
        """Uses the Vision API to detect text in the given file.
        """

        batch_request = []

        for image in images:
            batch_request.append({
                'image': {
                    'content': base64.b64encode(image).decode('UTF-8')
                },
                'features': [{
                    'type': 'LABEL_DETECTION',
                    'maxResults': max_results,
                }]
            })

        request = self.vision.images().annotate(
            body={'requests': batch_request})

        response = request.execute(num_retries=num_retries)

        label_responses = []

        for r in response['responses']:
            labels = [
                x['description'] for x in r.get('labelAnnotations', [])]

            label_responses.append(labels)

        return label_responses
