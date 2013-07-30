
import json

def load(filename="stars.json"):
    with open(filename, 'r') as datafile:
        data = json.load(datafile)
        
    star_array = data['stars']
    
    #we have to convert the string keys in the edge dict back to integer, and the values from lists back to sets
    edge_dict = {}
    for key, value in data['edges'].iteritems():
        edge_dict[int(key)] = set(value)
    
    return star_array, edge_dict

def save(star_array, edge_dict, filename="stars.json"):
    
    #we have to convert the int keys in the edge dict to strings, and we have to convert the values from sets to lists
    edge_output = {}
    for key, value in edge_dict.iteritems():
        edge_output[str(key)] = list(value)
        
    with open(filename, 'w') as datafile:
        json.dump({'stars':star_array, 'edges':edge_output}, datafile)
        