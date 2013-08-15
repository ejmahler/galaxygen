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

def forced_directed_layout(star_dict, edge_dict, iterations=1):
    
    node_keys = star_dict.keys()
    
    #TODO: dont hardcode these values. get them from python's settings module or something
    #that way we can git ingore the settings file and changing the numbers wont cause deltas
    #build functions to pass to map()
    repel_func = partial(compute_repel_force,
        linear_constant=0.5,
        quad_constant=0,
        cubic_constant=9000,
        )
    attraction_func = partial(compute_attraction_force,
        log_constant=1,
        linear_constant=0.001, 
        quad_constant=0.0001,
        cubic_constant=0.0000001,
        different_region_multiplier=0.05
        )
        
    global_func = partial(compute_global_force,
        center_constant=.0005,
        plane_constant=1
        )
    
    
    
    #create the function that will be called by map
    total_force_func = partial(compute_vertex_force,
        vertex_dict=star_dict,
        edge_dict=edge_dict,
        attraction_func=attraction_func,
        repulsion_func=repel_func,
        global_func=global_func
        )
    
    #create an array of the forces that were computed on the previous frame
    previous_forces = {}
    
    timestep = 0.9
    swing_tolerance = .2
    printstep = int((100.0 / (len(star_dict)**2)) * 1000.0) or 1
    
    if(printstep < iterations):
        print "0%"
    
    start_time = datetime.datetime.now()
    for i in xrange(iterations):
        #compute the forces for this frame
        current_forces = {k:total_force_func(k) for k in node_keys}
        
        #use the current and previous force data to update the global speed
        timestep = update_timestep(timestep, previous_forces, current_forces, swing_tolerance)
    
        #apply the forces
        for v, vertex in star_dict.iteritems():
            
            current_force = current_forces[v]
            
            #we need to compute the "local speed" - in addition to updating the global timestep based on swing, we also do the same for each vertex
            if(v in previous_forces):
                prev_force = previous_forces[v]
                
                #take the dot product of the current force with the previous force, both normalized
                #if the dot product is negative, there must be some swing going on
                #timestep * sqrt((dot + 1)*0.5) will result in a local timestep close to 0 if the dot product is close to -1
                #and will result in a local timestep close to the global timestep if the dot product is close to 1
                swing_dot = Vector3D.dot(prev_force.normalized(),current_force.normalized())
                
                local_timestep = timestep * math.sqrt((swing_dot + 1) * 0.5)
            else:
                local_timestep = timestep
                
            vertex['position'] += current_force * local_timestep
        previous_forces = current_forces
        
        if(i % printstep == 0):
            current_time = datetime.datetime.now()
            elapsed = current_time - start_time
            
            pct = float(i+1) / iterations
            seconds_per_percent = elapsed.total_seconds() / pct
            
            remaining_time = datetime.timedelta(seconds=(1 - pct) * seconds_per_percent)
            eta = current_time + remaining_time
            
            print "%.1f%%, timestep=%.4f, remaining time=%s, eta=%s"%(round(pct*100,1), timestep, str(remaining_time), str(eta))
            

def compute_vertex_force(v, vertex_dict, edge_dict, attraction_func, repulsion_func, global_func):

    current_position = vertex_dict[v]['position']
    current_region = vertex_dict[v]['region']


    
    global_force = global_func(current_position)
    attraction_force = Vector3D(0,0,0)
    repulsion_force = Vector3D(0,0,0)

    #compute attraction to this vertex's neighbors
    for n in edge_dict[v]:
        displacement = vertex_dict[n]['position'] - current_position
        
        #if these are in different regions, we want the attraction to be much weaker
        multiplier = 1
        same_region = (current_region == vertex_dict[n]['region'])
            
        attraction_force += attraction_func(displacement, same_region)
        
    
    #compute the repulsion from every other vertex
    for other_v, vertex in vertex_dict.iteritems():
        if(v != other_v):
            displacement = vertex_dict[n]['position'] - current_position
            repulsion_force += repulsion_func(displacement)
            
    return global_force + attraction_force + repulsion_force


def compute_global_force(position, center_constant, plane_constant):
    
    
    #compute attraction to the center
    center = position * (center_constant * -1)

    #compute attraction to the XZ plane
    plane = (0, -position[1] * plane_constant, 0)

    return center + plane


def compute_attraction_force(
    
        #different for each call
        displacement, same_region, 
        
        #same for each call (provided by functools.partial)
        log_constant, linear_constant, quad_constant, cubic_constant, different_region_multiplier
        ):
    
    #we will multiply the displacement vector by this multiplier
    #it's faster to add up this multiplier than it is to compute each vector (linearl, quadratic, cubic) separately and then add them
    multiplier = 0
    
    distance_sq = displacement.length_sq()

    #for repulsion only one of the options requires us to actually compute the square root, 
    #but for attraction more than one does, so just get it over with here
    distance = math.sqrt(distance_sq);

    if(log_constant != 0):
        #normalize, then multiply by the log of the distance
        multiplier += math.log(distance) * log_constant / distance
    
    if(linear_constant != 0):
        #we dont have to multiply anything here, jusr add the linear constant
        multiplier += linear_constant
    
    if(quad_constant != 0):
        #noralize, then multiply by distance squared
        #so we have constant * d^2 / d, or just constant * d
        multiplier += distance * quad_constant
    
    if(cubic_constant != 0):
        #noralize, then multiply by distance cubed
        #so we have constant * d^3 / d, or just constant * d*2
        multiplier += distance_sq * cubic_constant
        
    if(not same_region):
        multiplier *= different_region_multiplier

    return multiplier * displacement


MIN_DISTANCE_SQ = 4
def compute_repel_force(displacement, linear_constant, quad_constant, cubic_constant):
    
    #we will multiply the displacement vector by this multiplier
    #it's faster to add up this multiplier than it is to compute each vector (linearl, quadratic, cubic) separately and then add them
    multiplier = 0

    distance_sq = displacement.length_sq()

    if(distance_sq < MIN_DISTANCE_SQ):
        distance_sq = MIN_DISTANCE_SQ

    if(linear_constant != 0):
        #divide by distance to normalize, then divide by distance again to get force proportional to 1/distance
        #we can be sneaky and not even compute distance in the first place!
        multiplier -= linear_constant / distance_sq
    
    if(quad_constant != 0):
        #divide by distance to normalize, then divide by distance^2 to get force proportional to 1/(distance^2)
        #we have to compute distance for this one :(
        distance = math.sqrt(distance_sq);
        multiplier -= quad_constant / (distance * distance_sq)
    
    if(cubic_constant != 0):
        #divide by distance to normalize, then divide by distance*3 to get force proportional to 1/(distance^3)
        #we can be sneaky and not even compute distance on the first place!
        multiplier -= cubic_constant / (distance_sq * distance_sq)
    

    return multiplier * displacement;



#if there is a lot of swing (ie vertices moving back and forth without going anywhere) we need to slow the simulation down
#if there is not a lot of swing we can speed up the simulation
def update_timestep(timestep, previous_forces, current_forces, swing_tolerance):
    if(len(previous_forces) > 0):
        #take the average dot product for every (previous, current) pair
        dot_sum = sum(Vector3D.dot(previous_forces[v].normalized(), current_forces[v].normalized()) for v in current_forces.iterkeys())
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
    