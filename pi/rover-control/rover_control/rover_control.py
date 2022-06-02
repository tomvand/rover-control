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

        self.write_errors = 0

        # Set up watchdog time
        self.last_read = None
        self.read_notified = False
        # Set up incoming serial device
        while True:
            try:
                self.tty_in = serial.Serial(
                    port=tty_in,
                    baudrate=baud_in,
                    timeout=0.001
                )
                break
            except Exception as e:
                logging.error(f'Unable to open {tty_in}: {e}, retrying...')
                time.sleep(2)
        # Set up outgoing serial device
        self.tty_out_name = tty_out
        self.tty_out_baud = baud_out
        self.tty_out = None
        self.init_tty_out()

    def init_tty_out(self):
        if self.tty_out is not None:
            try:
                self.tty_out.close()
            except:
                pass
        while True:
            try:
                self.tty_out = serial.Serial(
                    port=self.tty_out_name,
                    baudrate=self.tty_out_baud,
                    timeout=0.001
                )
                self.write_errors = 0
                break
            except Exception as e:
                logging.error(f'Unable to open {self.tty_out_name}: {e}, retrying...')
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
            latest = None
            while True:  # Slightly hacky, drop all lines except latest
                inline = self.tty_in.readline()  # type: bytes
                inline = inline.decode()
                inline = inline.strip('\x00')
                if '\n' in inline:
                    inline = inline.strip()
                    latest = inline
                elif latest is not None:
                    break
            inline = latest
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
        # 0b Ls L4 L2 L1 Rs R4 R2 R1
        # xs: sign (0 positive, 1 negative)
        # x4, 2, 1: value
        left_int, right_int = round(cmd[0] / 100.0 * 7.0), round(cmd[1] / 100.0 * 7.0)
        left_sign, right_sign = cmd[0] < 0, cmd[1] < 0
        left_val, right_val = abs(left_int), abs(right_int)
        command_byte = 0x00
        if left_sign:
            command_byte |= 0b10000000
        if right_sign:
            command_byte |= 0b00001000
        command_byte |= (left_val & 0b0111) << 4
        command_byte |= (right_val & 0b0111)
        logging.debug(f'Command: {cmd}')
        logging.debug(f'Left int: {left_int}, right int: {right_int}')
        logging.debug(f'Command byte: {command_byte:08b}')
        # Send command
        try:
            self.tty_out.write(command_byte.to_bytes(1, 'big', signed=False))
        except Exception as e:
            logging.error(f'Error sending command: {e}')
            self.write_errors += 1
            raise e

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
            if self.write_errors > 10:
                logging.error(f'Too many write errors! Re-opening tty_out...')
                self.init_tty_out()
            cmd = self.read_command()
            self.send_command(cmd)
            self.read_response()
        except Exception as e:
            logging.error(f'Error in main loop: {repr(e)}')


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
