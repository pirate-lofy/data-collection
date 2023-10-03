
from cameras.camera import Camera
from logger import Logger
from common import *

class Wrapper:

    def __init__(self,configs,vehicle,world):
        self.configs=configs
        self.vehicle=vehicle
        self.world=world
        self.logger=Logger('Wrapper',self.configs)

        self._init_attr()
        self.logger.info('all attributes are initializes')
        self.meta_cames=self._parse_cameras()
        self.logger.info('all cameras are parsed from the configuration file')
        self._generate_cames()
        self.logger.info('all cameras are generated and added to the wrapper')


    def _parse_cameras(self):
        meta_cames={k:v for k,v in self.configs['cameras'].items() if v['enable']}
        return meta_cames

    
    def _generate_cames(self):
        for (k,v) in self.meta_cames.items():
            c=Camera(self.configs,k,v,self.vehicle,self.world)
            self.cames.append(c)
            self.actors.extend(c.actors)
            self.logger.debug(f'camera {c.name} is generated')

    def _init_attr(self):
        self.cames=[]
        self.actors=[]
        self.data=[]

    def _check_cam_data(self,data):
        for type in self.configs.camera_types:
            if not (type in data):
                return False
        return True

    def step(self):
        self.visualize()
        step_data={}
        for cam in self.cames:
            if self._check_cam_data(cam.data):
                step_data[cam.name]=cam.get_data()
        return step_data        

    def get_actors(self):
        return self.actors

    def get_cames(self):
        return self.cames

    def visualize(self):
        if not self.configs.general.show:
            return 
        for cam in self.cames:
            if cam.name=='viz':
                data=cam.get_data()
                break
        if not len(data):
            return

        cv.imshow('rgb',cv.resize(data['rgb'],(600,480)))
        cv.imshow('seg',cv.resize(data['seg'],(600,480)))
        cv.imshow('dep',cv.resize(data['dep'],(600,480)))
        if cv.waitKey(1)==27:
            raise Exception()