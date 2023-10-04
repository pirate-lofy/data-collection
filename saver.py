from common import *
from logger import Logger

class Saver:
    def __init__(self,configs):
        self.configs=configs
        self.logger=Logger('Saver',self.configs)
        self._init_attr()
        self.data_root=Path(self.configs.general.data_root)
        if self.configs.general.save:
            self._check_paths()
        self._get_latest()
        self.logger.debug('All saving paths has been checked')
        self.logger.info(self)


    def __str__(self):
        return f'''Saver with batch size of {self.configs.general.batch_size}, saving interval of {self.configs.general.save_interval}, saving to data_root={self.configs.general.data_root}, starting with batch #{self.step_number//self.configs.general.batch_size}'''


    def _get_latest(self):
        for sensor in self.configs.camera_types:
            for cam in self.configs.cameras:
                folder=self.data_root/sensor/cam
                if not folder.exists():continue
                files=os.listdir(folder)
                if not len(files):continue
                files=[int(i.split('.')[0]) for i in files]
                files.sort()
                self.step_number=files[-1]

    def _init_attr(self):
        self.counter=0 # number of sequential steps
        self.step_number=0
        self.data=[]

    def _create_dir(self,dir:Path)->None:
        if not dir.exists():
            self.logger.debug(f'{dir} has been created')
            os.mkdir(dir)

    def _check_paths(self):
        self._create_dir(self.data_root)

        for sensor in self.configs.camera_types:
            self._create_dir(self.data_root/sensor)

            for cam,cam_info in self.configs.cameras.items():
                if cam=='viz' or not cam_info['enable']:
                    continue
                self._create_dir(self.data_root/sensor/cam)


    def save(self,data:list):
         # saving configurations
        if not self.configs.general.save:
            return
        if self.counter%self.configs.general.save_interval==0:
            self.data.append(data)
        self.counter+=1

        if len(self.data) and len(self.data)%self.configs.general.batch_size==0:
            self.save_batch(self.data)
            self.data=[]
            self.logger.info(f'Saved batch #{self.step_number//self.configs.general.batch_size}')


    # accepts batch of data
    def save_batch(self,data:list)->None:
        for step in data:
            for cam,cam_data in step.items():
                for sensor_name,sensor_data in cam_data.items():
                    if cam=='viz':continue
                    cv.imwrite(f'data/{sensor_name}/{cam}/{self.step_number}.jpg',sensor_data)
            self.step_number+=1