"""
rover_control.py

1. Forward serial line commands
2. Log telemetry data
"""

import serial
import time
from parse import parse

import logging
logging.basicConfig(
    filename='rover_control.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)


class RoverControl(object):
    def __init__(self,
                 tty_in='/dev/ttyUSB0',
                 baud_in=9600,
                 tty_out='/dev/ttyUSB1',
                 baud_out=9600,
                 *args,
                 **kwargs):
        super().__init__()

        # Set up incoming serial device
        self.tty_in = serial.Serial(
            port=tty_in,
            baudrate=baud_in,
            timeout=0.10
        )
        # Set up outgoing serial device
        self.tty_out = serial.Serial(
            port=tty_out,
            baudrate=baud_out
        )

    def read_command(self):
        try:
            inline = self.tty_in.readline()
            assert(type(inline) == str)
        except Exception as e:
            logging.error(f'Serial readline error: {e}')
            raise e

        try:
            assert(len(inline.strip()) == 9)
            r = parse('{left:d},{right:d}', inline)
            cmd = (r['left'], r['right'])
            logging.debug(f'Received command: {cmd}')
            return cmd
        except Exception as e:
            logging.error(f'Command parsing error: {e}')
            raise e

    def send_command(self, cmd):
        # Command format:
        # left: int8 except -128; right: int8 except -128; stop byte: -128
        left_int = round(cmd[0] / 100.0 * 127.0)
        right_int = round(cmd[1] / 100.0 * 127.0)
        if left_int == -128:
            left_int = -127
        if right_int == -128:
            right_int = -127
        logging.debug(f'Command: {cmd}')
        logging.debug(f'Left int: {left_int}, right int: {right_int}')
        left_b = left_int.to_bytes(1, byteorder='big', signed=True)
        right_b = right_int.to_bytes(1, byteorder='big', signed=True)
        stop_b = (-128).to_bytes(1, byteorder='big', signed=True)
        cmd_b = left_b + right_b + stop_b
        logging.debug(f'Command bytes: {cmd_b}')
        # Send command
        self.tty_out.write(cmd_b)

    def loop(self):
        try:
            cmd = self.read_command()
            self.send_command(cmd)
        except Exception as e:
            logging.error(f'Error in main loop: {e}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Rover control script')
    parser.add_argument('tty_in', type=str)
    parser.add_argument('tty_out', type=str)
    args = parser.parse_args()

    c = RoverControl(**vars(args))
    while True:
        c.loop()
        time.sleep(0.05)
