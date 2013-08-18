# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''
This file is responsible for computing various centrality measures for a given graph
'''

import random

import networkx
import numpy
from scipy.sparse import csr_matrix

def compute_centrality(star_dict, edge_dict):
    
    #build up a nx graph
    galaxy = networkx.Graph()
    for v, vertex in star_dict.iteritems():
        galaxy.add_node(v)
    
    for v, neighbors in edge_dict.iteritems():
        for n in neighbors:
            galaxy.add_edge(v,n)
            
    print "betweenness"
    betweenness_map = networkx.current_flow_betweenness_centrality(galaxy)
    betweenness_map = normalize(betweenness_map)
    
    for key, value in betweenness_map.iteritems():
        star_dict[key]['betweenness'] = value
        
    print "closeness"
    closeness_map = networkx.current_flow_closeness_centrality(galaxy)
    closeness_map = normalize(closeness_map)
    
    for key, value in closeness_map.iteritems():
        star_dict[key]['closeness'] = value
        

    print "pagerank"
    pagerank_map = networkx.pagerank_scipy(galaxy)
    pagerank_map = normalize(pagerank_map)
    
    for key, value in pagerank_map.iteritems():
        star_dict[key]['pagerank'] = value


def compute_security(star_dict, edge_dict, num_seeds, num_iterations):
    
    #build up a nx graph
    galaxy = networkx.Graph()
    for v, vertex in star_dict.iteritems():
        galaxy.add_node(v)
    
    for v, neighbors in edge_dict.iteritems():
        for n in neighbors:
            galaxy.add_edge(v,n)
            
    #use the centrality measures already computed to find seeds
    
    #find the top 25% vertices of each centrality measure
    betweenness_limit = int(len(star_dict)* 0.4)
    sorted_betweenness = sorted((v['betweenness'], k) for k, v in star_dict.iteritems())
    top_betweenness = {k for (value, k) in sorted_betweenness[-betweenness_limit:]}
    
    closeness_limit = int(len(star_dict)* 0.15)
    sorted_closeness = sorted((v['closeness'], k) for k, v in star_dict.iteritems())
    top_closeness = {k for (value, k) in sorted_closeness[-closeness_limit:]}
    
    pagerank_limit = int(len(star_dict)* 0.4)
    sorted_pagerank = sorted((v['pagerank'], k) for k, v in star_dict.iteritems())
    top_pagerank = {k for (value, k) in sorted_pagerank[-pagerank_limit:]}
    
    #take the intersection of all the top measures. this will be our pool to choose seeds from
    seed_pool = top_betweenness & top_closeness & top_pagerank
    print len(seed_pool)
    
    seeds = set()
    #loop until we have num_seeds or the seed pool is exhausted
    while(len(seed_pool) > 0 and len(seeds) < num_seeds):
        
        #pick a random vertex and remove it from the seed pool
        current_seed = random.choice(list(seed_pool))
        seed_pool.remove(current_seed)
        
        #find all vertices within 10 jumps
        close_vertices = networkx.single_source_shortest_path(galaxy, source=current_seed, cutoff=15)
        
        #if none of the current seeds were found within 10 jumps, add this as a seed
        if(len(seeds.intersection(close_vertices.iterkeys())) == 0):
            seeds.add(current_seed)
    print len(seeds)
    
    #apply the random walk algorithm, aka pagerank with alpha=1
    personalization_dict = {k: v['closeness']**10 for k,v in star_dict.iteritems()}
    mat = networkx.google_matrix(galaxy, alpha=1, personalization=personalization_dict, nodelist=star_dict.keys())
    mat = csr_matrix(mat)
    
    #for the initial array, set the seeds to 1 and everything else to 0
    weight_array = numpy.empty(len(star_dict), dtype=mat.dtype)
    weight_array.fill(0.0001)
    for i,k in enumerate(star_dict.iterkeys()):
        if(k in seeds):
            weight_array[i] = 1
            
    #iterate that shit
    for i in xrange(num_iterations):
        weight_array = weight_array * mat
        
    #create a security dict to normalize
    security_dict = {k:weight_array[i] for i, k in enumerate(star_dict.iterkeys())}
    security_dict = normalize(security_dict)
    
    #apply some data transformations - the square root will create more hisec, and the subtraction will create nullsec
    for key,value in security_dict.iteritems():
        security_dict[key] = value ** 0.025 - 0.94
        
    security_dict = normalize(security_dict)
    
    
    #copy the result into the security field
    for k,v in star_dict.iteritems():
        v['security'] = security_dict[k]
    
    
def normalize(centrality_dict):
    max_value = max(centrality_dict.itervalues())
    return {key:value/max_value for key, value in centrality_dict.iteritems()}
