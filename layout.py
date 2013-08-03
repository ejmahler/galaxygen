# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''
This file is responsible for modifying the spatial layout of an existing graph

Motivations for doing so might be to make the graph more visually appealing, for example
'''

import math
from functools import partial

import serialize
from utils.vector3d import Vector3D

def forced_directed_layout(star_array, edge_data, iterations=1, repel_multiplier=30000, attraction_multiplier=1, global_multiplier = .1):
    
    position_array = [Vector3D(*(v['position'])) for v in star_array]
    region_array = [v['region'] for v in star_array]
    
    #provide the same position array to every vertex
    repel_func = partial(repel_vertex_charge, vertex_array=position_array)
    
    #provide the same position array to every vertex
    attraction_func = partial(attract_vertex_spring, vertex_array=position_array, region_array=region_array, edge_data=edge_data)
    
    global_func = partial(compute_global_forces, vertex_array=position_array)
    
    timestep = .1
    printstep = int((100.0 / (len(star_array)**2)) * 1000.0) or 1
    
    for i in xrange(iterations):
        
        if(i > 0 and i % printstep == 0):
            pct = float(i) / iterations
            print "%.1f%%"%(round(pct*100,1))
        
        #compute repelling forces
        repel_forces = map(repel_func, xrange(len(position_array)))
        
        #compute repelling forces
        attraction_forces = map(attraction_func, xrange(len(position_array)))
        
        global_forces = map(global_func, xrange(len(position_array)))
    
        #apply the forces
        for v_index, repel_force, attract_force, global_force in zip(xrange(len(position_array)), repel_forces, attraction_forces, global_forces):
            position_array[v_index] += (repel_force * repel_multiplier + attract_force * attraction_multiplier + global_force * global_multiplier) * timestep
            
    if(printstep < iterations):
        print "100%"
    
    for star, pos in zip(star_array, position_array):
        star['position'] = tuple(pos)
    
    

#compute all the repelling forces for this vertex as if they were all electrically charged particles
def repel_vertex_charge(v_index, vertex_array):
    
    total_force = Vector3D(0,0,0)
    
    pos = vertex_array[v_index]
    
    for index, neighbor_pos in enumerate(vertex_array):
        if(index != v_index):
            displacement = pos - neighbor_pos
            
            distance = math.sqrt(displacement.length_sq())
            
            #prevent distance from getting too large, otherwise you get vertices shooting away from each other at the start if they're too close
            if(distance < 10):
                distance = 10
            
            #normalize by dividing by distance
            #then apply force proportinal to the inverse square of the distance (divide by distance * distance)
            multiplier = 1 / (distance * distance * distance)
            total_force += displacement * multiplier
        
    return total_force

#compute all the attracting forces for this vertex as if it was attached to its neighbors by springs
def attract_vertex_spring(v_index, vertex_array, region_array, edge_data):
    
    total_force = Vector3D(0,0,0)
    
    pos = vertex_array[v_index]
    vc = region_array[v_index]
    
    for neighbor in edge_data[v_index]:
        nc = region_array[neighbor]
        
        neighbor_pos = vertex_array[neighbor]
        
        displacement = neighbor_pos - pos
        
        #if these two vertices are in diffrent regions, only attract at 5% strength
        if(vc != nc):
            total_force += displacement * 0.5
        else:
            total_force += displacement
        
    return total_force

def compute_global_forces(v_index, vertex_array):
        
    #gently pull this vertex towards the center
    pos_vector = vertex_array[v_index]
    center_force = pos_vector.normalized() * -1
    
    #pull this vertex towards the ecliptic
    ecliptic_force = Vector3D(0, 0, pos_vector[2] * -100)
    
    return center_force + ecliptic_force


