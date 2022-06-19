from environment import CarlaEnv
import logging 

try:
    env=CarlaEnv()
    action={'thr':1,'ste':0,'br':0}

    i=0
    while 1:
        env.step(action)
        env.render('dep')
        #env.save()

except Exception:
    env.close()
    logging.exception('')
