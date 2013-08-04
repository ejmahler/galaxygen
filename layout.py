# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''
This file is responsible for modifying the spatial layout of an existing graph

Motivations for doing so might be to make the graph more visually appealing, for example
'''

import datetime
import math
from functools import partial
from itertools import izip

import serialize
from utils.vector3d import Vector3D

def forced_directed_layout(star_array, edge_data, algorithm = "log-lin", iterations=1, 
        repel_quad_multiplier=30000, attraction_linear_multiplier=1, 
        
        repel_lin_multiplier=.04, repel_cubic_multiplier=50000, attraction_log_multiplier=.2,
        
        global_multiplier = .1):
    
    position_array = [Vector3D(*(v['position'])) for v in star_array]
    region_array = [v['region'] for v in star_array]
    
    #build functions to pass to map()
    if(algorithm == 'log-lin'):
        repel_func = partial(
            repel_vertex_linear, 
            vertex_array=position_array,
            linear_multiplier=repel_lin_multiplier, 
            cubic_multiplier=repel_cubic_multiplier
            )
        attraction_func = partial(attract_vertex_log, vertex_array=position_array, region_array=region_array, edge_data=edge_data)
        
        attraction_multiplier = attraction_log_multiplier
        
    elif(algorithm == 'spring-charge'):
        repel_func = partial(repel_vertex_quadratic, vertex_array=position_array)
        attraction_func = partial(attract_vertex_linear, vertex_array=position_array, region_array=region_array, edge_data=edge_data)
        
        attraction_multiplier = attraction_linear_multiplier
        repel_multiplier = repel_quad_multiplier
        
    global_func = partial(compute_global_forces, vertex_array=position_array)
    
    #create an array of the forces that were computed on the previous frame
    previous_forces = []
    
    timestep = 5
    swing_tolerance = .2
    printstep = int((100.0 / (len(star_array)**2)) * 1000.0) or 1
    
    if(printstep < iterations):
        print "0%"
    
    start_time = datetime.datetime.now()
    for i in xrange(iterations):
        
        #compute the attraction, repulsion, and global forces
        repel_forces = map(repel_func, xrange(len(position_array)))
        attraction_forces = map(attraction_func, xrange(len(position_array)))
        global_forces = map(global_func, xrange(len(position_array)))
        
        #add up the attraction/repulsion to find the total force for each vertex
        current_forces = [
            repel_force + attract_force * attraction_multiplier + global_force * global_multiplier
            for repel_force, attract_force, global_force in izip(repel_forces, attraction_forces, global_forces)
            ]
        
        #use the current and previous force data to update the global speed
        timestep = update_timestep(timestep, previous_forces, current_forces, swing_tolerance)
    
        #apply the forces
        sum_local = 0
        for v_index, force in izip(xrange(len(position_array)), current_forces):
            
            #we need to compute the "local speed" - in addition to updating the global timestep based on swing, we also do the same for each vertex
            if(len(previous_forces) > 0):
                prev_force = previous_forces[v_index]
                
                #take the dot product of the current force with the previous force, both normalized
                #if the dot product is negative, there must be some swing going on
                #timestep * sqrt((dot + 1)*0.5) will result in a local timestep close to 0 if the dot product is close to -1
                #and will result in a local timestep close to the global timestep if the dot product is close to 1
                swing_dot = Vector3D.dot(prev_force.normalized(),force.normalized())
                
                local_timestep = timestep * math.sqrt((swing_dot + 1) * 0.5)
            else:
                local_timestep = timestep
                
            position_array[v_index] += force * local_timestep
            sum_local += local_timestep
            
        previous_forces = current_forces
        
        if(i % printstep == 0):
            current_time = datetime.datetime.now()
            elapsed = current_time - start_time
            
            pct = float(i+1) / iterations
            seconds_per_percent = elapsed.total_seconds() / pct
            
            remaining_time = datetime.timedelta(seconds=(1 - pct) * seconds_per_percent)
            eta = current_time + remaining_time
            
            print "%.1f%%, timestep=%.4f, remaining time=%s, eta=%s"%(round(pct*100,1), timestep, str(remaining_time), str(eta))
            
            
    for star, pos in zip(star_array, position_array):
        star['position'] = tuple(pos)
    
    

#compute all the repelling forces for this vertex, proprtional to the inverse square of their distance
def repel_vertex_quadratic(v_index, vertex_array):
    
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

#compute all the attracting forces, proportional to their distance
def attract_vertex_linear(v_index, vertex_array, region_array, edge_data):
    
    total_force = Vector3D(0,0,0)
    
    pos = vertex_array[v_index]
    vc = region_array[v_index]
    
    for neighbor in edge_data[v_index]:
        nc = region_array[neighbor]
        
        neighbor_pos = vertex_array[neighbor]
        
        displacement = neighbor_pos - pos
        
        #if these two vertices are in diffrent regions, only attract at 5% strength
        if(vc != nc):
            total_force += displacement * 0.01
        else:
            total_force += displacement
        
    return total_force



#compute all the repelling forces for this vertex, proprtional to the inverse of their distance
def repel_vertex_linear(v_index, vertex_array, linear_multiplier, cubic_multiplier):
    
    total_force = Vector3D(0,0,0)
    
    pos = vertex_array[v_index]
    
    for index, neighbor_pos in enumerate(vertex_array):
        if(index != v_index):
            displacement = pos - neighbor_pos
            
            distance_sq = displacement.length_sq()
            
            #prevent distance from getting too large, otherwise you get vertices shooting away from each other at the start if they're too close
            if(distance_sq < 1):
                distance_sq = 1
            
            #normalize by dividing by distance
            #then apply force proportinal to the inverse of the distance (divide by distance again)
            #for performance, just use the vector's length_sq method and never compute the actual distance
            multiplier = linear_multiplier / distance_sq
            total_force += displacement * multiplier
            
            #also apply cubic repulsion
            if(distance_sq < 100):
                distance_sq = 100
            multiplier = cubic_multiplier / (distance_sq * distance_sq)
            total_force += displacement * (multiplier)
        
    return total_force

#compute all the attracting forces, proportional to the log of their distance
def attract_vertex_log(v_index, vertex_array, region_array, edge_data):
    
    total_force = Vector3D(0,0,0)
    
    pos = vertex_array[v_index]
    vc = region_array[v_index]
    
    for neighbor in edge_data[v_index]:
        nc = region_array[neighbor]
        
        neighbor_pos = vertex_array[neighbor]
        
        displacement = neighbor_pos - pos
        
        displacement_length = displacement.length()
        log_length = math.log(displacement_length)
        
        #divide by length to normalize, then multiply by the log of the length
        multiplier = log_length / displacement_length
        
        #if these two vertices are in diffrent regions, only attract at 5% strength
        if(vc != nc):
            total_force += displacement * (multiplier * 0.01)
        else:
            total_force += displacement * multiplier
        
    return total_force



def compute_global_forces(v_index, vertex_array):
        
    #gently pull this vertex towards the center
    pos_vector = vertex_array[v_index]
    center_force = pos_vector.normalized() * -.1
    
    #pull this vertex towards the ecliptic
    ecliptic_force = Vector3D(0, 0, pos_vector[2] * -1000)
    
    return center_force + ecliptic_force


#if there is a lot of swing (ie vertices moving back and forth without going anywhere) we need to slow the simulation down
#if there is not a lot of swing we can speed up the simulation
def update_timestep(timestep, previous_forces, current_forces, swing_tolerance):
    if(len(previous_forces) > 0):
        #take the average dot product for every (previous, current) pair
        dot_sum = sum(Vector3D.dot(prev.normalized(), current.normalized()) for prev, current in izip(previous_forces, current_forces))
        dot_average = dot_sum / len(current_forces)
      
        multiplier = 1 - math.acos(dot_average) / math.pi + swing_tolerance
        
        new_timestep = timestep * multiplier
        
        #we don't want the timestep to increase/decrease too quickly - limit it to 40% up or down
        if(abs(new_timestep - timestep) / timestep > 0.2):
            if(new_timestep > timestep):
                return timestep * 1.2
            else:
                return timestep * 0.8
        else:
            return new_timestep
    else:
        #we don't have any data on the forces for the previous step, so we can't change the timestep
        return timestep