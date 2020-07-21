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
from adafruit_display_shapes.line import Line


class Sparkline(displayio.Group):
    def __init__(
        self,
        width,
        height,
        max_items,
        yMin=None,  # None = autoscaling
        yMax=None,  # None = autoscaling
        x=0,
        y=0,
        color=0xFFFFFF,  # line color, default is WHITE
    ):

        # define class instance variables
        self.width = width  # in pixels
        self.height = height  # in pixels
        self.color = color  #
        self._max_items = max_items  # maximum number of items in the list
        self._spark_list = []  # list containing the values
        self.yMin = yMin  # minimum of y-axis (None: autoscale)
        self.yMax = yMax  # maximum of y-axis (None: autoscale)
        self.yBottom = yMin  # yBottom: The actual minimum value of the vertical scale, will be updated if autorange
        self.yTop = yMax  # yTop: The actual minimum value of the vertical scale, will be updated if autorange
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

        y2 = int(self.height * (yTop - value) / (yTop - yBottom))
        y1 = int(self.height * (yTop - last_value) / (yTop - yBottom))
        self.append(Line(x1, y1, x2, y2, self.color))  # plot the line

    def update(self):
        # What to do if there is 0 or 1 element?

        # get the y range
        if self.yMin == None:
            self.yBottom = min(self._spark_list)
        else:
            self.yBottom = self.yMin

        if self.yMax == None:
            self.yTop = max(self._spark_list)
        else:
            self.yTop = self.yMax

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

                    if (self.yBottom <= last_value <= self.yTop) and (
                        self.yBottom <= value <= self.yTop
                    ):  # both points are in range, plot the line
                        self._plotLine(
                            x1, last_value, x2, value, self.yBottom, self.yTop
                        )

                    else:  # at least one point is out of range, clip one or both ends the line
                        if ((last_value > self.yTop) and (value > self.yTop)) or (
                            (last_value < self.yBottom) and (value < self.yBottom)
                        ):
                            # both points are on the same side out of range: don't draw anything
                            pass
                        else:
                            xintBottom = self._xintercept(
                                x1, last_value, x2, value, self.yBottom
                            )  # get possible new x intercept points
                            xintTop = self._xintercept(
                                x1, last_value, x2, value, self.yTop
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
                                        adj_last_value = self.yBottom  # y1
                                    if xintTop <= x2:  # top is clipped
                                        adj_x2 = xintTop
                                        adj_value = self.yTop  # y2
                                else:  # slope is negative
                                    if xintTop >= x1:  # top is clipped
                                        adj_x1 = xintTop
                                        adj_last_value = self.yTop  # y1
                                    if xintBottom <= x2:  # bottom is clipped
                                        adj_x2 = xintBottom
                                        adj_value = self.yBottom  # y2

                                self._plotLine(
                                    adj_x1,
                                    adj_last_value,
                                    adj_x2,
                                    adj_value,
                                    self.yBottom,
                                    self.yTop,
                                )

                last_value = value  # store value for the next iteration

    def values(self):
        return self._spark_list
