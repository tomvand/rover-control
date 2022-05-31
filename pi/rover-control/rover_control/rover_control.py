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
logging.getLogger().addHandler(console)


class RoverControl(object):
    def __init__(self,
                 tty_in='/dev/ttyUSB0',
                 baud_in=9600,
                 tty_out='/dev/ttyUSB1',
                 baud_out=9600,
                 *args,
                 **kwargs):
        super().__init__()

        # Set up watchdog time
        self.last_read = None
        self.read_notified = False
        # Set up incoming serial device
        while True:
            try:
                self.tty_in = serial.Serial(
                    port=tty_in,
                    baudrate=baud_in,
                    timeout=0.10
                )
                break
            except Exception as e:
                logging.error(f'Unable to open {tty_in}: {e}, retrying...')
                time.sleep(2)
        # Set up outgoing serial device
        while True:
            try:
                self.tty_out = serial.Serial(
                    port=tty_out,
                    baudrate=baud_out,
                    timeout=0.10
                )
                break
            except Exception as e:
                logging.error(f'Unable to open {tty_out}: {e}, retrying...')
                time.sleep(2)

    def read_command(self):
        # Update watchdog
        now = time.time()
        if self.last_read is None:
            self.last_read = now
        if now - self.last_read > 0.20:
            if not self.read_notified:
                logging.warning('Command receive time exceeded!')
                self.read_notified = True
        else:
            self.read_notified = False
        # Read and parse
        try:
            inline = self.tty_in.readline()  # type: bytes
            inline = inline.decode()
            inline = inline.strip('\x00')
            inline = inline.strip()
            assert type(inline) == str, f'inline type is not str'
            assert len(inline) == 9, f'command string is not 9 characters: "{inline}" ({len(inline)})'
        except Exception as e:
            logging.error(f'Serial readline error: {e}')
            raise e

        try:
            r = {'left': int(inline[:4]), 'right': int(inline[5:])}
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

    def read_response(self):
        try:
            inline = self.tty_out.readline()  # type: bytes
            inline = inline.decode()
            inline = inline.strip('\x00')
            inline = inline.strip()
            if len(inline) != 0:
                logging.info(f"Arduino response: {inline}")
        except Exception as e:
            logging.error(f"Error reading Arduino response! {e}")
            raise e

    def loop(self):
        try:
            cmd = self.read_command()
            self.send_command(cmd)
            self.read_response()
        except Exception as e:
            logging.error(f'Error in main loop: {e}')


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
        time.sleep(0.1)
