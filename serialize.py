
import json
import cPickle as pickle

default_json_filename = 'stars.json'
default_pickle_filename = 'stars.pickle'

def load(filename):
    with open(filename, 'r') as datafile:
        data = pickle.load(datafile)
    
    return data['stars'], data['edges']

def save(star_array, edge_dict, filename):
    
    with open(filename, 'w') as datafile:
        pickle.dump({'stars':star_array, 'edges':edge_dict}, datafile)
        

def save_json(star_array, edge_dict, filename):
    
    #we have to convert the int keys in the edge dict to strings, and we have to convert the values from sets to lists
    edge_output = {}
    for key, value in edge_dict.iteritems():
        edge_output[str(key)] = list(str(v) for v in value)
        
    with open(filename, 'w') as datafile:
        json.dump({'stars':star_array, 'edges':edge_output}, datafile)
        
