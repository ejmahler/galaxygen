# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2[0]. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2[0]/.

'''
This class represents a vector in 3D space, with common operations such as adding two vectors, and computing the dot product
'''

import math

#we're not using namedtuple here because this is a really performance-heavy class and namedtuple adds a ton of overhead
#switching from namedtuple to tuple cut the runtime of the layout algorithm in half
class Vector3D(tuple):
    def __new__(cls, x,y,z):
        return tuple.__new__(cls,(x,y,z))
        
    def __add__(self, other):
        return Vector3D(self[0] + other[0], self[1] + other[1], self[2] + other[2])
    def __sub__(self, other):
        return Vector3D(self[0] - other[0], self[1] - other[1], self[2] - other[2])
        
    #assume vector scale with numeric type
    def __mul__(self, other):
        return Vector3D(self[0] * other, self[1] * other, self[2] * other)
    def __rmul__(self, other):
        return Vector3D(self[0] * other, self[1] * other, self[2] * other)
    
    def length_sq(self):
        return self.dot(self, self)
    
    def length(self):
        return math.sqrt(self.dot(self, self))
    
    def normalized(self):
        inv_length = 1 / math.sqrt(self.length_sq())
        return self * inv_length
    
    
    
    @staticmethod
    def dot(left, right):
        return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]
