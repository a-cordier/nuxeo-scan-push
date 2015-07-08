# -*- coding: utf8 -*-
'''
Created on 14 oct. 2013

@author: acordier
'''
from __future__ import unicode_literals
import pyinotify
import logging
from connector import NxConnector
import sys
import functools
import os


class EventHandler(pyinotify.ProcessEvent):
    
    def __init__(self, connector, ocr, mapper):
        self.connector=connector
        self.ocr=ocr
        self.mapper=mapper
        self.logger = logging.getLogger('nxpush')
        self.logger.debug('init %s' %self.__class__.__name__)
        
    def process_IN_CREATE(self, event):
        path = event.pathname
        if not os.path.isfile(path):
            return
        index = path.rfind('/')
        self.logger.debug('1')
        self.connector.setNxPath(self.mapper[path[:index]])
        self.logger.debug('2')
        try:
            path = self.ocr.doOcr(path)
        except CalledProcessError, e:
            logger.error('OCR subprocess failed: '+ str(e))
        self.logger.debug('3')
        path = path.rstrip()
        self.connector.upload(path)
        self.logger.info('%s processed' %path)

    def process_IN_DELETE(self, event):
        self.logger.info("Removing:", event.pathname)
        
    def setConnector(self, connector):
        self.connector = connector



class Listener:
        
    def __init__(self, paths, eventHandler):
        self.paths=paths      
        self.watchManager = pyinotify.WatchManager() # Watch Manager
        self.mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE # watched events
        self.watchDescDict = self.watchManager.add_watch(self.paths, self.mask, rec=True, auto_add=True) # should put a list of pathes here
        self.notifier = pyinotify.Notifier(self.watchManager, eventHandler)
        self.logger = logging.getLogger('nxpush')
    
    def on_loop(self, notifier):       
        self.logger.debug(' notifier loop') # use in case of improvement >> caching ?
            
    def listen(self):
        on_loop_func = functools.partial(self.on_loop)
    #    self.notifier.loop(daemonize=True, callback=on_loop_func, pid_file='/var/run/nxpush.pid', stdout='stdout.log')
   	self.notifier.loop(callback=on_loop_func)     
