"""
rover_control.py

1. Forward serial line commands
2. Log telemetry data
"""

import serial
import time
from parse import parse

from rover_control.drone_pprzlink import DronePprzlink
from rover_control.rover_serial import RoverSerial


import logging
logging.basicConfig(
    filename='rover_control.log',
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logging.getLogger().addHandler(console)
logging = logging.getLogger(__name__)


class RoverControl(object):
    def __init__(self,
                 tty_in='/dev/ttyUSB0',
                 baud_in=9600,
                 tty_out='/dev/ttyUSB1',
                 baud_out=9600,
                 *args,
                 **kwargs):
        super().__init__()

        self.drone = DronePprzlink(tty_in)
        self.rover = RoverSerial(tty_out, baud_out)

        self.timeout = 0

    def loop(self):
        cmd = None

        try:
            msg = self.drone.read()
        except Exception as e:
            logging.error('Exception while reading from drone {e}, reopening...')
            self.drone.serial_open()
            return

        if msg is not None:
            if msg.name == 'ROVER':
                cmd = (msg.left, msg.right)

        if cmd is not None:
            self.timeout = time.time() + 0.5

        try:
            if time.time() < self.timeout:
                self.rover.send_command(cmd)
            else:
                self.rover.send_command((0, 0))
            # self.rover.read_response()
        except Exception as e:
            logging.error('Exception while writing to rover {e}, reopening...')
            self.rover.serial_open()
            return


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Rover control script')
    parser.add_argument('tty_in', type=str)
    parser.add_argument('tty_out', type=str)
    args = parser.parse_args()

    logging.info(f'\n\nNew log started at {time.asctime()}')

    c = RoverControl(**vars(args))
    while True:
        c.loop()
        time.sleep(0.01)
