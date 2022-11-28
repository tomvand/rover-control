"""uart_record.py
Goal: record raw video from a tty. (Re-)open the tty if the connection is temporarily unavailable. Add timestamps to
video frames.
"""
import serial
import time
import cv2
import numpy as np
import os

from .stereoboard_tools import readPartOfImage, determine_image_and_line_length, fill_image_array

import logging
logging = logging.getLogger(__name__)


class UartRecorder(object):
    def __init__(self, tty, baud=921600):
        for i in range(0, 9999+1):
            try:
                dir = f'./imgs/{i:04d}'
                os.makedirs(dir, exist_ok=False)
                self.dir = dir
                break
            except Exception as e:
                pass
        assert self.dir is not None

        self.tty_name = tty
        self.tty_baud = baud
        self.tty = None

        self.serial_open()

        self.current_buffer = []
        self.imgYUV = None
        self.imgBGR = None

    def run(self):
        # Adapted from color_viz.py
        try:
            self.current_buffer, location, endOfImagesFound = readPartOfImage(self.tty, self.current_buffer)
            start_position = location[0]
            end_position = location[1]
            if endOfImagesFound > 0:
                sync1, length, line_length, line_count = determine_image_and_line_length(
                    self.current_buffer[start_position:end_position])
                data = fill_image_array(sync1, self.current_buffer[start_position:end_position],
                                        line_length, line_count)
                self.current_buffer = self.current_buffer[end_position::]
                if end_position - start_position >= 128:
                    self.imgYUV = np.zeros((line_count, int(line_length / 2), 3), dtype="uint8")
                    self.imgYUV[:, :, 0] = data[:, 1::2]
                    self.imgYUV[:, 0::2, 1] = data[:, ::4]
                    self.imgYUV[:, 1::2, 1] = data[:, ::4]
                    self.imgYUV[:, ::2, 2] = data[:, 2::4]
                    self.imgYUV[:, 1::2, 2] = data[:, 2::4]

                    # Create a color image
                    self.imgBGR = cv2.cvtColor(self.imgYUV, cv2.COLOR_YUV2BGR)
                    # Save timestamped image
                    filename = f'{time.time():.3f}.png'
                    cv2.imwrite(os.path.join(self.dir, filename), self.imgBGR)
        except (serial.SerialException, OSError) as e:
            logging.error(f'Serial error: {e}, reopening...')
            self.serial_open()
        except Exception as e:
            logging.error(f'Unexpected error: {e}')
            raise

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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('tty', default='/dev/ttyCAM0')
    parser.add_argument('--baud', type=int, default=921600)
    args = parser.parse_args()

    rec = UartRecorder(**vars(args))
    while True:
        rec.run()
