"""
rover_control.py

1. Forward serial line commands
2. Log telemetry data
"""

import serial
import time
import os
import datetime
from parse import parse

from rover_control.drone_pprzlink import DronePprzlink
from rover_control.rover_serial import RoverSerial
from rover_control.logfile import LogFile
from rover_control.pi_led import Led


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
        self.led = Led()

        self.log = None

        self.cmd = (0, 0)
        self.timeout = 0

    def log_open(self):
        if self.log is None:
            log_idx = len(os.listdir('logs'))
            self.log = LogFile(f'logs/{log_idx:04d}.txt')

    def log_close(self):
        if self.log is not None:
            del self.log
            self.log = None

    def loop(self):
        try:
            msg = self.drone.read()
        except Exception as e:
            logging.error(f'Exception while reading from drone {e}, reopening...')
            self.drone.serial_open()
            return
        cmd = None
        if msg is not None:
            if self.log is not None:
                self.log.write(msg.to_json() + '\n')

            if msg.name == 'ROVER':
                cmd = (msg.left, msg.right)
            elif msg.name == 'IMCU_LOG':
                if msg.run == 0 and self.log is not None:
                    self.log_close()
                elif msg.run != 0 and self.log is None:
                    self.log_open()

        if cmd is not None:
            self.cmd = cmd
            self.timeout = time.time() + 0.5
            self.led.toggle()
        if time.time() > self.timeout:
            logging.error(f'Timeout exceeded! Commanding stop.')
            self.cmd = (0, 0)

        try:
            self.rover.send_command(self.cmd)
            self.rover.read_response()
        except Exception as e:
            logging.error(f'Exception while writing to rover {e}, reopening...')
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
