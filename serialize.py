# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import cPickle as pickle

from utils.vector3d import Vector3D

default_json_filename = 'stars.json'
default_pickle_filename = 'stars.pickle'

def load(filename):
    with open(filename, 'r') as datafile:
        data = pickle.load(datafile)
    
    return data['vertices'], data['edges']

def save(star_array, edge_dict, filename):
    
    with open(filename, 'w') as datafile:
        pickle.dump({'vertices':star_array, 'edges':edge_dict}, datafile)
        
        
def load_json(filename):
    
    with open(filename, 'r') as datafile:
        data = json.load(datafile)
    
    
    #for vertices, we have to convert the keys to int, as well as the region and constellation values
    vertex_output = {}
    for key, value in data['vertices'].iteritems():
        value['region'] = int(value['region'])
        value['constellation'] = int(value['constellation'])
        value['position']
        
        vertex_output[int(key)] = value
        
    #for edges we have to convert the keys to int, and convert the values to sets of ints
    edge_output = {}
    for key, value in data['edges'].iteritems():
        edge_output[int(key)] = {int(v) for v in value}
        
    return vertex_output, edge_output

def save_json(star_dict, edge_dict, filename):
    
    #for vertices, we have to convert the keys to str, as well as the region and constellation values
    vertex_output = {}
    for key, value in star_dict.iteritems():
        vertex = dict(value)
        
        vertex['region'] = str(vertex['region'])
        vertex['constellation'] = str(vertex['constellation'])
        vertex['position'] = Vector3D(*value['position'])
        
        vertex_output[str(key)] = vertex
    
    
    #for edges we have to convert the keys to str, and convert the values to lists of str
    edge_output = {}
    for key, value in edge_dict.iteritems():
        edge_output[str(key)] = list(str(v) for v in value)
        
    with open(filename, 'w') as datafile:
        json.dump({'vertices':vertex_output, 'edges':edge_output}, datafile)
        
