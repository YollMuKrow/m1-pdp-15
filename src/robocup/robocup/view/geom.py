import math
from typing import Union, Tuple

from gym.envs.classic_control import rendering as rendering
from gym.envs.classic_control.rendering import FilledPolygon, PolyLine

from robocup.spec.settings import *


np.set_printoptions(threshold=20, precision=3, suppress=True, linewidth=200)


def make_half_circle(radius: float = 10, res: int = 20, filled: bool = True) -> Union[FilledPolygon, PolyLine]:
    """helper function for pyglet renderer"""
    points = []
    for i in range(res + 1):
        ang = math.pi - math.pi * i / res
        points.append((math.cos(ang) * radius, math.sin(ang) * radius))
    if filled:
        return rendering.FilledPolygon(points)
    else:
        return rendering.PolyLine(points, True)


def _add_attrs(geom: Union[FilledPolygon, PolyLine], color: Tuple[int, int, int]) -> None:
    """ help scale the colors from 0-255 to 0.0-1.0 (pyglet renderer) """
    r = color[0]
    g = color[1]
    b = color[2]
    geom.set_color(r / 255., g / 255., b / 255.)


def create_canvas(canvas, window_width: int, window_height: int, c: Tuple[int, int, int]) -> Union[FilledPolygon, PolyLine]:
    rect(canvas, 0, 0, window_width, -window_height, color=BACKGROUND_COLOR)
    return canvas


def rect(canvas, x: float, y: float, width: float, height: float, color: Tuple[int, int, int])\
        -> Union[FilledPolygon, PolyLine]:

    box = rendering.make_polygon([(0, 0), (0, -height), (width, -height), (width, 0)])
    trans = rendering.Transform()
    trans.set_translation(x, y)
    _add_attrs(box, color)
    box.add_attr(trans)
    canvas.add_onetime(box)
    return canvas


def half_circle(canvas, x: float, y: float, r: float, color: Tuple[int, int, int]) -> Union[FilledPolygon, PolyLine]:

    geom = make_half_circle(r)
    trans = rendering.Transform()
    trans.set_translation(x, y)
    _add_attrs(geom, color)
    geom.add_attr(trans)
    canvas.add_onetime(geom)
    return canvas


def circle(canvas, x: float, y: float, r: float, color: Tuple[int, int, int]) -> Union[FilledPolygon, PolyLine]:

    geom = rendering.make_circle(r, res=40)
    trans = rendering.Transform()
    trans.set_translation(x, y)
    _add_attrs(geom, color)
    geom.add_attr(trans)
    canvas.add_onetime(geom)
    return canvas


def rotated_rect(canvas, x_top_left: float, y_top_left: float, x_low_left: float, y_low_left: float,
                 x_low_right: float, y_low_right: float, x_top_right: float,
                 y_top_right: float, color: Tuple[int, int, int]) -> Union[FilledPolygon, PolyLine]:

    box = rendering.make_polygon(
        [(x_top_left, y_top_left), (x_low_left, y_low_left), (x_low_right, y_low_right), (x_top_right, y_top_right)])
    _add_attrs(box, color)
    canvas.add_onetime(box)
    return canvas


class Rectangle:
    def __init__(self, x, y, w, h, c):
        self.x: float = x
        self.y: float = y
        self.w: float = w
        self.h: float = h
        self.c: Tuple[int, int, int] = c

    def display(self, canvas) -> Union[FilledPolygon, PolyLine]:
        return rect(canvas, self.x, self.y,
                    self.w, self.h, color=self.c)
        pass


class Circle:

    def __init__(self, x, y, r, c):
        self.x: float = x
        self.y: float = y
        self.r: float = r
        self.c: Tuple[int, int, int] = c

    def display(self, canvas) -> Union[FilledPolygon, PolyLine]:
        return circle(canvas, self.x, self.y, self.r, color=self.c)
        pass


class RotatedRectangle:

    def __init__(self, x_top_left: float, y_top_left: float, x_low_left: float, y_low_left: float,
                 x_low_right: float, y_low_right: float, x_top_right: float,
                 y_top_right: float, color: Tuple[int, int, int]):
        self.x_top_left: float = x_top_left
        self.y_top_left: float = y_top_left
        self.x_low_left: float = x_low_left
        self.y_low_left: float = y_low_left
        self.x_low_right: float = x_low_right
        self.y_low_right: float = y_low_right
        self.x_top_right: float = x_top_right
        self.y_top_right: float = y_top_right
        self.color: Tuple[int, int, int] = color

    def display(self, canvas) -> Union[FilledPolygon, PolyLine]:
        return rotated_rect(canvas=canvas, x_top_left=self.x_top_left, y_top_left=self.y_top_left,
                            x_low_left=self.x_low_left,
                            y_low_left=self.y_low_left, x_low_right=self.x_low_right, y_low_right=self.y_low_right,
                            x_top_right=self.x_top_right, y_top_right=self.y_top_right, color=self.color)
        pass


class Point:

    def __init__(self, x: float, y: float):
        self._x: float = x
        self._y: float = y

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @x.setter
    def x(self, x) -> None:
        self._x = x

    @y.setter
    def y(self, y) -> None:
        self._y = y
