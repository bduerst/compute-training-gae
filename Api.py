# Copyright 2017 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


class LogMessage(messages.Message):
    message = messages.StringField(1)
    level = messages.IntegerField(2)


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
        logging.debug('Deleting Image with ID: '+request.id)
        blob = blobstore.get(imageKey.get().blob_key)
        blob.delete()
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


    # Pass a logging message through to the logger
    @endpoints.method(
        LogMessage,
        LogMessage,
        path='logging',
        http_method='POST',
        name='logging.put')
    def logMessage(self, request):
        message = request.message
        level = request.level
        if(level == 0):
            logging.critical(message)
        elif(level == 1):
            logging.error(message)
        elif(level == 2):
            logging.warning(message)
        elif(level == 3):
            logging.info(message)
        else:
            logging.info("Couldn't read the logging level.  Message is:")
            logging.info(message)
        return request
