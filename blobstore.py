# Copyright 2015 Google Inc. All rights reserved.
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


from google.appengine.api import images

from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
import webapp2

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

        blob_info = blobstore.get(self.blob_key)
        if blob_info:
            img = images.Image(blob_key=self.blob_key)
            img.im_feeling_lucky()
            vision = VisionApi()
            response = vision.detect_labels([img.execute_transforms(output_encoding=images.JPEG)])[0]
            self.characteristics = response


class PhotoUploadFormHandler(webapp2.RequestHandler):
    def get(self):

        upload_url = blobstore.create_upload_url('/upload_photo')
        self.response.out.write("""
<html><body>
<form action="{0}" method="POST" enctype="multipart/form-data">
  Upload File: <input type="file" name="file"><br>
  <input type="submit" name="submit" value="Submit">
</form>
</body></html>""".format(upload_url))


class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        #try:
        upload = self.get_uploads()[0]
        file_info = self.get_file_infos()[0]

        image = ImageUpload(
            filename=file_info.filename,
            blob_key=upload.key())
        image.put()

        self.redirect('/')

        #except:
        #self.error(500)


class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)


class Thumbnailer(webapp2.RequestHandler):
    def get(self):
        blob_key = self.request.get("blob_key")
        if blob_key:
            blob_info = blobstore.get(blob_key)

            if blob_info:
                img = images.Image(blob_key=blob_key)
                img.resize(width=320, height=320,crop_to_fit=True)
                img.im_feeling_lucky()
                thumbnail = img.execute_transforms(output_encoding=images.JPEG)

                self.response.headers['Content-Type'] = 'image/jpeg'
                self.response.out.write(thumbnail)
                return

        self.error(404)

class ImageLoader(webapp2.RequestHandler):
    def get(self):
        blob_key = self.request.get("blob_key")
        if blob_key:
            blob_info = blobstore.get(blob_key)

            if blob_info:
                img = images.Image(blob_key=blob_key)
                img.im_feeling_lucky()
                fullImage = img.execute_transforms(output_encoding=images.JPEG)

                self.response.headers['Content-Type'] = 'image/jpeg'
                self.response.out.write(fullImage)
                return

        self.error(404)
