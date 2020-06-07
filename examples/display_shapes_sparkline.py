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

import displayio


class sparkline(displayio.Group):
    def __init__(
        self,
        width,
        height,
        max_items,
        yMin=None,  # None = autoscaling
        yMax=None,  # None = autoscaling
        line_color=0xFFFFFF,  # default = WHITE
        x=0,
        y=0,
    ):

        # define class instance variables
        self.width = width  # in pixels
        self.height = height  # in pixels
        self.line_color = line_color  #
        self._max_items = max_items  # maximum number of items in the list
        self._spark_list = []  # list containing the values
        self.yMin = yMin  # minimum of y-axis (None: autoscale)
        self.yMax = yMax  # maximum of y-axis (None: autoscale)
        self._x = x
        self._y = y

        super().__init__(
            max_size=self._max_items - 1, x=x, y=y
        )  # self is a group of lines

    def add_value(self, value):
        if value is not None:
            if (
                len(self._spark_list) >= self._max_items
            ):  # if list is full, remove the first item
                self._spark_list.pop(0)
            self._spark_list.append(value)
            # self.update()

    @staticmethod
    def _xintercept(
        x1, y1, x2, y2, horizontalY
    ):  # finds intercept of the line and a horizontal line at horizontalY
        slope = (y2 - y1) / (x2 - x1)
        b = y1 - slope * x1

        if slope == 0 and y1 != horizontalY:  # does not intercept horizontalY
            return None
        else:
            xint = (
                horizontalY - b
            ) / slope  # calculate the x-intercept at position y=horizontalY
            return int(xint)

    def _plotLine(self, x1, last_value, x2, value, yBottom, yTop):

        from adafruit_display_shapes.line import Line

        y2 = int(self.height * (yTop - value) / (yTop - yBottom))
        y1 = int(self.height * (yTop - last_value) / (yTop - yBottom))
        self.append(Line(x1, y1, x2, y2, self.line_color))  # plot the line

    def update(self):
        # What to do if there is 0 or 1 element?

        # get the y range
        if self.yMin == None:
            yBottom = min(self._spark_list)
        else:
            yBottom = self.yMin

        if self.yMax == None:
            yTop = max(self._spark_list)
        else:
            yTop = self.yMax

        if len(self._spark_list) > 2:
            xpitch = self.width / (
                len(self._spark_list) - 1
            )  # this is a float, only make int when plotting the line

            for i in range(len(self)):  # remove all items from the current group
                self.pop()

            for count, value in enumerate(self._spark_list):
                if count == 0:
                    pass  # don't draw anything for a first point
                else:
                    x2 = int(xpitch * count)
                    x1 = int(xpitch * (count - 1))

                    # print("x1: {}, x2: {}".format(x1,x2))

                    if (yBottom <= last_value <= yTop) and (
                        yBottom <= value <= yTop
                    ):  # both points are in range, plot the line
                        self._plotLine(x1, last_value, x2, value, yBottom, yTop)

                    else:  # at least one point is out of range, clip one or both ends the line
                        if ((last_value > yTop) and (value > yTop)) or (
                            (last_value < yBottom) and (value < yBottom)
                        ):
                            # both points are on the same side out of range: don't draw anything
                            pass
                        else:
                            xintBottom = self._xintercept(
                                x1, last_value, x2, value, yBottom
                            )  # get possible new x intercept points
                            xintTop = self._xintercept(
                                x1, last_value, x2, value, yTop
                            )  # on the top and bottom of range

                            if (xintBottom is None) or (
                                xintTop is None
                            ):  # out of range doublecheck
                                pass
                            else:
                                # Initialize the adjusted values as the baseline
                                adj_x1 = x1
                                adj_last_value = last_value
                                adj_x2 = x2
                                adj_value = value

                                if value > last_value:  # slope is positive
                                    if xintBottom >= x1:  # bottom is clipped
                                        adj_x1 = xintBottom
                                        adj_last_value = yBottom  # y1
                                    if xintTop <= x2:  # top is clipped
                                        adj_x2 = xintTop
                                        adj_value = yTop  # y2
                                else:  # slope is negative
                                    if xintTop >= x1:  # top is clipped
                                        adj_x1 = xintTop
                                        adj_last_value = yTop  # y1
                                    if xintBottom <= x2:  # bottom is clipped
                                        adj_x2 = xintBottom
                                        adj_value = yBottom  # y2

                                self._plotLine(
                                    adj_x1,
                                    adj_last_value,
                                    adj_x2,
                                    adj_value,
                                    yBottom,
                                    yTop,
                                )

                last_value = value  # store value for the next iteration

    def values(self):
        return self._spark_list


# The following is an example that shows the

# setup display
# instance sparklines
# add to the display
# Loop the following steps:
# 	add new values to sparkline `add_value`
# 	update the sparklines `update`

import board
import displayio
import random
import time
from adafruit_ili9341 import ILI9341

# from sparkline import sparkline # use this if sparkline.py is used to define the sparkline Class


# Setup the LCD display

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

##########################################
# Create background bitmaps and sparklines
##########################################

# Baseline size of the sparkline chart, in pixels.
chartWidth = 50
chartHeight = 50

# Setup the first bitmap and sparkline
palette = displayio.Palette(1)  # color palette used for bitmap (one color)
palette[0] = 0x444411

bitmap = displayio.Bitmap(chartWidth, chartHeight, 1)  # create a bitmap
tileGrid = displayio.TileGrid(
    bitmap, pixel_shader=palette, x=10, y=10
)  # Add the bitmap to tilegrid
mySparkline = sparkline(
    width=chartWidth, height=chartHeight, max_items=40, yMin=-1, yMax=1.25, x=10, y=10
)
# mySparkline uses a vertical y range between -1 to +1.25 and will contain a maximum of 40 items

# Setup the second bitmap and sparkline
palette2 = displayio.Palette(1)  # color palette used for bitmap2 (one color)
palette2[0] = 0x0000FF

bitmap2 = displayio.Bitmap(chartWidth * 2, chartHeight * 2, 1)  # create bitmap2
tileGrid2 = displayio.TileGrid(
    bitmap2, pixel_shader=palette2, x=150, y=10
)  # Add bitmap2 to tilegrid2
mySparkline2 = sparkline(
    width=chartWidth * 2,
    height=chartHeight * 2,
    max_items=10,
    yMin=0,
    yMax=1,
    x=150,
    y=10,
    line_color=0xFF00FF,
)
# mySparkline2 uses a vertical y range between 0 to 1, and will contain a maximum of 10 items

# Setup the third bitmap and sparkline
palette3 = displayio.Palette(1)  # color palette used for bitmap (one color)
palette3[0] = 0x11FF44
bitmap3 = displayio.Bitmap(DISPLAY_WIDTH, chartHeight * 2, 1)  # create bitmap3
tileGrid3 = displayio.TileGrid(
    bitmap3, pixel_shader=palette3, x=0, y=120
)  # Add bitmap3 to tilegrid3
mySparkline3 = sparkline(
    width=DISPLAY_WIDTH,
    height=chartHeight * 2,
    max_items=20,
    x=0,
    y=120,
    line_color=0xFFFFFF,
)
# mySparkline3 will contain a maximum of 20 items
# since yMin and yMax are not specified, mySparkline3 uses autoranging for both the top and bottom ranges.
# Note: Any unspecified edge limit (yMin, yMax) will autorange that edge based on the data in the list.


# Create a group to hold the three bitmap TileGrids and the three sparklines and
# append them into the group (myGroup)
#
# Note: In cases where display elements will overlap, then the order the elements are added to the
# group will set which is on top.  Latter elements are displayed on top of former elemtns.
myGroup = displayio.Group(max_size=8)
myGroup.append(tileGrid)
myGroup.append(mySparkline)

myGroup.append(tileGrid2)
myGroup.append(mySparkline2)

myGroup.append(tileGrid3)
myGroup.append(mySparkline3)


# Display myGroup that contains all the bitmap TileGrids and sparklines
display.show(myGroup)

# Start the main loop
while True:

    # add a new random value to each sparkline
    mySparkline.add_value(random.uniform(0, 1))

    mySparkline2.add_value(random.uniform(-1, 2))
    # Note: For mySparline2, the random value will sometimes
    # be out of the y-range to exercise the top and bottom clipping

    mySparkline3.add_value(random.uniform(0, 1))

    # Turn off the display refresh while updating the sparklines
    display.auto_refresh = False

    # Update the drawings for all three sparklines
    mySparkline.update()
    mySparkline2.update()
    mySparkline3.update()

    # Turn on the display refreshing
    display.auto_refresh = True

    # The display seems to be less jittery if a small sleep time is provided
    time.sleep(0.1)
