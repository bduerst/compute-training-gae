import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.ext import blobstore
from blobstore import ImageUpload

import logging


class Image(messages.Message):
    filename = messages.StringField(1)
    blob_key = messages.StringField(2)
    img_url = messages.StringField(3)
    characteristics = messages.StringField(4, repeated=True)
    date_created = messages.StringField(5)
    id = messages.IntegerField(6)


class ImageCollection(messages.Message):
    items = messages.MessageField(Image, 1, repeated=True)


class ImageKey(messages.Message):
    id = messages.StringField(1)


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
        imageQuery = ImageUpload.query().order(-ImageUpload.date_created)
        images = []
        for image in imageQuery:
            images.append(Image(
                filename=image.filename,
                blob_key=str(image.blob_key),
                img_url=image.img_url,
                characteristics=image.characteristics,
                date_created=str(image.date_created),
                id=image.key.id()
            ))
        return ImageCollection(items=images)


    # Delete an image from database
    @endpoints.method(
        ImageKey,
        ImageKey,
        path='delete',
        http_method='POST',
        name='images.delete')
    def deleteImages(self, request):
        # images = ImageUpload.query();
        id = int(request.id)
        imageKey = ImageUpload.get_by_id(id).key
        logging.info('Deleting Image with ID: '+request.id)
        imageKey.delete()
        return request


    # Get a blobstore upload url for new images
    @endpoints.method(
        message_types.VoidMessage,
        BlobstoreUploadURL,
        path='blobstore',
        http_method='GET',
        name='blobstore.getUrl')
    def getUploadUrl(self, unused_request):
        upload_url = blobstore.create_upload_url('/upload_photo')
        return BlobstoreUploadURL(url=upload_url)
