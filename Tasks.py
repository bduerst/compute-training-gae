from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images

from vision import VisionApi


# Simple datastore model for uploads
class ImageUpload(ndb.Model):
    filename = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()
    img_url = ndb.StringProperty()
    characteristics = ndb.StringProperty(repeated=True)
    date_created = ndb.DateTimeProperty(auto_now_add=True)

    def _pre_put_hook(self):
        self.img_url = '/img?blob_key=' + str(self.blob_key)

    def renderCharacteristics(self):
        blob_info = blobstore.get(self.blob_key)
        if blob_info:
            img = images.Image(blob_key=self.blob_key)
            img.im_feeling_lucky()
            vision = VisionApi()
            response = vision.detect_labels([img.execute_transforms(output_encoding=images.JPEG)])[0]
            self.characteristics = response


# Deferrable Task for Task Queue
def deferredImageProcessing(filename, blob_key):
    image = ImageUpload(
        filename=filename,
        blob_key=blob_key
    )
    image.renderCharacteristics()
    image.put()
