import os

import logging
logging = logging.getLogger(__name__)


class Led(object):
    def __init__(self):
        self.led = False
        self.is_on = False
        try:
            # Detect led pseudo-file present and writable
            with open('/sys/class/leds/led0/trigger', 'wt') as f:
                pass
            os.system('echo none > /sys/class/leds/led0/trigger')
            self.led = True
        except Exception as e:
            logging.info(f'Could not open led file: {e}. Ignoring.')

    def __del__(self):
        try:
            if self.led:
                os.system('echo mmc0 > /sys/class/leds/led0/trigger')
        except:
            pass

    def toggle(self):
        if self.led:
            self.is_on = not self.is_on
            os.system(f'echo {"1" if self.is_on else "0"} > /sys/class/leds/led0/brightness')
