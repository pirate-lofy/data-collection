import os
import sys
from common import *
import numpy as np

try:
    sys.path.append("carla-0.9.5-py3.5-linux-x86_64.egg")
except IndexError:
    printc('cant append carla #egg',MsgType.ERROR)

import carla
from carla import ColorConverter as cc

class Camera:
    
    def __init__(self,name,dic,vehicle):
        self.name=name
        self.vehicle=vehicle
        self.dic=AttrDict(dic)

        self.init_attr()
        self._make_cam(dic)

    def init_attr(self):
        self.data={}
        self.actors=[]

    def _make_cam(self,dic):
        image_x=self.dic.image_x
        image_y=self.dic.image_y
        fov=self.dic.fov

        loc=self.dic.location
        x,y,z=[*loc.values()]
        ori=self.dic.orientation
        pitch,yaw,roll=[*ori.values()]

        
        
        transform = carla.Transform(carla.Location(x=x, y=y, z=z),
                                    carla.Rotation(pitch=pitch, yaw=yaw, roll=roll))
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