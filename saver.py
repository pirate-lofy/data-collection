from glob import glob
from os import path
import cv2 as cv
import re

class Saver:
    def __init__(self,flush=True):
        self.c_data=[]
        self.origins=[
                      ['seg','data/seg/',0],
                      ['rgb','data/rgb/',0],
                      ['dep','data/dep/',0]
                     ]
        if flush:
            self._find_latest()

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
                #slef.error(not_in_dic)
                print(orig[0] +' not included')
                continue
            self.c_data.append(orig[0])
        return True

    def _check_sync(self):
        return True

    def _save_data(self,data):
        for orig in self.origins:
            if not orig[0] in self.c_data:
                continue
            name=orig[1]+orig[0]+'-'+str(orig[2])+'.jpg'
            orig[2]+=1
            d=data[orig[0]]
            #print(name)
            cv.imwrite(name,d)


    def save(self,data):
        self._check_available(data)
        self._check_sync()

        self._save_data(data)

