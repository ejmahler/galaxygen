
import argparse

from PyQt4.QtGui import QImage, QPainter, QBrush, QPen
from PyQt4.QtCore import QPointF

#global enums
from PyQt4.Qt import Qt

import serialize

def print_galaxy_from_file(filename, edge):
    star_array, edge_data = serialize.load(filename)
    
    if(edge):
        y_index=2
    else:
        y_index=1
    
    print_galaxy(star_array, edge_data, y_index=y_index)


def print_galaxy(vertices, edges, x_index=0, y_index=1, image_size=2400):
    
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
    
    
    painter.setPen(Qt.red)
    painter.setBrush(QBrush(Qt.red))
    
    #draw all vertices
    for v in vertices:
        center = QPointF(v['position'][x_index],v['position'][y_index])
        
        painter.drawEllipse(center, 5,5)
        
    painter.end()
    output_image.save("galaxy.png")
    
def find_biggest_coord(vertices):
    return max(max(v['position']) for v in vertices)


if(__name__ == '__main__'):
    parser = argparse.ArgumentParser('Takes an existing star data set and generates an image for it')
    parser.add_argument('-f','--filename', help="File name to load and save star data to and from", type=str, default='stars.json')
    parser.add_argument('-e','--edge', help="Print the galaxy edge-on instead of top-down", action='store_true')
    
    args = parser.parse_args()
    
    kwargs = {}
    if(args.filename is not None):
        kwargs['filename'] = args.filename
    kwargs['edge'] = args.edge == True
        
        
    print_galaxy_from_file(**kwargs)