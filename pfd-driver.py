import systemd.daemon
import pifacedigitalio
import redis
import time


def execute():
    print('Startup')

    input_count = 8

    pfd = pifacedigitalio.PiFaceDigital()
    listener = pifacedigitalio.InputEventListener(chip=pfd)

    r = redis.Redis(host='192.168.0.1', port=6379,
                    db=0, decode_responses=True)
    p = r.pubsub(ignore_subscribe_messages=True)
    p.subscribe('pfd.inputs')

    input_on = [None]*input_count
    input_off = [None]*input_count

    r.publish('services', 'pfd.on')
    systemd.daemon.notify('READY=1')
    print('Startup complete')

    try:
        for i in range(0, input_count):
            input_on[i] = lambda e, i=i: r.publish(
                "pfd.input." + str(i), "input." + str(i) + ".on")
            input_off[i] = lambda e, i=i: r.publish(
                "pfd.input." + str(i), "input." + str(i) + ".off")
            listener.register(
                i, pifacedigitalio.IODIR_FALLING_EDGE, input_on[i])
            listener.register(
                i, pifacedigitalio.IODIR_RISING_EDGE, input_off[i])

        listener.activate()

        for message in p.listen():
            if message['data'] == "*":
                tgt_range = range(0, input_count)
            else:
                try:
                    rangespec = int(message['data'])
                    if rangespec < 0 or rangespec > 7:
                        tgt_range = None
                    else:
                        tgt_range = range(rangespec, rangespec + 1)
                except:
                    # Do nothing if can't parse
                    tgt_range = range(0, 0)
            for i in tgt_range:
                if pfd.input_pins[i].value > 0:
                    (input_on[i])(None)
                else:
                    (input_off[i])(None)
    except:
        p.close()

        listener.deactivate()
        pfd.deinit_board()

        r.publish('services', 'pfd.off')
        print("Goodbye")


if __name__ == '__main__':
    execute()
