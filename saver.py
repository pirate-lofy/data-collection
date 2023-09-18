from glob import glob
from os import path
import cv2 as cv
import re
from common import *

class Saver:
    def __init__(self,configs,flush=True):
        self.configs=configs
        self.origins=origins.copy()
        self.cams=[i for i in self.configs if 'cam' in i[0]]
        self.iter=0

        if flush:
            self._flush()

    def _find_latest(self):
        for orig in self.origins:
            files=glob(orig[1]+'*')
            if len(files)>0:
                files=[path.split(x)[1] for x in files]
                nums=[int(re.findall(r'\d+',f)[0]) for f in files]
                orig[-1]=max(nums)


    def _reset(self):
        self._find_latest()

    def _check_available(self,data:dict)->None:
        
        # check for all cameras existance
        if not len(self.cams)==len(data):
            printc('not all cameras available',MsgType.ERROR,2)
            for a in self.cams:
                if not a in data:
                    printc(f'camera number {a} not included',MsgType.ERROR,3)


        for cam in data:
            for orig in self.origins:
                if not orig[0] in cam:
                    printc(orig[0] +' not included',MsgType.WARN,level=3)
     

    def _check_sync(self)->bool:
        return True


    def _save_list(self,data:tuple,cam:str)->None:
        name,lst=data
        for i,orig in enumerate(self.origins):
            if name==orig[0]:
                index=i
                path=orig[1]
                count=orig[2]
                break
        for img in lst:
            npath=path+cam+'-'+name+'-'+str(count)+'.jpg'
            count+=1
            self._save_img(npath,img)
        
        self.origins[index][2]=count

    def _save_img(self,path:str,img):
        cv.imwrite(path,img)    


    def _save_data(self,data:dict)->None:
        for cam,value in data.items():
            for d in value.items():
                self._save_list(d,cam)


        # updating counters
        for i in len(origins):
            origins[i][2]=self.origins[i][2]

    def _flush(self):
        self._find_latest()

    # accepts batch of data
    def save(self,data:list)->None:
        for step in data:
            for cam,cam_data in step.items():
                for sensor_name,sensor_data in cam_data.items():
                    self._save_img(f'data/{sensor_name}-{cam}-{time.time()}.jpg',sensor_data)