import urllib
import webapp2
from google.appengine.ext import blobstore,db
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import blobstore_handlers 

class FileRecord(db.Model):
  blob = blobstore.BlobReferenceProperty()
  
class MainHandler(webapp2.RequestHandler):
  def get(self):
    respond = self.response.out.write
    upload_url = blobstore.create_upload_url('/upload')
    page = '<html><body>'
    files = FileRecord.all()
    if files.count():
      page += '<table border="0">'
      for record in files:
        date = str(record.blob.creation)
        key = record.key().id()
        filename = record.blob.filename
        size = str(round(float(record.blob.size) / 1024 / 1024,3)) + ' Mb'
        page += '<tr><td>%s</td><td>%s</td><td><a href="/get/%s">' % (date,size,key)
        page += '%s</a></td><td><a href="/delete/%s">' % (filename,key)
        page += 'Delete</a></td></tr>' 
      page += '</table><br>'
    page += '<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url
    page += """Upload File: <input type="file" name="file"><br> <input type="submit" name="submit" 
    value="Submit"></form></body></html>"""
    respond(page)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    blob_info = self.get_uploads('file')[0]  # 'file' is file upload field in the form
    record = FileRecord(blob = blob_info)
    record.put()
    self.redirect('/')

class GetHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, blob_key):
    blob_key = str(urllib.unquote(blob_key))
    record = FileRecord.get_by_id(int(blob_key))
#    blob_info = blobstore.BlobInfo.get(record.blob.key()))
    self.send_blob(record.blob,save_as=record.blob.filename)
    
class DeleteHandler(webapp2.RequestHandler):
  def get(self,blob_key):
    try:
      blob_key = urllib.unquote(blob_key)
      record = FileRecord.get_by_id(int(blob_key))
      
      record.blob.delete()
      record.delete()
    except:
      self.error(404)
    self.redirect('/')

app = webapp2.WSGIApplication(
          [('/', MainHandler),
           ('/upload', UploadHandler),
           ('/delete/([^/]+)?', DeleteHandler),
           ('/get/([^/]+)?', GetHandler),
          ], debug=False)