if __name__ == '__main__':
    import systemd.daemon
    import pifacedigitalio
    import redis
    import time

    print('Startup')
    pfd = pifacedigitalio.PiFaceDigital()
    listener = pifacedigitalio.InputEventListener(chip=pfd)
    r = redis.Redis(host='192.168.0.1', port=6379, db=0)
    p = r.pubsub(ignore_subscribe_messages=True)
    p.subscribe('pfd.inputs')
    print('Startup complete')
    systemd.daemon.notify('READY=1')

    input_on = list()
    input_off = list()

    try:
        for i in range(0, 8):
            input_on[i] = lambda e: r.publish(
                "pfd.input." + str(i), "input." + str(i) + ".on")
            input_on[i] = lambda e: r.publish(
                "pfd.input." + str(i), "input." + str(i) + ".off")
            listener.register(
                i, pifacedigitalio.IODIR_FALLING_EDGE, input_on[i])
            listener.register(
                i, pifacedigitalio.IODIR_RISING_EDGE, input_off[i])

        listener.activate()

        for message in p.listen():
            # If message is received, send current status
            if message.data == "*":
                tgt_range = range(0, 8)
            else:
                try:
                    rangespec = int(message.data)
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
        listener.deactivate()
        pfd.deinit_board()
        print("Goodbye")
