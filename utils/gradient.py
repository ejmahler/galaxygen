# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''
This class represents a gradient of floating point values, intened to represent a color gradient

Any objects supporting arithmetic can be used - use numpy arrays for example to interpolate multiple values at once
'''

class Gradient:
    def __init__(self):
        self.gradient = []
    
    def add_entry(self, float_position, value):
        self.gradient.append((float_position, value))
        self.gradient.sort()
        
    def interpolate(self, position):
        first_position, first_value = self.gradient[0]
        last_position, last_value = self.gradient[-1]
        
        #if the provided position is before the first entry or after the last entry, return the first or last entry respectively
        if(position <= first_position):
            return first_value
        elif(position >= last_position):
            return last_value
        
        #it must be somewhere in the middle, so go through the list two at a time
        for i in xrange(len(self.gradient) - 1):
            before_position, before_value = self.gradient[i]
            after_position, after_value = self.gradient[i+1]
            
            #if the requested position falls between these two entries, linearly interpolate the entries
            if(position > before_position and position <= after_position):
                percent = (position - before_position) / (after_position - before_position)
                
                return (1 - percent) * before_value + percent * after_value
