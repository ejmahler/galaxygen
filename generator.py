
import math
import random
import pprint

from scipy.optimize import brentq
from scipy.spatial import cKDTree as KDTree

inner_r = 0
outer_r = 2000
bulge_zr = 150
outer_zr = 50

def generate_galaxy(num_stars):
    
    #generate vertices
    star_array = []
    
    #spiral stars
    for i in xrange(int(num_stars*0.65)):
        star_array.append(create_vertex_spiral(inner_r, outer_r))
    
    #inner cluster stars
    for i in xrange(int(num_stars*0.2)):
        star_array.append(create_vertex_inner(inner_r, outer_r* 0.8))
    
    
    #outer "spread out" stars
    for i in xrange(int(num_stars*0.15)):
        star_array.append(create_vertex_outer(inner_r, outer_r * 1.1))
    
    #generate a KDTree from the star data in order to help with edges
    star_tree = KDTree(star_array)
    
    #compute the nearest neighbors for each vertex
    distance_data, index_data = star_tree.query(star_array, k=20, eps=0.1)
    
    #for each vertex, randomly add edges to its nearest neighbors
    edge_dict = {}
    for distances, indexes in zip(distance_data, index_data):
        v1 = indexes[0]
        
        for distance, v2 in create_edges(zip(distances[1:],indexes[1:])):
            
            if(v1 not in edge_dict):
                edge_dict[v1] = set()
            edge_dict[v1].add(v2)
            
            if(v2 not in edge_dict):
                edge_dict[v2] = set()
            edge_dict[v2].add(v1)
    
    return star_array, edge_dict

def create_vertex_inner(inner_radius, outer_radius):
    
    radius_pct = random.betavariate(1.5, 6)
    radius = radius_pct * (outer_radius - inner_radius) + inner_radius
    
    angle = random.uniform(0, 2 * math.pi)
    
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    
    
    max_z = bulge_zr*20*radius_pct*(radius_pct - 1)**7
    z = random.triangular(-max_z,max_z, 0)
    
    return [x,y,z]

def create_vertex_outer(inner_radius, outer_radius):
    
    radius_pct = random.betavariate(4, 4)
    radius = radius_pct * (outer_radius - inner_radius) + inner_radius
    
    angle = random.uniform(0, 2 * math.pi)
    
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    
    max_z = outer_zr * math.sqrt(1 - radius_pct)
    z = random.triangular(-max_z,max_z, 0)
    
    return [x,y,z]

b=0.4
num_arms=6
arm_width = 2 * math.pi / num_arms
def create_vertex_spiral(inner_radius, outer_radius):
    
    radius_pct = random.betavariate(4, 4)
    radius = radius_pct * (outer_radius - inner_radius) + inner_radius
    
    base_angle = math.log(radius) / (b)
    
    angle_pct = random.betavariate(4, 4)
    arm_num = random.randint(0,num_arms - 1)
    arm_angle = (angle_pct + arm_num) * arm_width
    
    
    
    angle = base_angle + arm_angle
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    
    max_z = outer_zr * math.sqrt(1 - radius_pct)
    z = random.triangular(-max_z,max_z, 0)
    
    return [x,y,z]

def create_edges(neighbors):
    for i, (distance, v) in enumerate(neighbors):
        num = random.betavariate(i + 1, 3)
        
        if(num < (0.5 - math.sqrt(distance) / 750)):
            yield (distance,v)
            pass
            
    return
    yield
