# SPDX-FileCopyrightText: 2020 Kevin Matocha
#
# SPDX-License-Identifier: MIT

# class of sparklines in CircuitPython

# See the bottom for a code example using the `sparkline` Class.

# # File: display_shapes_sparkline.py
# A sparkline is a scrolling line graph, where any values added to sparkline using `
# add_value` are plotted.
#
# The `sparkline` class creates an element suitable for adding to the display using
# `display.show(mySparkline)`
# or adding to a `displayio.Group` to be displayed.
#
# When creating the sparkline, identify the number of `max_items` that will be
# included in the graph. When additional elements are added to the sparkline and
# the number of items has exceeded max_items, any excess values are removed from
# the left of the graph, and new values are added to the right.
"""
`sparkline`
================================================================================

Various common shapes for use with displayio - Sparkline!


* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
try:
    from typing import List, Optional
except ImportError:
    pass

# pylint: disable=too-many-instance-attributes

import displayio
from adafruit_display_shapes.line import Line


class Sparkline(displayio.Group):
    # pylint: disable=too-many-arguments
    """A sparkline graph.

    :param width: Width of the sparkline graph in pixels
    :param height: Height of the sparkline graph in pixels
    :param max_items: Maximum number of values housed in the sparkline
    :param y_min: Lower range for the y-axis.  Set to None for autorange.
    :param y_max: Upper range for the y-axis.  Set to None for autorange.
    :param x: X-position on the screen, in pixels
    :param y: Y-position on the screen, in pixels
    :param color: Line color, the default value is 0xFFFFFF (WHITE)
    """

    def __init__(
        self,
        width: int,
        height: int,
        max_items: int,
        y_min: Optional[float] = None,  # None = autoscaling
        y_max: Optional[float] = None,  # None = autoscaling
        x: float = 0.0,
        y: float = 0.0,
        color: Optional[int] = 0xFFFFFF,  # line color, default is WHITE
    ) -> None:

        # define class instance variables
        self.width = width  # in pixels
        self.height = height  # in pixels
        self.color = color  #
        self._max_items = max_items  # maximum number of items in the list
        self._spark_list: List[float] = []  # list containing the values
        self.y_min = y_min  # minimum of y-axis (None: autoscale)
        self.y_max = y_max  # maximum of y-axis (None: autoscale)
        self.y_bottom = y_min
        # y_bottom: The actual minimum value of the vertical scale, will be
        # updated if autorange
        self.y_top = y_max
        # y_top: The actual minimum value of the vertical scale, will be
        # updated if autorange
        self._x = x
        self._y = y

        super().__init__(x=x, y=y)  # self is a group of lines

    def clear_values(self):
        """Removes all values from the _spark_list list and removes all lines in the group"""

        for _ in range(len(self)):  # remove all items from the current group
            self.pop()
        self._spark_list = []  # empty the list

    def add_value(self, value: Optional[float]):
        """Add a value to the sparkline.
        :param value: The value to be added to the sparkline
        """

        if value is not None:
            if (
                len(self._spark_list) >= self._max_items
            ):  # if list is full, remove the first item
                self._spark_list.pop(0)
            self._spark_list.append(value)
            self.update()

    # pylint: disable=no-else-return
    @staticmethod
    def _xintercept(
        x_1: float, y_1: float, x_2: float, y_2: float, horizontal_y: float
    ) -> Optional[int]:  # finds intercept of the line and a horizontal line at horizontalY
        slope = (y_2 - y_1) / (x_2 - x_1)
        b = y_1 - slope * x_1

        if slope == 0 and y_1 != horizontal_y:  # does not intercept horizontalY
            return None
        else:
            xint = (
                horizontal_y - b
            ) / slope  # calculate the x-intercept at position y=horizontalY
            return int(xint)

    def _plotline(self, x_1: int, last_value: int, x_2: int, value: int, y_bottom: int, y_top: int):

        y_2 = int(self.height * (y_top - value) / (y_top - y_bottom))
        y_1 = int(self.height * (y_top - last_value) / (y_top - y_bottom))
        self.append(Line(x_1, y_1, x_2, y_2, self.color))  # plot the line

    # pylint: disable= too-many-branches, too-many-nested-blocks

    def update(self):
        """Update the drawing of the sparkline."""

        # get the y range
        if self.y_min is None:
            self.y_bottom = min(self._spark_list)
        else:
            self.y_bottom = self.y_min

        if self.y_max is None:
            self.y_top = max(self._spark_list)
        else:
            self.y_top = self.y_max

        # Guard for y_top and y_bottom being the same
        if self.y_top == self.y_bottom:
            self.y_bottom -= 10
            self.y_top += 10

        if len(self._spark_list) > 2:
            xpitch = (self.width - 1) / (
                len(self._spark_list) - 1
            )  # this is a float, only make int when plotting the line

            for _ in range(len(self)):  # remove all items from the current group
                self.pop()

            for count, value in enumerate(self._spark_list):
                if count == 0:
                    pass  # don't draw anything for a first point
                else:
                    x_2 = int(xpitch * count)
                    x_1 = int(xpitch * (count - 1))

                    if (self.y_bottom <= last_value <= self.y_top) and (
                        self.y_bottom <= value <= self.y_top
                    ):  # both points are in range, plot the line
                        self._plotline(
                            x_1, last_value, x_2, value, self.y_bottom, self.y_top
                        )

                    else:  # at least one point is out of range, clip one or both ends the line
                        if ((last_value > self.y_top) and (value > self.y_top)) or (
                            (last_value < self.y_bottom) and (value < self.y_bottom)
                        ):
                            # both points are on the same side out of range: don't draw anything
                            pass
                        else:
                            xint_bottom = self._xintercept(
                                x_1, last_value, x_2, value, self.y_bottom
                            )  # get possible new x intercept points
                            xint_top = self._xintercept(
                                x_1, last_value, x_2, value, self.y_top
                            )  # on the top and bottom of range

                            if (xint_bottom is None) or (
                                xint_top is None
                            ):  # out of range doublecheck
                                pass
                            else:
                                # Initialize the adjusted values as the baseline
                                adj_x_1 = x_1
                                adj_last_value = last_value
                                adj_x_2 = x_2
                                adj_value = value

                                if value > last_value:  # slope is positive
                                    if xint_bottom >= x_1:  # bottom is clipped
                                        adj_x_1 = xint_bottom
                                        adj_last_value = self.y_bottom  # y_1
                                    if xint_top <= x_2:  # top is clipped
                                        adj_x_2 = xint_top
                                        adj_value = self.y_top  # y_2
                                else:  # slope is negative
                                    if xint_top >= x_1:  # top is clipped
                                        adj_x_1 = xint_top
                                        adj_last_value = self.y_top  # y_1
                                    if xint_bottom <= x_2:  # bottom is clipped
                                        adj_x_2 = xint_bottom
                                        adj_value = self.y_bottom  # y_2

                                self._plotline(
                                    adj_x_1,
                                    adj_last_value,
                                    adj_x_2,
                                    adj_value,
                                    self.y_bottom,
                                    self.y_top,
                                )

                last_value = value  # store value for the next iteration

    def values(self):
        """Returns the values displayed on the sparkline."""

        return self._spark_list
