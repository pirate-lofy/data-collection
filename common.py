from enum import Enum
from colorama import Fore

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


def printc(msg,which=MsgType.info,level=1):
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