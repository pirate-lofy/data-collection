from glob import glob
from os import path
import cv2 as cv
import re
from common import *

class Saver:
    def __init__(self,configs,flush=True):
        self.configs=configs
        self.iter=0

    def _check_sync(self)->bool:
        return True

    def _save_img(self,path:str,img):
        cv.imwrite(path,img)    

    # accepts batch of data
    def save(self,data:list)->None:
        for step in data:
            for cam,cam_data in step.items():
                for sensor_name,sensor_data in cam_data.items():
                    if cam=='viz':continue
                    self._save_img(f'data/{sensor_name}-{cam}-{time.time()}.jpg',sensor_data)