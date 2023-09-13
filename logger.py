from genericpath import isfile
import sys
import logging 
import yaml
from attrdict import AttrDict
from pathlib import Path
import json
import traceback
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import cv2 as cv

class JsonFormatter(logging.Formatter):
    ''' reformat the message it gets to be in a json format to be saved to desk'''
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'module': record.module,
            'message': str(record.msg),
        }
        # If the log record has an exception, include its traceback in the log_data
        if record.exc_info:
            log_data['traceback'] = ''.join(traceback.format_exception(*record.exc_info))

        return json.dumps(log_data)


class LogFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, log_file,configs):
        super().__init__(log_file, when=configs.logs.rotation_when,
                                    backupCount=configs.logs.rotation_backupcount)  # BackupCount set to 0 to prevent from deleting old logs
        self.setFormatter(JsonFormatter(datefmt='%Y-%m-%d %H:%M:%S'))


class ConsoleLoggingHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter('%(asctime)s - %(name)s -%(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))


class Logger(logging.Logger):
    def __init__(self,module_name,configs):
        super().__init__(module_name)
        self.module_name=module_name
        self.configs=configs
        
        log_root=self.make_log_root()
        log_file = "{}/{}.log".format(log_root, self.module_name)
        self.setLevel(logging.DEBUG if self.configs.logs.level=='debug' else logging.INFO)
        
        console_handler = ConsoleLoggingHandler() # console handler
        file_handler = LogFileHandler(log_file,self.configs ) # file handler

        # message will be forwarded to all handlers added to this object
        self.addHandler(console_handler)
        self.addHandler(file_handler)

        self.propagate = False
        # sys.excepthook = custom_exception_hook


    def make_log_root(self):
        path=self.configs.logs.root
        if not os.path.exists(path):
            os.mkdir(path)
        return path
