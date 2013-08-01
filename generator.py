
import math
import random
import pprint

from scipy.optimize import brentq
from scipy.spatial import cKDTree as KDTree


def generate_galaxy(num_stars, spiral_arm_count, spiral_tightness, galaxy_radius, bulge_height, disk_height):
    
    #generate vertices
    star_array = []
    
    #spiral stars
    for i in xrange(int(num_stars*0.65)):
        star_array.append(create_vertex_spiral(max_radius=galaxy_radius, arm_count=spiral_arm_count, beta=spiral_tightness, disk_height=disk_height))
    
    #inner cluster stars
    for i in xrange(int(num_stars*0.2)):
        star_array.append(create_vertex_inner(max_radius=galaxy_radius * 0.8, bulge_height=bulge_height))
    
    
    #outer "spread out" stars
    for i in xrange(int(num_stars*0.15)):
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
    
    
    #convert the star array to an array of dictionaries before returning, so other data can be added
    star_array = [{'position':p} for p in star_array]
    
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
    for i, (distance, v) in enumerate(neighbors):
        num = random.betavariate(i + 1, 2.6)
        
        if(num < (0.5)):
            yield (distance,v)
            pass
            
    return
    yield
