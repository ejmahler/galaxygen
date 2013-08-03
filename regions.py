'''
This file is responsible for grouping an existing galaxy into constellations and regions
'''

from itertools import izip


#use the iterative kerningham-lin modularity algorithm
def compute_regions(star_data, edge_data, constellation_iterations=2, region_iterations=4):
    if(region_iterations < constellation_iterations):
        region_iterations = constellation_iterations
        
    #create a mapping from star to community
    community_map = {key:key for key in edge_data.iterkeys()}
    
    #repeat the process several times
    for i in xrange(region_iterations):
        #create a mapping that will store edges with weight data. start weights out at 1
        weight_map = {}
        for v, neighbors in edge_data.iteritems():
            vc = community_map[v]
            
            #if this vertex's community is not in the weight map, add it
            if(vc not in weight_map):
                weight_map[vc] = dict()
            
            for n in neighbors:
                nc = community_map[n]
                
                if(nc not in weight_map[vc]):
                    weight_map[vc][nc] = 0
                    
                #if these are in the same community, add 2 to the edge weight (because we have a single loop edge to represent both directions), otherwise 1
                if(vc == nc):
                    weight_map[vc][nc] += 2
                else:
                    weight_map[vc][nc] += 1
        
        #run the community algorithm on the current graph
        result = create_communities(weight_map)
        
        #copy the result into the community map
        for key, value in community_map.iteritems():
            community_map[key] = result[value]
            
        #if this is the contellation iteration, copy the community map into the star list's constellation data
        if(i + 1 == constellation_iterations):
            for i, star in enumerate(star_data):
                star['constellation'] = community_map[i]
                
        #if this is the region iteration, copy the community map into the star list's region data
        if(i + 1 == region_iterations):
            for i, star in enumerate(star_data):
                star['region'] = community_map[i]
        

#given a graph, start each vertex in its own community, and merge communities to maximize modularity
def create_communities(edge_map):
    
    #compute the degree sum of this graph, times the weight of each edge
    degree_sum = float(sum(sum(weight for weight in item.itervalues()) for item in edge_map.itervalues()))
    
    #create a map from vertices to communities - start every vertex in its own community
    vertex_to_community = {key: key for key in edge_map.iterkeys()}
    
    #create a corresponding map from communities to vertices
    community_to_vertices = {key: {key} for key in edge_map.iterkeys()}
    
    #compute and store the modularity of each community
    modularity_map = {key: compute_modularity(community_to_vertices[key], edge_map, degree_sum) for key in edge_map.iterkeys()}
    
    #create an open set of all vertices
    open_set = {key for key in edge_map.iterkeys()}
    
    #while there are still vertices to look at
    while(len(open_set) > 0):
        v = open_set.pop()
        vc = vertex_to_community[v]
        
        positive_changes = []
        
        #look at each neighbor of v
        for n, edge_weight in edge_map[v].iteritems():
            nc = vertex_to_community[n]
            
            #if they are not in the same community
            if(vc != nc):
                
                #get the current modularity for comparison
                current_modularity = modularity_map[vc] + modularity_map[nc]
                
                #hypothetically move v into n's community, and compute the change in modularity
                vc_copy = set(community_to_vertices[vc])
                nc_copy = set(community_to_vertices[nc])
                
                vc_copy.remove(v)
                nc_copy.add(v)
                
                vc_modularity = compute_modularity(vc_copy, edge_map, degree_sum)
                nc_modularity = compute_modularity(nc_copy, edge_map, degree_sum)
                
                new_modularity = vc_modularity + nc_modularity
                
                #if this improves the modularity, record it
                modularity_delta = new_modularity - current_modularity
                
                if(modularity_delta > 0):
                    
                    #pack the data in a tuple to use when applying the change if needed
                    #needed information: delta, the neighbor community, and the "new" modularities for the current and neighbor community
                    packed_data = (modularity_delta, nc, vc_modularity, nc_modularity)
                    positive_changes.append(packed_data)
            
        
        #if there were any positive changes, take the one weith the highest delta and apply it
        if(len(positive_changes) > 0):
            delta, nc, new_vc_modularity, new_nc_modularity = max(positive_changes)
            
            #apply this change            
            vertex_to_community[v] = nc
            community_to_vertices[vc].remove(v)
            community_to_vertices[nc].add(v)
            
            #record the new modularity values
            modularity_map[vc] = new_vc_modularity
            modularity_map[nc] = new_nc_modularity
            
            #add all neighbors to the open set, if they're not a part of the new community
            for n, edge_weight in edge_map[v].iteritems():
                neighbor_community = vertex_to_community[n]
                
                if(nc != neighbor_community):
                    open_set.add(n)
                    
    #return the mapping from vertex to community
    return vertex_to_community
    
    
    
def compute_modularity(community_vertices, edge_map, degree_sum):
    
    #the modularity of this community is the fraction of edges with both ends inside the community, minus (the fraction of all edges that have at least one end inside this community)^2
    
    in_weight_sum = 0
    out_weight_sum = 0
    
    #loop through every 
    for v in community_vertices:
        
        #loop through v's neighbors
        for n, edge_weight in edge_map[v].iteritems():
            
            if(n in community_vertices):
                in_weight_sum += edge_weight
                out_weight_sum += edge_weight
            else:
                out_weight_sum += 2*edge_weight
                
    in_weight_sum /= degree_sum
    out_weight_sum /= degree_sum
    
    return in_weight_sum - (out_weight_sum * out_weight_sum)
    
    
    