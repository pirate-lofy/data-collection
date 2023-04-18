from saver import Saver
from cameras.camera_wrapper import Wrapper

import random
import sys
import numpy as np
import cv2 as cv
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
        self.configs=read_configs()
        self.init_attr()
        printc('all attributes initialized')
        
        self.blueprint=self._connect()
        printc('client connected')
        self.vehicle=self._add_vehicle(self.blueprint)
        printc('vehicle spawned')
        self._add_actors()
        printc('actors spawned')
    
    
    def init_attr(self):
        self.step=0

        # classes
        self.saver=Saver(self.configs)
        printc('Saver class initialized',level=2)
        self.wrapper=Wrapper(self.configs,self.vehicle)
        printc('Wrapper class initialized',level=2)



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

        self.wrapper.step()
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
        self.data=self.wrapper.retrieve()
        self.saver.save(self.data)
        

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
