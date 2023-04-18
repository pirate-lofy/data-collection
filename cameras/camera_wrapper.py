from cameras.camera import Camera

from copy import deepcopy

class Wrapper:

    def __init__(self,configs,vehicle):
        self.configs=configs
        self.vehicle=vehicle

        self.init_attr()
        self.num,self.meta_cames=self._parse_cameras()
        self._generate_cames()


    def _parse_cameras(self):
        meta_cames=dict([i for i in self.configs.items() if 'cam' in i[0]])
        return len(meta_cames),meta_cames

    
    def _generate_cames(self):
        for (k,v) in self.meta_cames.items():
            c=Camera(k,v,self.vehicle)
            self.cames.append(c)
            self.actors.extend(c.actors)

    def init_attr(self):
        self.cames=[]
        self.actors=[]
        self.data=[]

    def step(self):
        self.data.append({cam.name:cam.data for cam in self.cames})

    def retrieve(self):
        data=deepcopy(self.data)
        self.data=[]
        return data