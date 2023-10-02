# imports
from enum import Enum
from colorama import Fore
import yaml
import datetime as dt
import time
from attrdict import AttrDict
import carla
from carla import ColorConverter as cc
import random
import sys
import numpy as np
import cv2 as cv
from copy import deepcopy

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

def show(title,img):
    cv.imshow(title,img)
    cv.waitKey(0)