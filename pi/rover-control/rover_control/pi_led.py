import logging
logging = logging.getLogger(__name__)


class Led(object):
    def __init__(self):
        self.led = None
        self.is_on = False
        try:
            # Disable mmc trigger
            with open('/sys/class/leds/led0/trigger', 'wt') as f:
                f.write('none')
            # Open brightness control
            self.led = open('/sys/class/leds/led0/brightness', 'wt')
        except Exception as e:
            logging.info(f'Could not open led file: {e}. Ignoring.')

    def __del__(self):
        try:
            self.led.close()
        except:
            pass

        try:
            with open('/sys/class/leds/led0/trigger', 'wt') as f:
                f.write('mmc0')
        except:
            pass

    def toggle(self):
        if self.led is not None:
            self.is_on = not self.is_on
            self.led.write('1' if self.is_on else '0')
