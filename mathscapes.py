#!/usr/bin/python3

import  cairo
import  math
from    enum import Enum
    
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, theta, c):
        self.theta = theta
        self.c = c

class LineSegment:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

class Ray:
    def __init__(self, p, theta):
        self.p = p
        self.theta = theta

class Ellipse:
    def __init__(self, p, w, h):
        self.p = p
        self.w = w
        self.h = h

class Polygon:
    def __init__(self, points):
        self.points = points

class Tri(Polygon):
    def __init__(self, p1, p2, p3):
        points = [p1, p2, p3]
        super(Tri, self).__init__(points)

class Quad(Polygon):
    def __init__(self, p1, p2, p3, p4):
        points = [p1, p2, p3, p4]
        super(Quad, self).__init__(points)

class Rect(Quad):
    def __init__(self, p, w, h):
        p1 = p
        p2 = Point(p.x + w, p.y)
        p3 = Point(p2.x   , p.y + h)
        p4 = Point(p.x    , p.y + h)
        points = [p1, p2, p3, p4]
        super(Rect, self).__init__(points)

class SurfaceType(Enum):
    PDF     = 1
    PS      = 2
    SVG     = 3

def map(value, start1, stop1, start2, stop2):
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

class Device:
    def __init__(self, width, height, surfaceType = SurfaceType.SVG):
        self.width          = width 
        self.height         = height
        self.surfaceType    = surfaceType
        self.fileName       = 'drawing'

        # Create Surface
        if self.surfaceType == SurfaceType.PDF:
            self.surface = cairo.PDFSurface( self.fileName + '.pdf',
                                             self.width,
                                             self.height )
        elif self.surfaceType == SurfaceType.PS:
            self.surface = cairo.PSSurface( self.fileName + '.ps',
                                             self.width,
                                             self.height )
        elif self.surfaceType == SurfaceType.SVG:
            self.surface = cairo.SVGSurface( self.fileName + '.svg',
                                             self.width,
                                             self.height )
        else:
            self.surface = None

        # Create Context
        self.context = cairo.Context(self.surface)

        self.context.scale(self.width, self.height)

        self._color  = (0,0,0,1)
        self._stroke = 1/self.width
        self.origin = Point(0,0)
        self._textSize = 12/self.width
    
    def translate(self, x, y):
        self.origin.x += x
        self.origin.y += y

    def _scaleToWidth(self, x):
        return map(x, -self.origin.x, self.width - self.origin.x, 0, 1)
    
    def _scaleToHeight(self, y):
        return map(y, -self.origin.y, self.height - self.origin.y, 0, 1)

    def color(self, r,g,b,a):
        self._color = (r,g,b,a)

    def stroke(self, _stroke):
        self._stroke = self._scaleToWidth(_stroke)

    def textSize(self, size):
        self._textSize = size/self.width

    def draw(self, geometry):
        if geometry.__class__.__name__ == 'Point':
            self._drawPoint(geometry)
        if geometry.__class__.__name__ == 'LineSegment':
            self._drawLineSegment(geometry)
        if geometry.__class__.__name__ == 'Line':
            self._drawLine(geometry)
        if geometry.__class__.__name__ == 'Ray':
            self._drawRay(geometry)

    def _drawPoint(self, p):
        r, g, b, a = self._color
        x, y = self._scaleToWidth(p.x), self._scaleToHeight(p.y)
        self.context.set_source_rgba(r,g,b,a)
        self.context.arc(x, y, self._stroke, 0, 2 * math.pi)
        self.context.fill()

    def _drawLineSegment(self, lineSegment):
        r,g,b,a = self._color
        self.context.set_source_rgba(r,g,b,a)
        self.context.set_line_width(self._stroke)
        x, y = self._scaleToWidth(lineSegment.p1.x), self._scaleToHeight(lineSegment.p1.y)
        self.context.move_to(x, y)
        x, y = self._scaleToWidth(lineSegment.p2.x), self._scaleToHeight(lineSegment.p2.y)
        self.context.line_to(x, y)
        self.context.stroke()
    
    def _drawLine(self, line):
        
        if math.tan(line.theta) != math.tan(math.pi/2):
            x = -self.origin.x
            p1 = Point(x, math.tan(line.theta) * x + line.c)
            x = self.width - self.origin.x
            p2 = Point(x, math.tan(line.theta) * x + line.c)
        else:
            y = -self.origin.y
            p1 = Point(-line.c + (y)/math.tan(line.theta), y)
            y = self.height - self.origin.y
            p2 = Point(-line.c + (y)/math.tan(line.theta), y)
        self._drawLineSegment(LineSegment(p1,p2))
    
    def _drawRay(self, ray):
        pass

    def text(self, txt, loc):
        r,g,b,a = self._color
        self.context.set_source_rgba(r,g,b,a)
        self.context.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.context.set_font_size(self._textSize)
        self.context.move_to(self._scaleToWidth(loc.x), self._scaleToHeight(loc.y))
        self.context.show_text(txt)
