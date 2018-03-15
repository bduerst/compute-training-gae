import webapp2
import blobstore
import endpoints
import Api
import Tasks

""" Main Webapp2 Routing """
app = webapp2.WSGIApplication([
    ('/upload', blobstore.PhotoUploadFormHandler),
    ('/upload_photo', blobstore.PhotoUploadHandler),
    ('/img', blobstore.Thumbnailer),
    ('/fullimg', blobstore.ImageLoader)
], debug=True)

""" Route API requests to API """
api = endpoints.api_server([Api.ComputeTrainingApi])

