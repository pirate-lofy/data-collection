from common import *
from logger import Logger

class Camera:
    
    def __init__(self,configs,name:str,settings:dict,vehicle,world):
        '''
            @input:
                name: name of the camera to be referenced with
                settings: settings of the camera comes from conf file
                vehicle: spawned vehicle 
                world: carla world
        '''
        self.configs=configs
        self.name=name
        self.vehicle=vehicle
        self.settings=AttrDict(settings)
        self.world=world
        self.blueprint=self.world.get_blueprint_library()
        self.logger=Logger('Camera',self.configs)

        self._init_attr()
        self.logger.info('all attributes are initialized')
        self._make_cam()


    def _init_attr(self):
        self.data={}
        self.actors=[]
        self.sensors_names=[]

    def _make_cam(self):
        image_x=self.settings.image_x
        image_y=self.settings.image_y
        fov=self.settings.fov

        loc=self.settings.location
        x,y,z=[*loc.values()]
        ori=self.settings.orientation
        pitch,yaw,roll=[*ori.values()]

        
        
        transform = carla.Transform(carla.Location(x=x, y=y, z=z),
                                    carla.Rotation(pitch=pitch, yaw=yaw, roll=roll))
        # rgb sensor
        if 'rgb' in self.configs.camera_types:
            rgb = self.blueprint.find('sensor.camera.rgb')
            rgb.set_attribute('image_size_x', f"{image_x}")
            rgb.set_attribute('image_size_y', f"{image_y}")
            rgb.set_attribute('fov', f"{fov}")
            rgb = self.world.spawn_actor(rgb, transform, attach_to=self.vehicle)
            rgb.listen(lambda data: self._process_rgb(data))
            self.actors.append(rgb)
            self.sensors_names.append('rgb')
            self.logger.info('RGB sensor is added')
        
        # segmentation sensor
        if 'seg' in self.configs.camera_types:
            seg = self.blueprint.find('sensor.camera.semantic_segmentation')
            seg.set_attribute('image_size_x', f"{image_x}")
            seg.set_attribute('image_size_y', f"{image_y}")
            seg.set_attribute('fov', f'{fov}')
            seg = self.world.spawn_actor(seg, transform, attach_to=self.vehicle)
            seg.listen(lambda data: self._process_seg(data))
            self.actors.append(seg)
            self.sensors_names.append('seg')
            self.logger.info('Segmentation sensor is added')
        
        # depth sensor
        if 'dep' in self.configs.camera_types:
            dep=self.blueprint.find('sensor.camera.depth')
            dep.set_attribute('image_size_x', f"{image_x}")
            dep.set_attribute('image_size_y', f"{image_y}")
            dep.set_attribute('fov', f'{fov}')
            dep = self.world.spawn_actor(dep, transform, attach_to=self.vehicle)
            dep.listen(lambda data: self._process_depth(data))
            self.actors.append(dep)
            self.sensors_names.append('dep')
            self.logger.info('Depth sensor is added')

    
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


    def get_data(self):
        '''
            it won't work if you tried to access
            self.data directrly from outside this class
            as data would not change through time 
        '''
        return deepcopy(self.data)

    
    def __str__(self):
        return f'Camera {self.name} attached to vehicle {self.vehicle} with settings {dict(self.settings)} and list of sensors {self.sensors_names}'
