'''
This file is responsible for modifying the spatial layout of an existing graph

Motivations for doing so might be to make the graph more visually appealing, for example
'''

import argparse
import math
from functools import partial

import serialize

#this function runs when the file is run standalone
def run_iterations_on_file(filename, iterations):
    star_array, edge_data = serialize.load(filename)
    forced_directed_layout(star_array, edge_data, iterations=iterations)
    serialize.save(star_array, edge_data, filename)
    

def forced_directed_layout(star_array, edge_data, iterations=1, repel_multiplier=10000, attraction_multiplier=1, global_multiplier = .1):
    
    position_array = [v['position'] for v in star_array]
    
    #provide the same position array to every vertex
    repel_func = partial(repel_vertex_charge, vertex_array=position_array)
    
    #provide the same position array to every vertex
    attraction_func = partial(attract_vertex_spring, vertex_array=position_array, edge_data=edge_data)
    
    global_func = partial(compute_global_forces, vertex_array=position_array)
    
    timestep = .1
    
    for i in xrange(iterations):
        
        #compute repelling forces
        repel_forces = map(repel_func, xrange(len(position_array)))
        
        #compute repelling forces
        attraction_forces = map(attraction_func, xrange(len(position_array)))
        
        global_forces = map(global_func, xrange(len(position_array)))
    
        #apply the forces
        for v_index, repel_force, attract_force, global_force in zip(xrange(len(position_array)), repel_forces, attraction_forces, global_forces):
            results = [0] * 3
            for i in xrange(3):
                delta_force = repel_force[i] * repel_multiplier + \
                    attract_force[i] * attraction_multiplier + \
                    global_force[i] * global_multiplier
                
                results[i] = position_array[v_index][i] + delta_force * timestep
                
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

def compute_global_forces(v_index, vertex_array):
    
    x_force = 0
    y_force = 0
    z_force = 0
    
    #gently pull this vertex towards the center
    vx, vy, vz = vertex_array[v_index]
    
    distance = math.sqrt(vx*vx + vy*vy + vz*vz)
    
    x_force += -vx / distance
    y_force += -vy / distance
    z_force += -vz / distance
    
    
    #pull this vertex towards the center disk
    z_force += -vz
    
    return x_force, y_force, z_force


if(__name__ == '__main__'):
    parser = argparse.ArgumentParser('Takes an existing star data set and runs iterations of force layout on them. Can be run on pypy, unlike the rest of the galaxy generator modules')
    parser.add_argument('-i','--iterations', help="Number of iterations to run", type=int, default=1)
    parser.add_argument('-f','--filename', help="File name to load and save star data to and from", type=str, default='stars.json')
    
    args = parser.parse_args()
    
    kwargs = {}
    if(args.filename is not None):
        kwargs['filename'] = args.filename
    if(args.iterations is not None):
        kwargs['iterations'] = args.iterations
        
    run_iterations_on_file(**kwargs)
    