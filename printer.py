# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import random

import numpy

from PyQt4.QtGui import QImage, QPainter, QBrush, QPen, QColor, QLinearGradient, qRgb
from PyQt4.QtCore import QPointF
from PyQt4.Qt import Qt

import serialize
from utils import gradient

def print_galaxy(vertices, edges, edge=False, image_size=3200, color_type='region'):
    
    #parse options
    x_index = 0
    y_index = 1
    if(edge):
        y_index = 1
    
    output_image = QImage(image_size, image_size, QImage.Format_ARGB32_Premultiplied)
    output_image.fill(Qt.black)
    painter = QPainter(output_image)
    painter.setRenderHint(QPainter.Antialiasing)
    
    #first we have to scale/translate the painter to fit all the stars in the image
    biggest_coord = find_biggest_coord(vertices)
    size_ratio = image_size / (biggest_coord * 2 * 1.03)
    
    #translate the origin into the center of the image, then scale by size_ratio
    painter.translate(image_size/2, image_size/2)
    painter.scale(size_ratio, size_ratio)
    
    pen = QPen(Qt.gray)
    pen.setWidthF(1)
    painter.setPen(pen)
    
    #draw all edges
    for v1, neighbors in edges.iteritems():
        for v2 in neighbors:
            x1 = vertices[v1]['position'][x_index]
            y1 = vertices[v1]['position'][y_index]
            x2 = vertices[v2]['position'][x_index]
            y2 = vertices[v2]['position'][y_index]
            
            painter.drawLine(x1,y1,x2,y2)
    
    
    #draw all vertices
    for v in vertices:
        vertex_color = get_color(v, color_type)
        
        painter.setPen(vertex_color)
        painter.setBrush(QBrush(vertex_color))
        
        center = QPointF(v['position'][x_index],v['position'][y_index])
        
        painter.drawEllipse(center, 5,5)
        
    painter.end()
    output_image.save("galaxy.png")
    
def find_biggest_coord(vertices):
    return max(max(v['position']) for v in vertices)





def get_color(v, color_type):
    if(color_type == 'region'):
        return color_for_group(v['region'])
    elif(color_type == 'security'):
        return color_for_normalized_float(0.6)
    elif(color_type == 'betweenness'):
        return color_for_normalized_float(v['betweenness'])


def color_for_group(group):
    random.seed(group * group + 2*group + 17)
    
    return QColor(qRgb(
        random.randint(64, 255),
        random.randint(64, 255),
        random.randint(64, 255),
        ))
    
#input: float between 0 and 1
#output: color, smoothly going from red to yellow to green to cyan
gradient = gradient.Gradient()
gradient.add_entry(0.0, numpy.array([255, 0, 0], dtype=numpy.float32))
gradient.add_entry(0.5, numpy.array([255, 255, 0], dtype=numpy.float32))
gradient.add_entry(0.75, numpy.array([0, 255, 0], dtype=numpy.float32))
gradient.add_entry(1.0, numpy.array([0, 255, 255], dtype=numpy.float32))

def color_for_normalized_float(val):
    r,g,b = tuple(gradient.interpolate(val))
    return QColor(qRgb(r,g,b))
    
    
    
    
    
    
    
    
    
    
    
    