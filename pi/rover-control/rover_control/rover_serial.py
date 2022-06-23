import serial
import time

import logging
logging = logging.getLogger(__name__)


class RoverSerial(object):
    def __init__(self, tty, baud=9600):
        self.tty_name = tty
        self.tty_baud = baud
        self.tty = None

        self.serial_open()

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
            self.tty.write(command_byte.to_bytes(1, 'big', signed=False))
        except Exception as e:
            logging.error(f'Error sending command: {e}')
            raise e

    def read_response(self):
        try:
            inline = self.tty.readline()  # type: bytes
            inline = inline.decode('ascii')
            inline = inline.strip('\x00')
            inline = inline.strip()
            if len(inline) != 0:
                logging.info(f"Arduino response: {inline}")
        except Exception as e:
            logging.error(f"Error reading Arduino response! {e}")
            raise e

    def serial_open(self):
        # Try closing the tty first
        try:
            self.tty.close()
        except:
            pass
        # Loop while trying to open tty
        while True:
            try:
                self.tty = serial.Serial(
                    port=self.tty_name,
                    baudrate=self.tty_baud,
                    timeout=0.001
                )
                break
            except Exception as e:
                logging.error(f'Unable to open {self.tty_name}: {e}, retrying...')
                time.sleep(2)
