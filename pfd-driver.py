import systemd.daemon
import pifacedigitalio
import redis


def execute():
    print('Startup')

    input_count = 8
    output_count = 8

    pfd = pifacedigitalio.PiFaceDigital()
    listener = pifacedigitalio.InputEventListener(chip=pfd)

    r = redis.Redis(host='192.168.0.1', port=6379,
                    db=0, decode_responses=True)
    p = r.pubsub(ignore_subscribe_messages=True)
    p.psubscribe('pfd.input', 'pfd.output.?')

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

            # Invoke it for initial state
            (input_off[i])(None)

            listener.register(
                i, pifacedigitalio.IODIR_FALLING_EDGE, input_on[i])
            listener.register(
                i, pifacedigitalio.IODIR_RISING_EDGE, input_off[i])

        listener.activate()

        for i in range(0, output_count):
            pfd.output_pins[i].turn_off()
            r.publish('pfd.output.' + str(i) + '.status',
                      'output.' + str(i) + '.on')

        for message in p.listen():
            if message['channel'] == 'pfd.input':
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
            elif message['channel'].startswith('pfd.output.'):
                output_id = int(message['channel'][-1])

                if output_id >= output_count or output_id < 0:
                    continue

                if message['data'] == 'on':
                    pfd.output_pins[output_id].turn_on()
                    r.publish('pfd.output.' +
                              str(output_id) + '.status', 'output.' + str(output_id) + '.on')
                elif message['data'] == 'off':
                    pfd.output_pins[output_id].turn_off()
                    r.publish('pfd.output.' +
                              str(output_id) + '.status', 'output.' + str(output_id) + '.off')
                elif message['data'] == '/':
                    pfd.output_pins[output_id].toggle()

                if message['data'] == '?' or message['data'] == '/':
                    pin_status = pfd.output_pins[output_id]
                    if pin_status.value:
                        r.publish('pfd.output.' +
                                  str(output_id) + '.status', 'output.' + str(output_id) + '.on')
                    else:
                        r.publish('pfd.output.' +
                                  str(output_id) + '.status', 'output.' + str(output_id) + '.off')
    except:
        p.close()

        listener.deactivate()
        pfd.deinit_board()

        r.publish('services', 'pfd.off')
        print("Goodbye")


if __name__ == '__main__':
    execute()
