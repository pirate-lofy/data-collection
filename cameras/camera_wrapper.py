
from cameras.camera import Camera
from logger import Logger

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
        meta_cames=dict([i for i in self.configs['cameras'].items()])
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
        step_data=[]
        for cam in self.cames:
            if self._check_cam_data(cam.data):
                step_data.append({cam.name:cam.data})
        return step_data        

    def get_actors(self):
        return self.actors

    def get_cames(self):
        return self.cames