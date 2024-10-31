import motors as mot
import keyboardmodule as km
km.init()
while True:
    if km.getKey('w'):
        print('bright')
        mot.bleft(100)
    elif km.getKey('s'):
        print('fright')
        mot.fright(100)
    elif km.getKey('q'):
        print('fleft')
        mot.fleft(100)
    elif km.getKey('e'):
        print('fright')
        mot.fright(100)
    elif km.getKey('a'):
        print('backward')
        mot.backward(100)
    elif km.getKey('d'):
        print('fleft')
        mot.fleft(100)
    else:
        mot.stop(0)