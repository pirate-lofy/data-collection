import sys

print('preparing env paths and variables')

try:
    sys.path.append("carla-0.9.13-py3.7-linux-x86_64.egg")
except IndexError:
    print('CarlaEnv log: cant append carla #egg')

sys.path.append(".")

sys.path.append("cameras")
