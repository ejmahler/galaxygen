# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import math
import random
import pprint

import numpy

from scipy.sparse import dok_matrix
from scipy.sparse import csgraph
from scipy.optimize import brentq
from scipy.spatial import cKDTree as KDTree


def generate_galaxy(num_stars, spiral_arm_count, spiral_tightness, galaxy_radius, bulge_height, disk_height):
    
    #generate vertices
    star_array = []
    
    #spiral stars
    for i in xrange(int(num_stars*0.65)):
        star_array.append(create_vertex_spiral(max_radius=galaxy_radius, arm_count=spiral_arm_count, beta=spiral_tightness, disk_height=disk_height))
    
    #inner cluster stars
    for i in xrange(int(num_stars*0.15)):
        star_array.append(create_vertex_inner(max_radius=galaxy_radius * 0.8, bulge_height=bulge_height))
    
    #outer "spread out" stars
    while(len(star_array) < num_stars):
        star_array.append(create_vertex_outer(max_radius=galaxy_radius * 0.9, disk_height=disk_height))
    
    #generate a KDTree from the star data in order to help with edges
    star_tree = KDTree(star_array)
    
    #compute the nearest neighbors for each vertex
    distance_data, index_data = star_tree.query(star_array, k=20, eps=0.1)
    
    #for each vertex, randomly add edges to its nearest neighbors
    edge_dict = {}
    for distances, indexes in zip(distance_data, index_data):
        v1 = int(indexes[0])
        
        if(v1 not in edge_dict):
            edge_dict[v1] = set()
        
        for distance, v2 in create_edges(zip(distances[1:],indexes[1:])):
            
            v2 = int(v2)
            
            edge_dict[v1].add(v2)
            
            if(v2 not in edge_dict):
                edge_dict[v2] = set()
            edge_dict[v2].add(v1)
    
    #remove disconnected components from the graph
    star_array, edge_dict = remove_diconnected_stars(star_array, edge_dict)
    
    #convert the star array to an array of dictionaries before returning, so other data can be added
    star_array = [{'position':p} for p in star_array]
    
    print len(star_array)
    
    return star_array, edge_dict

def create_vertex_inner(max_radius, bulge_height):
    
    radius_pct = random.betavariate(1.5, 4)
    radius = radius_pct * max_radius
    
    angle = random.uniform(0, 2 * math.pi)
    
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    
    
    max_z = bulge_height*20*radius_pct*(radius_pct - 1)**7
    z = random.triangular(-max_z,max_z, 0)
    
    return (x,y,z)

def create_vertex_outer(max_radius, disk_height):
    
    radius_pct = random.betavariate(2, 2)
    radius = radius_pct * max_radius
    
    angle = random.uniform(0, 2 * math.pi)
    
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    
    max_z = disk_height * math.sqrt(1 - radius_pct)
    z = random.triangular(-max_z,max_z, 0)
    
    return (x,y,z)

def create_vertex_spiral(max_radius, disk_height, arm_count, beta):
    
    radius_pct = random.betavariate(4, 4)
    radius = radius_pct * max_radius
    
    base_angle = math.log(radius) / (beta)
    
    angle_pct = random.betavariate(4, 4)
    arm_num = random.randint(0,arm_count - 1)
    arm_angle = (angle_pct + arm_num) * 2 * math.pi / arm_count
    
    angle = base_angle + arm_angle
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    
    max_z = disk_height * math.sqrt(1 - radius_pct)
    z = random.triangular(-max_z,max_z, 0)
    
    return (x,y,z)

def create_edges(neighbors):
    inf = float('inf')
    
    for i, (distance, v) in enumerate(neighbors):
        if(distance != inf):
            num = random.betavariate(i + 1, 2.1)
            
            if(num < (0.5)):
                yield (distance,v)
                pass
            
    return
    yield


def remove_diconnected_stars(position_array, edge_dict):
    
    #build an adjacency matrix using the scipy sparse matrix library.
    #the scipy docs recommend using dok_matrix for incrementally building a matrix like this
    mat_size = len(edge_dict)
    mat = dok_matrix( (mat_size,mat_size), dtype=numpy.int8)
    
    for v, neighbors in edge_dict.iteritems():
        for n in neighbors:
            mat[v,n] = 1
            
    #compute the connected components
    n, component_array = csgraph.connected_components(mat)
    
    #group the vertices into their components
    component_group = dict()
    for v, group in enumerate(component_array):
        if(group not in component_group):
            component_group[group] = []
        component_group[group].append(v)
        
        
    #sort the components by size
    sorted_components = sorted((len(component), component) for component in component_group.itervalues())
    
    #put the elements of every component but the last into the disconnection set. the last component is the largest.
    disconnection_set = set()
    for size,vertices in sorted_components[:-1]:
        disconnection_set.update(vertices)
        
    #remove stars in the disconnection set and convert the star array to an array of dictionaries before returning, so other data can be added
    index_map = {}
    result_array = []
    for i, p in enumerate(position_array):
        if(i not in disconnection_set):
            index_map[i] = len(result_array)
            result_array.append(p)
            
    #use the index map to convert old indexes to new indexes in the edge dict
    new_edge_dict = {}
    for v, neighbors in edge_dict.iteritems():
        
        if(v not in disconnection_set):
            new_v = index_map[v]
            
            if(new_v not in new_edge_dict):
                new_edge_dict[new_v] = set()
            
            for n in neighbors:
                new_n = index_map[n]
                new_edge_dict[new_v].add(new_n)
            
    return result_array, new_edge_dict
    
    
    
    
    
    
    
    
    
    
    
    
    
    