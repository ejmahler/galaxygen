'''
This file is responsible for modifying the spatial layout of an existing graph

Motivations for doing so might be to make the graph more visually appealing, for example
'''

import math
from functools import partial

def forced_directed_layout(star_array, edge_data, iterations=1, repel_multiplier=100, attraction_multiplier=1):
    print "beginning force direction"
    
    position_array = [v['position'] for v in star_array]
    
    #provide the same position array to every vertex
    repel_func = partial(repel_vertex_charge, vertex_array=position_array)
    
    #provide the same position array to every vertex
    attraction_func = partial(attract_vertex_spring, vertex_array=position_array, edge_data=edge_data)
    
    timestep = .1
    
    for i in xrange(iterations):
        print "iteration %d"%i
        
        #compute repelling forces
        repel_forces = map(repel_func, xrange(len(position_array)))
        
        #compute repelling forces
        attraction_forces = map(attraction_func, xrange(len(position_array)))
    
        #apply the forces
        for v_index, repel_force, attract_force in zip(xrange(len(position_array)), repel_forces, attraction_forces):
            results = [0] * 3
            for i in xrange(3):
                results[i] = position_array[v_index][i] + (repel_force[i] * repel_multiplier + attract_force[i] * attraction_multiplier) * timestep
            position_array[v_index] = tuple(results)
    
    for star, pos in zip(star_array, position_array):
        star['position'] = pos
    
    

#compute all the repelling forces for this vertex as if they were all electrically charged particles
def repel_vertex_charge(v_index, vertex_array):
    
    x_force = 0
    y_force = 0
    z_force = 0
    
    vx,vy,vz = vertex_array[v_index]
    
    for index, (nx,ny,nz) in enumerate(vertex_array):
        if(index != v_index):
            dx = vx - nx
            dy = vy - ny
            dz = vz - nz
            
            inv_distance_sq = 1/(dx*dx + dy*dy + dz*dz)
            inv_distance = math.sqrt(inv_distance_sq)
            
            #normalize by dividing by distance (multiplying by inv distance)
            #then divide by distance squared (multiply by inv_distance_sq) to get the force
            multiplier = inv_distance * inv_distance_sq
            x_force += dx * multiplier
            y_force += dy * multiplier
            z_force += dz * multiplier
        
    return x_force, y_force, z_force

#compute all the attracting forces for this vertex as if it was attached to its neighbors by springs
def attract_vertex_spring(v_index, vertex_array, edge_data):
    
    x_force = 0
    y_force = 0
    z_force = 0
    
    vx,vy,vz = vertex_array[v_index]
    
    for neighbor in edge_data[v_index]:
        
        nx, ny, nz = vertex_array[neighbor]
        
        dx = nx - vx
        dy = ny - vy
        dz = nz - vz
        
        x_force += dx
        y_force += dy
        z_force += dz
        
    return x_force, y_force, z_force
