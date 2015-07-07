# -*- coding: utf8 -*-
'''
Created on 16 oct. 2013
@author: acordier
'''
from __future__ import unicode_literals
from connector import NxConnector
from ocrwrapper import OcrWrapper
from listener import EventHandler, Listener
from xml.dom.minidom import parseString
import getpass
import sys
import logging
import traceback
import os


def main():
    # logging stuff
    logger = logging.getLogger('nxpush')
    logger.setLevel(logging.DEBUG) # Configure global level here
    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
    fileHandler = logging.FileHandler('/home/nxpush/log/client.log')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)    
    logger.debug(' %s started' %__name__)
    
    path = os.path.dirname(os.path.abspath(__file__))
 
    #unwrapping properties
    try:
        propFile = open('%s/nx-properties.xml' %path)
        data = propFile.read()
        propFile.close()
    except:     
        logger.error('file error')
        sys.exit(0)
    try:     
        dom = parseString(data)
        credFilePath = dom.getElementsByTagName('credentials')[0].childNodes[0].nodeValue
        ocrScript = dom.getElementsByTagName('script')[0].childNodes[0].nodeValue        
        mapping=dom.getElementsByTagName('mapping')
        # mapping local to remote	
        mapper={}
        for node in mapping:
            local = node.getElementsByTagName('local')[0].childNodes[0].nodeValue
            remote = node.getElementsByTagName('remote')[0].childNodes[0].nodeValue
            mapper[local]=remote
    except:   
        traceback.print_exc()     
        
        logger.error('Document Object Model Error')     
        sys.exit(0) 
    # nuxeo url
    host = dom.getElementsByTagName('host')[0].childNodes[0].nodeValue
    url = '%s/nuxeo/site/automation/' %host
    
    if (len(sys.argv)==1):
        # nuxeo credentials are read  from ${credentialsPath}/credentials.xml
        try:
            credFile = open(credFilePath);
            data = credFile.read()
            credFile.close()           
        except:
            logger.error('file error') 
        
        try:     
            dom = parseString(data)
            user = dom.getElementsByTagName('user')[0].childNodes[0].nodeValue 
            password=dom.getElementsByTagName('pass')[0].childNodes[0].nodeValue
        except:
            logger.error('Document Object Model Error')      
            
    elif ( sys.argv[1]=='--prompt' ):     
        # nuxeo credentials are read  from prompt
        print 'Authentication to the nuxeo platform' 
        user = raw_input("Utilisateur: " )        
        password = getpass.getpass("Mot de passe: ") 
    else:
        print 'Usage : python nxpush.py [--prompt]' 
        sys.exit(0)
        
    
    # getting a session
    try:
        connector = NxConnector(url, user, password)
        connector.openSession()
    except:
        logger.error('%s \n >>> ERROR: Invalid username or password ' %url)       
        sys.exit(0)

    # setting up ocr wrapper
    try:
        ocr = OcrWrapper(ocrScript)
    except FileNotFoundError, e:
        logger.error('Failed to wrap ocr script: '+ str(e))
    
    # listener
    handler = EventHandler(connector, ocr, mapper)
    listener = Listener(mapper.keys(), handler)
    
    # start
    listener.listen()
    logger.debug('nxpush service is running')
    
if __name__ == '__main__':
    main()
