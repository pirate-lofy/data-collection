from saver import Saver

from colorama import Fore
import random
import sys
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

try:
    sys.path.append("carla-0.9.5-py3.5-linux-x86_64.egg")
except IndexError:
    print(Fore.YELLOW+'CarlaEnv log: cant append carla #egg'+Fore.WHITE)

import carla
from carla import ColorConverter as cc

class CarlaEnv:
    # attributes
    port=2000
    host='127.0.01'
    actors=[]
    data={}
    image_x=800
    image_y=600
    fov=110
    
    def __init__(self):
        self.saver=Saver()
        
        self.blueprint=self._connect()
        print(Fore.YELLOW+'client connected'+Fore.WHITE)
        self.vehicle=self._add_vehicle(self.blueprint)
        print(Fore.YELLOW+'vehicle spawned'+Fore.WHITE)
        self._add_actors()
        print(Fore.YELLOW+'actors spawned'+Fore.WHITE)
    
    
    def _connect(self):
        self.client=carla.Client(self.host,self.port)
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
        image_x=self.image_x
        image_y=self.image_y
        fov=self.fov
        
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
        
        # segmentation cam
        seg = self.blueprint.find('sensor.camera.semantic_segmentation')
        seg.set_attribute('image_size_x', f"{image_x}")
        seg.set_attribute('image_size_y', f"{image_y}")
        seg.set_attribute('fov', f'{fov}')
        seg = self.world.spawn_actor(seg, transform, attach_to=self.vehicle)
        seg.listen(lambda data: self._process_seg(data))
        self.actors.append(seg)
        
        # depth cam
        dep=self.blueprint.find('sensor.camera.depth')
        dep.set_attribute('image_size_x', f"{image_x}")
        dep.set_attribute('image_size_y', f"{image_y}")
        dep.set_attribute('fov', f'{fov}')
        dep = self.world.spawn_actor(dep, transform, attach_to=self.vehicle)
        dep.listen(lambda data: self._process_depth(data))
        self.actors.append(dep)
        



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

    def close(self):
        self.client.apply_batch([carla.command.DestroyActor(x)
                                for x in self.actors])
        cv.destroyAllWindows()
        print("All actors have been destroyed")

    def step(self,action):
        throttle=action['thr']
        steer=action['ste']
        brake=action['br']
        control=carla.VehicleControl(throttle,steer,0)
        self.vehicle.apply_control(control)

    def show(self,title,frame):
        cv.imshow('frame', frame)
        key = cv.waitKey(1) & 0xFF
             
    
    def save(self):
        self.saver.save(self.data)
        

    def render(self,which):
        if which=='rgb' and 'rgb' in self.data:
            self.show('rgb',self.data['rgb'])
        elif which=='dep' and 'dep' in self.data: 
            self.show('depth',self.data['dep'])
        elif which=='seg' and 'seg' in self.data:
            self.show('segmentation',self.data['seg'])
