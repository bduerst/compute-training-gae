from google.appengine.api import images
from google.appengine.api import taskqueue
from google.appengine.ext import deferred
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from Tasks import deferredImageProcessing
import webapp2
import logging

from Tasks import ImageUpload

# URL generator for file upload
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
        deferredSetting = self.request.get('deferred')

        upload = self.get_uploads()[0]
        file_info = self.get_file_infos()[0]

        logging.info("Deferred status:"+deferredSetting)
        if(deferredSetting == 'on'):
            logging.info('User requesting image processing to be deferred, sending to task queue')
            # Send the task to the defered queue so we can see it in the console
            deferred.defer(
                deferredImageProcessing,
                file_info.filename,
                upload.key(),
                _countdown=30,
                _queue="default"
            )

        else:
            # Process immediately
            image = ImageUpload(
                filename=file_info.filename,
                blob_key=upload.key()
            )
            image.renderCharacteristics()
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
    # Generates and loads a thumbnail of image for viewing
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
    # Loads the full image for viewing
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
