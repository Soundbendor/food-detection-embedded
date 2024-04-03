"""Minimal example of reading a single line."""

import gpiod

from gpiod.line import Direction


def get_line_value(chip_path, line_offset):
    with gpiod.request_lines(
        chip_path,
        consumer="get-line-value",
        config={line_offset: gpiod.LineSettings(direction=Direction.INPUT)},
    ) as request:
        value = request.get_value(line_offset)
        print("{}={}".format(line_offset, value))


if __name__ == "__main__":
    while True:
    	try:
        	get_line_value("/dev/gpiochip4", 17)
    	except OSError as ex:
        	print(ex, "\nCustomise the example configuration to suit your situation")

