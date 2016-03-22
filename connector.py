#-*- coding: utf-8 -*-
'''
Created on 27 sept. 2013

@author: acordier
upload file from file system to nuxeo repo
'''
from __future__ import unicode_literals
from nuxeoautomation import Session
from fileutils import FileUtils
import logging
import codecs  
from io import open
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class NxConnector:

    def __init__(self, nxURL, user, password):
        self.nxURL = nxURL
        self.user = user
        self.password = password
        self.logger = logging.getLogger('nxpush')
    def openSession(self):
        self.session = Session(self.nxURL, self.user, self.password)
    
            
    def setNxPath(self, path):
        self.nxPath=path
    
    # You need to set nxPath with the convenient method before calling this    
    def upload(self, path):
        fileName = FileUtils.getFileName(path)
        extension = FileUtils.getExtension(fileName)
        nxFolder = self.session.fetch(self.nxPath.strip())
        folderUid = nxFolder['uid']
        nxDoc = self.session.create( folderUid, "File", fileName, {'dc:title': fileName} )
        docPath = nxDoc['path']
        try:
            binStream = open(path, 'rb')
            self.logger.debug('connector reads stream')
            blob=binStream.read().encode("base64")
        except Exception, e:
            self._handle_error(e)
            raise               
        return self.session.attachBlob(docPath, blob, extension)      


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


