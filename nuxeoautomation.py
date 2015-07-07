# -*- coding: utf8 -*-
from __future__ import unicode_literals
import urllib2, base64, sys, time, os
import logging
import json
import mimetypes, random
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
   

'''
Attach blob method modified by acordier@univ-lille2 10/10/2013
'''

class Client(object):
    def __init__(self, root):
        self.root = root

    def getSession(self, login, password):
        return Session(self.root, login, password)
    
class Session(object):
    def __init__(self, root, login, passwd):
        self.root = root
        self.login = login
        self.passwd = passwd
        self.auth = 'Basic %s' % base64.b64encode(
                self.login + ":" + self.passwd).strip()

        cookie_processor = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener(cookie_processor)
        self.logger = logging.getLogger('nxpush')
        self.fetchAPI()
        
    def fetchAPI(self):
        headers = {
            "Authorization": self.auth,
        }
        req = urllib2.Request(self.root, headers=headers)              
        response = json.loads(self.opener.open(req).read())
        self.operations = {}
        for operation in response["operations"]:
            self.operations[operation['id']] = operation

    # Document category

    def create(self, ref, type, name=None, properties=None):
        return self._execute("Document.Create", input="doc:"+ref,
            type=type, name=name, properties=properties)

    def update(self, ref, properties=None):
        return self._execute("Document.Update", input="doc:"+ref,
            properties=properties)

    def setProperty(self, ref, xpath, value):
        return self._execute("Document.SetProperty", input="doc:"+ref,
            xpath=xpath, value=value)

    def delete(self, ref):
        return self._execute("Document.Delete", input="doc:"+ref)

    def getChildren(self, ref):
        return self._execute("Document.GetChildren", input="doc:"+ref)

    def getParent(self, ref):
        return self._execute("Document.GetParent", input="doc:"+ref)

    def lock(self, ref):
        return self._execute("Document.Lock", input="doc:"+ref)

    def unlock(self, ref):
        return self._execute("Document.Unlock", input="doc:"+ref)

    def move(self, ref, target, name=None):
        return self._execute("Document.Move", input="doc:"+ref,
            target=target, name=name)

    def copy(self, ref, target, name=None):
        return self._execute("Document.Copy", input="doc:"+ref,
            target=target, name=name)

    # These ones are special: no 'input' parameter
    def fetch(self, ref):
        return self._execute("Document.Fetch", value=ref)

    def query(self, query, language=None):
        return self._execute("Document.Query", query=query, language=language)

    # Blob category

    def getBlob(self, ref):
        return self._execute("Blob.Get", input="doc:"+ref)

    # Special case. Yuck:(
    def attachBlob(self, ref, blob, ext):
        return self._attach_blob(blob, document=ref, extension=ext)

# generic function to execute operations on nuxeo (source : nuxeo documentation)

    # Private
    def _execute(self, command, input=None, **params):
        self._checkParams(command, input, params)
        headers = {
            "Content-Type": "application/json+nxrequest",
            "Authorization": self.auth}
        d = {}
        if params:
            d['params'] = {}
            for k, v in params.items():
                if v == None:
                    continue
                if k == 'properties':
                    s = ""
                    for propname, propvalue in v.items():
                        s += "%s=%s\n" % (propname, propvalue)
                    d['params'][k] = s.strip()
                else:
                    d['params'][k] = v
        if input:
            d['input'] = input
        if d:
            data = json.dumps(d)
        else:
            data = None
        req = urllib2.Request(self.root + command, data, headers)
        try:
            resp = self.opener.open(req)
        except Exception, e:
            self._handle_error(e)
            raise
        
        info = resp.info()
        s = resp.read()
        if info.has_key('content-type') and \
                info['content-type'].startswith("application/json"):
            if s:
                return json.loads(s)
            else:
                return None
        else:
            return s

    def _attach_blob(self, blob, **params):
        ref = params['document']
        filename = os.path.basename(ref)
        self.logger.debug(filename)
        
        if params['extension']:
            extension = params['extension']

        container = MIMEMultipart("related",
                type="application/json+nxrequest",
                start="request")

        d = {'params': params}
        json_data = json.dumps(d)
        json_part = MIMEBase("application", "json+nxrequest")
        json_part.add_header("Content-ID", "request")
        json_part.set_payload(json_data)
        container.attach(json_part)

        if filename[filename.rfind('.'):]!=extension:
            filename += extension
 
        ctype, encoding = mimetypes.guess_type(filename)

        if ctype:
            maintype, subtype = ctype.split('/', 1)
        else:
            maintype, subtype = "application", "binary"

        blob_part = MIMEBase(maintype, subtype)
        blob_part.add_header("Content-ID", "input")
        blob_part.add_header("Content-Transfer-Encoding", "base64")
        blob_part.add_header("Content-Disposition",
            "attachment;filename=%s" % filename)

        try:
            self.logger.debug('session: setting payload')
            blob_part.set_payload(blob)
            self.logger.debug('session: container blob')
            container.attach(blob_part)
        except Exception, e:
            self._handle_error(e)
            raise        
       
        # Create data by hand :(
        boundary = "====Part=%s=%s===" % (time.time, random.randint(0, 1000000000))
        headers = {
                "Accept": "application/json+nxentity, */*",
                "Authorization": self.auth,
                "Content-Type": 'multipart/related;boundary="%s";type="application/json+nxrequest";start="request"'
                    % boundary,
        }
        try:
      
            data = "--" + boundary + "\r\n" \
                + json_part.as_string() + "\r\n" \
                + "--" + boundary + "\r\n" \
                + blob_part.as_string() + "\r\n" \
                + "--" + boundary + "--"
           
        except Exception, e:
            self._handle_error(e)
            raise
        

        req = urllib2.Request(self.root + "Blob.Attach", data, headers)

        try:
     
            resp = self.opener.open(req)
        except Exception, e:
            self._handle_error(e)
            raise

        s = resp.read()
        
        return s
        
    def _checkParams(self, command, input, params):
        method = self.operations[command]
        required_params = []
        other_params = []
        for param in method['params']:
            if param['required']:
                required_params.append(param['name'])
            else:
                other_params.append(param['name'])
        for param in params.keys():
            if not param in required_params \
                and not param in other_params:
                raise Exception("Bad param: %s" % param)
        for param in required_params:
            if not param in params.keys():
                raise Exception("Missing param: %s" % param)
        # TODO: add typechecking
    
    def _handle_error(self, e):
        self.logger.error(e)
        if hasattr(e, "fp"):
            detail = e.fp.read()
            try:
                exc = json.loads(detail)
                self.logger.error(exc['message'])
                self.logger.error(exc['stack'])
            except:
                # Error message should always be a JSON message, but sometimes it's not
                self.logger.error(detail)

