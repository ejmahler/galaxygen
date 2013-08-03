
import argparse
import datetime
import json


import serialize

def main(options):
    import generator, printer, regions, centrality
    
    print "Generating galaxy..."
    star_array, edge_data = generator.generate_galaxy(
        num_stars=6000, 
        galaxy_radius=2000, 
        
        spiral_arm_count=6, 
        spiral_tightness=.5, 
        
        disk_height=50, 
        bulge_height=150
        )
    
    print "Computing regions..."
    regions.compute_regions(star_array, edge_data)
    
    serialize.save(star_array, edge_data, options.filename)
    
    print "Rendering..."
    printer.print_galaxy(star_array, edge_data)
    
    
    
def run_layout(options):
    import layout
    
    star_array, edge_data = serialize.load(options.filename)
    
    print "Running layout..."
    layout.forced_directed_layout(star_array, edge_data, iterations=options.iterations)
    
    serialize.save(star_array, edge_data, options.filename)
    
    
    

def run_render(options):
    import printer
    
    star_array, edge_data = serialize.load(options.filename)
    
    print "Rendering..."
    printer.print_galaxy(star_array, edge_data, edge=options.edge or False, image_size = options.size, color_type=options.color)
    
    
def run_regions(options):
    import regions
    import printer
    
    star_array, edge_data = serialize.load(options.filename)
    
    print "Computing regions..."
    regions.compute_regions(star_array, edge_data)
    
    serialize.save(star_array, edge_data, options.filename)
    
    print "Rendering..."
    printer.print_galaxy(star_array, edge_data)
    

def run_centrality(options):
    import centrality
    import printer
    
    star_array, edge_data = serialize.load(options.filename)
    
    print "Computing centrality..."
    centrality.compute_centrality(star_array, edge_data)
    
    serialize.save(star_array, edge_data, options.filename)
    
    print "Rendering..."
    printer.print_galaxy(star_array, edge_data)
    
    
def run_json(options):
    star_array, edge_data = serialize.load(options.filename)
    
    print "Writing json..."
    serialize.save_json(star_array, edge_data, options.output)
    

if(__name__ == '__main__'):
    parser = argparse.ArgumentParser('Functions for randomly generating a galaxy similar to the one in EVE Online')
    parser.add_argument('-f','--filename', help="Pickle file to load and save star data to and from", type=str, default=serialize.default_pickle_filename)
    
    subparsers = parser.add_subparsers(title="Subcommands")
    
    main_parser = subparsers.add_parser('main', help='Generates a new galaxy, renders it, and serializes it')
    main_parser.set_defaults(func=main)
    
    layout_parser = subparsers.add_parser('layout', help='Takes an existing star data set and runs iterations of force layout on them. Can be run on pypy, unlike the rest of the galaxy generator modules')
    layout_parser.add_argument('-i','--iterations', help="Number of iterations to run", type=int, default=1)
    layout_parser.set_defaults(func=run_layout)
    
    render_parser = subparsers.add_parser('render', help='Takes an existing star data set and generates an image for it')
    render_parser.add_argument('-e','--edge', help="Print the galaxy edge-on instead of top-down", action='store_true', default=False)
    render_parser.add_argument('-c','--color', help="Chooses which measure to use to color each star", type=str, default='region',choices=['security','region','betweenness'])
    render_parser.add_argument('-s','--size', help="Width and height of the resulting image, in pixels", type=int, default=3200)
    render_parser.set_defaults(func=run_render)
    
    region_parser = subparsers.add_parser('region', help='Takes an existing star data set and computes regions for it')
    region_parser.set_defaults(func=run_regions)
    
    centrality_parser = subparsers.add_parser('centrality', help='Takes an existing star data set and computes centrality data for it')
    centrality_parser.set_defaults(func=run_centrality)
    
    json_parser = subparsers.add_parser('tojson', help='Takes an existing star data set and converts it to json format')
    json_parser.add_argument('-o','--output', help="The file to write the json to", type=str, default=serialize.default_json_filename)
    json_parser.set_defaults(func=run_json)
    
    args = parser.parse_args()
    
    start = datetime.datetime.now()
    args.func(args)
    end = datetime.datetime.now()
    
    print "Completed in %s"%str(end - start)
