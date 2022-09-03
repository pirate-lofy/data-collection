from glob import glob
from os import path
from turtle import st
import cv2 as cv
import re
from common import *

class Saver:
    def __init__(self,flush=True):
        self.origins=origins.copy()

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

    def _check_available(self,data):
        for orig in self.origins:
            if not orig[0] in data:
                printc(orig[0] +' not included',MsgType.WARN,level=3)
        return True

    def _check_sync(self):
        return True


    def _save_list(self,data):
        name,lst=data
        for i,orig in enumerate(self.origins):
            if name==orig[0]:
                index=i
                path=orig[1]
                count=orig[2]
                break
        for img in lst:
            npath=path+name+'-'+str(count)+'.jpg'
            count+=1
            self._save_img(npath,img)
        
        self.origins[index][2]=count

    def _save_img(self,path,img):
        cv.imwrite(path,img)    


    def _save_data(self,data):
        for d in data.items():
            self._save_list(d)


        # updating counters
        for i in len(origins):
            origins[i][2]=self.origins[i][2]

    def _flush(self):
        self._find_latest()

    # accepts batch of data
    def save(self,data):
        self._flush()
        self._check_available(data)
        self._check_sync()
        printc('saving check are done',level=2)

        self._save_data(data)
        printc('done saving data to disk',level=2)

