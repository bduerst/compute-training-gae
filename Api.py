import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.ext import blobstore
from blobstore import ImageUpload


class Image(messages.Message):
    filename = messages.StringField(1)
    blob_key = messages.StringField(2)
    img_url = messages.StringField(3)
    characteristics = messages.StringField(4, repeated=True)
    date_created = messages.StringField(5)


class ImageCollection(messages.Message):
    items = messages.MessageField(Image, 1, repeated=True)


STORED_IMAGES = ImageCollection(items=[
    Image(filename='hello world!'),
    Image(filename='goodbye world!'),
])


class BlobstoreUploadURL(messages.Message):
    url = messages.StringField(1)


@endpoints.api(name="computeTraining",
               version="v1")  # , description="dev_items", allowed_client_ids=CLIENT_ID_WHITELIST)
class ComputeTrainingApi(remote.Service):
    """
    API for client calls to see images
    """

    # Get the list of Images uploaded for display
    @endpoints.method(
        message_types.VoidMessage,
        ImageCollection,
        path='images',
        http_method='GET',
        name='images.list')
    def listImages(self, unused_request):
        # images = ImageUpload.query();
        imageQuery = ImageUpload.query()
        images = []
        for image in imageQuery:
            images.append(Image(
                filename=image.filename,
                blob_key=str(image.blob_key),
                img_url=image.img_url,
                characteristics=image.characteristics,
                date_created=str(image.date_created)
            ))
        return ImageCollection(items=images)

    # Get the list of Images uploaded for display
    @endpoints.method(
        message_types.VoidMessage,
        BlobstoreUploadURL,
        path='blobstore',
        http_method='GET',
        name='blobstore.getUrl')
    def getUploadUrl(self, unused_request):
        upload_url = blobstore.create_upload_url('/upload_photo')
        return BlobstoreUploadURL(url=upload_url)
