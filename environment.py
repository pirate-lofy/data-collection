import prepare_env
from common import *

from saver import Saver
from logger import Logger
from cameras.camera_wrapper import Wrapper
from agents.navigation.behavior_agent import BehaviorAgent ,BasicAgent



class CarlaEnv:    
    def __init__(self):
        self.configs=read_configs()
        self.logger=Logger('CarlaEnv',self.configs)
        self._init_attr()

        self._connect()
        self.logger.info('client connected')
        self.vehicle=self._add_vehicle()
        self.logger.info('vehicle spawned')
        
        # initial world tick is mandatory for the path planner to 
        # work properly, without it it would make the vehicle
        # spines arounds itself, which means there is no waypoints 
        # in this world to follow
        self.world.tick()

        # cameras wrapper
        self.wrapper=Wrapper(self.configs,self.vehicle,self.world) 
        self.actors.extend(self.wrapper.get_actors())

        # data saver
        self.saver=Saver(self.configs)

        # PID controller
        self.controller = BasicAgent(self.vehicle) 
        self.spawn_points = self.map.get_spawn_points() 
        destination=self._get_random_location()
        self.controller.set_destination(destination)

    def _get_random_location(self):
        destination = random.choice(self.spawn_points).location
        return destination


    def _init_attr(self):
        self.actors=[]
        self.data=[]
        self.counter=0 # number of sequential steps



    def _connect(self):
        '''
            makes a connection with carla server and prepare
            world and map
        '''
        self.client=carla.Client(self.configs.host,self.configs.port)

        self.world=self.client.get_world()
        settings = self.world.get_settings()
        settings.synchronous_mode = True # Enables synchronous mode
        settings.fixed_delta_seconds = 0.05
        self.world.apply_settings(settings)

        self.map=self.world.get_map()
        self.blueprint=self.world.get_blueprint_library()


    def _add_vehicle(self):
        '''
            spawn a vehicle in a random location
        '''
        car=self.blueprint.filter(self.configs.actors.car)[0]
        transform=random.choice(self.map.get_spawn_points())
        vehicle=self.world.spawn_actor(car,transform)
        self.actors.append(vehicle)
        return vehicle
        

    def step(self):
        '''
            0. set a random destination and get command from controller
            1. applies control to the vehicle 
            2. apply a world tick 
            3. retrieve data from sensors
            4. aler saver class to save batch
        '''
        # 0
        if self.controller.done():
            spawn_points = self.map.get_spawn_points()
            destination = random.choice(spawn_points).location
            self.controller.set_destination(destination)
        
        control = self.controller.run_step()

        # 1
        control.manual_gear_shift = False
        self.vehicle.apply_control(control)
        
        # 2, as world runs in a sync mode 
        self.world.tick()

        # 3
        data=self.wrapper.step()
        if not len(data):
            return 
        # 4
        self._check_saving_interval(data)
        self._check_writing_interval()
        

    def _check_saving_interval(self,data):
        # saving configurations
        if not self.configs.save:
            return
        if self.counter%self.configs.general.save_interval==0:
            self.data.append(data)
        self.counter+=1


    def _check_writing_interval(self):
        if len(self.data) and len(self.data)%self.configs.general.batch_size==0:
            self.saver.save(self.data)
            self.data=[]
            self.logger.info('saved one batch')


    def close(self):
        self.client.apply_batch([carla.command.DestroyActor(x)
                                for x in self.actors])
        cv.destroyAllWindows()
        self.logger.info("All actors and windows have been destroyed")

if __name__=='__main__':
    try:
        env=CarlaEnv()
        while 1:
            env.step()

    except Exception as e:
        env.logger.exception(e)
        env.close()
    except KeyboardInterrupt as e:
        env.logger.exception(e)
        env.close()
    finally:
        env.close()
