import time
import serial
import sys

import logging
logging = logging.getLogger(__name__)

sys.path.insert(1, 'pprzlink/pprzlink/lib/v2.0/python')
from pprzlink import messages_xml_map
from pprzlink.pprz_transport import PprzTransport


class DronePprzlink(object):
    def __init__(self, tty, messages_xml='pprzlink/messages.xml', baud=115200):
        self.tty_name = tty
        self.tty_baud = baud
        self.tty = None

        self.serial_open()

        self.transport = PprzTransport('intermcu')
        messages_xml_map.parse_messages(messages_xml)

        self.callback = lambda sender_id, msg: 0

    def read(self):
        while True:
            # Read character
            while True:
                try:
                    c = self.tty.read(1)
                    break
                except Exception as e:
                    logging.error(f'Error reading from {self.tty}: {e}')
                    raise e
            if len(c) < 1:
                break  # no more characters

            # Parse character
            if self.transport.parse_byte(c):
                # Message complete
                try:
                    (sender_id, receiver_id, component_id, msg) = self.transport.unpack()
                except ValueError as e:
                    logging.warning("Ignoring unknown message, %s" % e)
                else:
                    logging.debug(msg)
                    return msg
        return None

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


if __name__ == '__main__':
    drone = DronePprzlink('/dev/ttyACM0')
    while True:
        msg = drone.read()
        if msg is not None:
            print(msg)
