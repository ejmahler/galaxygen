# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import math
import random
import pprint
import sqlite3

import numpy
from scipy.sparse import dok_matrix
from scipy.sparse import csgraph
from scipy.optimize import brentq
from scipy.spatial import cKDTree as KDTree

from utils.vector3d import Vector3D


def generate_galaxy(num_stars, spiral_arm_count, spiral_tightness, galaxy_radius, bulge_height, disk_height):
    
    #generate vertices
    star_dict = {}
    
    next_index = 0
    #spiral stars
    for i in xrange(int(num_stars*0.65)):
        star_dict[next_index] = create_vertex_spiral(max_radius=galaxy_radius, arm_count=spiral_arm_count, beta=spiral_tightness, disk_height=disk_height)
        next_index += 1
    
    #inner cluster stars
    for i in xrange(int(num_stars*0.15)):
        star_dict[next_index] = create_vertex_inner(max_radius=galaxy_radius * 0.8, bulge_height=bulge_height)
        next_index += 1
    
    #outer "spread out" stars
    while(len(star_dict) < num_stars):
        star_dict[next_index] = create_vertex_outer(max_radius=galaxy_radius * 0.9, disk_height=disk_height)
        next_index += 1
    
    #generate a KDTree from the star data in order to help with edges
    star_keys = star_dict.keys()
    star_values = star_dict.values()
    star_tree = KDTree(star_values)
    
    #compute the nearest neighbors for each vertex
    distance_data, index_data = star_tree.query(star_values, k=20, eps=0.1)
    
    #for each vertex, randomly add edges to its nearest neighbors
    edge_dict = {}
    for distances, indexes in zip(distance_data, index_data):
        v1 = star_keys[int(indexes[0])]
        
        if(v1 not in edge_dict):
            edge_dict[v1] = set()
        
        for distance, v2 in create_edges(zip(distances[1:],indexes[1:])):
            
            v2 = star_keys[int(v2)]
            
            edge_dict[v1].add(v2)
            
            if(v2 not in edge_dict):
                edge_dict[v2] = set()
            edge_dict[v2].add(v1)
    
    #remove disconnected components from the graph
    star_dict, edge_dict = remove_disconnected_stars(star_dict, edge_dict)
    
    #convert the star array to an array of dictionaries before returning, so other data can be added
    star_dict = {key:{'position':Vector3D(*p)} for key, p in star_dict.iteritems()}
    
    return star_dict, edge_dict

def create_vertex_inner(max_radius, bulge_height):
    
    radius_pct = random.betavariate(1.5, 4)
    radius = radius_pct * max_radius
    
    angle = random.uniform(0, 2 * math.pi)
    
    x = math.cos(angle) * radius
    z = math.sin(angle) * radius
    
    
    max_y = bulge_height*20*radius_pct*(radius_pct - 1)**7
    y = random.triangular(-max_y,max_y, 0)
    
    return (x,y,z)

def create_vertex_outer(max_radius, disk_height):
    
    radius_pct = random.betavariate(2, 2)
    radius = radius_pct * max_radius
    
    angle = random.uniform(0, 2 * math.pi)
    
    x = math.cos(angle) * radius
    z = math.sin(angle) * radius
    
    max_y = disk_height * math.sqrt(1 - radius_pct)
    y = random.triangular(-max_y,max_y, 0)
    
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
    z = math.sin(angle) * radius
    
    max_y = disk_height * math.sqrt(1 - radius_pct)
    y = random.triangular(-max_y,max_y, 0)
    
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
    
    
    
#load data from an sqlite version of an eve data dump (intended for use with http://pozniak.pl/wp/?page_id=530)
def load_sqlite(filename):
    con = sqlite3.connect(filename)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    
    #load vertices
    vertices = {}
    for row in cursor.execute("SELECT * FROM mapsolarsystems"):
        vertex = {}
        vertex['region'] = int(row['regionID'])
        vertex['constellation'] = int(row['constellationID'])
        vertex['name'] = row['solarSystemName']
        vertex['security'] = row['security']
        
        vertex['position'] = Vector3D(row['x'], row['y'], -row['z'])#we have to flip the z axis
        
        vertices[int(row['solarSystemID'])] = vertex
    
    #load edges
    edges = {v:set() for v in vertices.iterkeys()}
    for row in cursor.execute("SELECT * FROM mapsolarsystemjumps"):
        edges[row['fromSolarSystemID']].add(row['toSolarSystemID'])

    #the vertices dict currently includes the wormhole systems, and we don't want those. so remove any vertex that has no edges
    vertices, edges = remove_disconnected_stars(vertices, edges)
    
    #we have to normalize the position, since it's huge right now
    #shrink everything so every vertex is at most 2000 units away
    max_distance = max(v['position'].length() for v in vertices.itervalues())
    multiplier = 2000/max_distance
    for v in vertices.itervalues():
        v['position'] *= multiplier
        
    return vertices, edges


def remove_disconnected_stars(position_dict, edge_dict):
    
    #create a mapping from keys to indexes and indexes back to keys
    index_to_key = position_dict.keys()
    key_to_index = {k:i for i,k in enumerate(index_to_key)}
    
    #build an adjacency matrix using the scipy sparse matrix library.
    #the scipy docs recommend using dok_matrix for incrementally building a matrix like this
    mat_size = len(edge_dict)
    mat = dok_matrix( (mat_size,mat_size), dtype=numpy.int8)
    
    for v, neighbors in edge_dict.iteritems():
        for n in neighbors:
            mat[key_to_index[v],key_to_index[n]] = 1
            
    #compute the connected components
    n, component_array = csgraph.connected_components(mat)
    
    #group the vertices into their components
    component_group = dict()
    for index, group in enumerate(component_array):
        if(group not in component_group):
            component_group[group] = []
        component_group[group].append(index_to_key[index])
        
        
    #sort the components by size
    sorted_components = sorted((len(component), component) for component in component_group.itervalues())
    
    #put the elements of every component but the last into the disconnection set. the last component is the largest.
    disconnection_set = set()
    for size,vertices in sorted_components[:-1]:
        disconnection_set.update(vertices)
            
    #use the index map to convert old indexes to new indexes in the edge dict
    new_position_dict = {}
    new_edge_dict = {}
    for v, neighbors in position_dict.iteritems():
        
        if(v not in disconnection_set):
            new_position_dict[v] = position_dict[v]
            new_edge_dict[v] = edge_dict[v]
            
    return new_position_dict, new_edge_dict
    
    
    
    
    
    
    
    
    
    
    
    
    
    