from enum import Enum
from colorama import Fore
import yaml
from attrdict import AttrDict

origins=[
        ['seg','data/seg/',0],
        ['rgb','data/rgb/',0],
        ['dep','data/dep/',0]
        ]
data_frames=['seg','rgb','dep']


class MsgType(Enum):
    INFO=0,
    ERROR=1,
    WARN=2

def printc(msg:str,which=MsgType.INFO,level:int=1)-> None:
    msg='CarlaEnv: '+msg
    # hireical printing
    for _ in range(level-1):
        print('\t',end='')

    if which==MsgType.INFO:
        print(Fore.GREEN+msg+Fore.WHITE)
    elif which==MsgType.ERROR:
        print(Fore.RED+msg+Fore.WHITE)
    elif which==MsgType.WARN:
        print(Fore.YELLOW+msg+Fore.WHITE)
    
    if level==1:
        print()

def check_saving_interval(i,interval):
    return i%interval==0

def read_configs():
    path='config.yaml'
    with open(path, 'r', encoding='utf8') as f:
        config = yaml.safe_load(f)
    config = AttrDict(config)
    return config