
from PyQt4.QtGui import QImage, QPainter, QBrush, QPen
from PyQt4.QtCore import QPointF

#global enums
from PyQt4.Qt import Qt


image_size = 2400
def print_galaxy(vertices, edges, x_index=0, y_index=1):
    
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
            x1 = vertices[v1][x_index]
            y1 = vertices[v1][y_index]
            x2 = vertices[v2][x_index]
            y2 = vertices[v2][y_index]
            
            painter.drawLine(x1,y1,x2,y2)
    
    
    painter.setPen(Qt.red)
    painter.setBrush(QBrush(Qt.red))
    
    #draw all vertices
    for v in vertices:
        center = QPointF(v[x_index],v[y_index])
        
        painter.drawEllipse(center, 5,5)
        
    painter.end()
    output_image.save("galaxy.png")
    
def find_biggest_coord(vertices):
    return max(max(coordinates) for coordinates in vertices)

