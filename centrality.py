# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''
This file is responsible for computing various centrality measures for a given graph
'''

import networkx

def compute_centrality(star_data, edge_data):
    
    #build up a nx graph
    galaxy = networkx.Graph()
    
    for v, neighbors in edge_data.iteritems():
        for n in neighbors:
            galaxy.add_edge(v,n)
            
    centrality_map = networkx.approximate_current_flow_betweenness_centrality(galaxy, epsilon=.2)
    centrality_map = normalize(centrality_map)
    
    
    for key, value in centrality_map.iteritems():
        star_data[key]['betweenness'] = value
        
def normalize(centrality_dict):
    max_value = max(centrality_dict.itervalues())
    return {key:value/max_value for key, value in centrality_dict.iteritems()}
