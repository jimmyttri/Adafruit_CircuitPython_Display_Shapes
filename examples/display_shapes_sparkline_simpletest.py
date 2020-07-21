# class of sparklines in CircuitPython
# created by Kevin Matocha - Copyright 2020 (C)

# See the bottom for a code example using the `sparkline` Class.

# # File: display_shapes_sparkline.py
# A sparkline is a scrolling line graph, where any values added to sparkline using `add_value` are plotted.
#
# The `sparkline` class creates an element suitable for adding to the display using `display.show(mySparkline)`
# or adding to a `displayio.Group` to be displayed.
#
# When creating the sparkline, identify the number of `max_items` that will be included in the graph.
# When additional elements are added to the sparkline and the number of items has exceeded max_items,
# any excess values are removed from the left of the graph, and new values are added to the right.


# The following is an example that shows the

# setup display
# instance sparklines
# add to the display
# Loop the following steps:
# 	add new values to sparkline `add_value`
# 	update the sparklines `update`

import board
import displayio
import terminalio
import random
import time
from adafruit_display_shapes.sparkline import Sparkline

from adafruit_display_text import label


# from sparkline import sparkline # use this if sparkline.py is used to define the sparkline Class

if "DISPLAY" not in dir(board):
    # Setup the LCD display with driver
    from adafruit_ili9341 import ILI9341

    displayio.release_displays()

    # setup the SPI bus
    spi = board.SPI()
    tft_cs = board.D9  # arbitrary, pin not used
    tft_dc = board.D10
    tft_backlight = board.D12
    tft_reset = board.D11

    while not spi.try_lock():
        spi.configure(baudrate=32000000)
        pass
    spi.unlock()

    display_bus = displayio.FourWire(
        spi,
        command=tft_dc,
        chip_select=tft_cs,
        reset=tft_reset,
        baudrate=32000000,
        polarity=1,
        phase=1,
    )

    print("spi.frequency: {}".format(spi.frequency))

    # Number of pixels in the display
    DISPLAY_WIDTH = 320
    DISPLAY_HEIGHT = 240

    # create the display
    display = ILI9341(
        display_bus,
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        rotation=180,
        auto_refresh=True,
        native_frames_per_second=90,
    )

    # reset the display to show nothing.
    display.show(None)
else:
    # built-in display
    display = board.DISPLAY

##########################################
# Create background bitmaps and sparklines
##########################################

# Baseline size of the sparkline chart, in pixels.
chartWidth = display.width
chartHeight = display.height


# mySparkline1 uses a vertical y range between 0 to 10 and will contain a maximum of 40 items
mySparkline1 = Sparkline(
    width=chartWidth, height=chartHeight, max_items=40, yMin=0, yMax=10, x=0, y=0
)


# Create a group to hold the sparkline and append the sparkline into the group (myGroup)
#
# Note: In cases where display elements will overlap, then the order the elements are added to the
# group will set which is on top.  Latter elements are displayed on top of former elemtns.
myGroup = displayio.Group(max_size=1)

myGroup.append(mySparkline1)


# Display myGroup that contains the sparkline
display.show(myGroup)


# Start the main loop
while True:

    # add_value: add a new value to a sparkline
    # Note: The y-range for mySparkline1 is set to 0 to 10, so all these random
    # values (between 0 and 10) will fit within the visible range of this sparkline
    mySparkline1.add_value(random.uniform(0, 10))

    display.auto_refresh = False
    mySparkline1.update()
    display.auto_refresh = True

    # The display seems to be less jittery if a small sleep time is provided
    # You can adjust this to see if it has any effect
    time.sleep(0.01)
