from saver import Saver

import random
import sys
import numpy as np
import cv2 as cv
import yaml
from attrdict import AttrDict
import matplotlib.pyplot as plt
from common import *

try:
    sys.path.append("carla-0.9.5-py3.5-linux-x86_64.egg")
except IndexError:
    printc('CarlaEnv log: cant append carla #egg',MsgType.ERROR)

import carla
from carla import ColorConverter as cc

class CarlaEnv:    
    def __init__(self):
        self.configs=self._read_configs()
        self.intialize_attributes()
        printc('all attributes initialized')
        
        self.blueprint=self._connect()
        printc('client connected')
        self.vehicle=self._add_vehicle(self.blueprint)
        printc('vehicle spawned')
        self._add_actors()
        printc('actors spawned')
    

    def _read_configs(self):
        path='config.yaml'
        with open(path, 'r', encoding='utf8') as f:
            config = yaml.safe_load(f)
        config = AttrDict(config)
        return config
    
    def initialize_attributes(self):
        self.step=0
        self.actors=[]
        self.data={}

        # classes
        self.saver=Saver()
        printc('Saver class initialized',level=2)



    def _connect(self):
        self.client=carla.Client(self.configs.host,self.configs.port)
        self.world=self.client.get_world()
        self.map=self.world.get_map()
        return self.world.get_blueprint_library()

    def _add_vehicle(self,blueprint):
        car=blueprint.filter('model3')[0]
        transform=random.choice(self.map.get_spawn_points())
        vehicle=self.world.spawn_actor(car,transform)
        self.actors.append(vehicle)
        return vehicle

    def _add_actors(self):
        image_x=self.configs.image_x
        image_y=self.configs.image_y
        fov=self.configs.fov
        
        transform = carla.Transform(carla.Location(x=1.1, y=0, z=2),
                                    carla.Rotation(pitch=0, yaw=0, roll=0))
        # rgb cam
        rgb = self.blueprint.find('sensor.camera.rgb')
        rgb.set_attribute('image_size_x', f"{image_x}")
        rgb.set_attribute('image_size_y', f"{image_y}")
        rgb.set_attribute('fov', f"{fov}")
        rgb = self.world.spawn_actor(rgb, transform, attach_to=self.vehicle)
        rgb.listen(lambda data: self._process_rgb(data))
        self.actors.append(rgb)
        printc('rgb camera spawned',level=2)
        
        # segmentation cam
        seg = self.blueprint.find('sensor.camera.semantic_segmentation')
        seg.set_attribute('image_size_x', f"{image_x}")
        seg.set_attribute('image_size_y', f"{image_y}")
        seg.set_attribute('fov', f'{fov}')
        seg = self.world.spawn_actor(seg, transform, attach_to=self.vehicle)
        seg.listen(lambda data: self._process_seg(data))
        self.actors.append(seg)
        printc('rgb camera spawned',level=2)
        
        # depth cam
        dep=self.blueprint.find('sensor.camera.depth')
        dep.set_attribute('image_size_x', f"{image_x}")
        dep.set_attribute('image_size_y', f"{image_y}")
        dep.set_attribute('fov', f'{fov}')
        dep = self.world.spawn_actor(dep, transform, attach_to=self.vehicle)
        dep.listen(lambda data: self._process_depth(data))
        self.actors.append(dep)
        printc('rgb camera spawned',level=2)
        

    def _process_rgb(self,image):
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        self.data['rgb']=array.copy()

    def _process_seg(self,image):
        image.convert(cc.CityScapesPalette)
        i3=np.array(image.raw_data)
        i3 = i3.reshape((image.height,image.width,4))[:,:,:3] 
        self.data['seg']=i3.copy()

    def _process_depth(self,image):
        image.convert(cc.LogarithmicDepth)
        i3=np.array(image.raw_data)
        i3=i3.reshape((image.height,image.width,4))[:,:,:3]
        self.data['dep']=i3.copy()


    def _flush(self):
        self.data={}

    def close(self):
        self.client.apply_batch([carla.command.DestroyActor(x)
                                for x in self.actors])
        cv.destroyAllWindows()
        printc("All actors and windows have been destroyed")

    def step(self,action):
        throttle=action['thr']
        steer=action['ste']
        brake=action['br']
        control=carla.VehicleControl(throttle,steer,brake)
        self.vehicle.apply_control(control)
        self.step+=1

        if self.config.save and \
            check_saving_interval(self.step,self.configs.saving_interval):
            self._save()

    def show(self,title,frame):
        cv.imshow(title, frame)
        key = cv.waitKey(1)
        return key
 
    
    def _save(self):
        printc('saving data to disk')
        self.saver.save(self.data)
        self._flush()
        

    def render(self,which):
        if which=='all':
            for data in self.data.items():
                k=self.show(*data)
        else:
            for data_f in data_frames:
                if which==data_f and data_f in self.data:
                    k=self.show(data_f,self.data[data_f])
        

        # end program by raising exception which will be handled in the main script
        if k==27: # escape button
            raise Exception
