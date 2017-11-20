#!/usr/bin/env python
#
# Copyright 2017 Google Inc.
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
#
import webapp2
import blobstore
import endpoints
import Api
import Tasks

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


""" Main Webapp2 Routing """
app = webapp2.WSGIApplication([
    ('/upload', blobstore.PhotoUploadFormHandler),
    ('/upload_photo', blobstore.PhotoUploadHandler),
    ('/img', blobstore.Thumbnailer),
    ('/fullimg', blobstore.ImageLoader)
], debug=True)

""" Route API requests to API """
api = endpoints.api_server([Api.ComputeTrainingApi])

